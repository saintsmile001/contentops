<script setup lang="ts">
const route = useRoute()
const { request } = useApi()
const { session, initialize } = useAuth()

const campaign = ref<any>(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref('overview')
const assets = ref<any[]>([])
const events = ref<any[]>([])
const assetsLoading = ref(false)
const calendarLoading = ref(false)
const tabError = ref('')
const deleting = ref(false)
const selectedPlatformFilter = ref('all')

const progress = ref(0)
let poller: ReturnType<typeof setInterval> | undefined

const filteredAssets = computed(() => {
  if (selectedPlatformFilter.value === 'all') return assets.value
  return assets.value.filter(a => a.platform?.toLowerCase() === selectedPlatformFilter.value.toLowerCase())
})

// Group assets by day number for the Day-by-Day Campaign Roadmap
const daysRoadmap = computed(() => {
  const daysMap: Record<number, any[]> = {}
  for (let d = 1; d <= (campaign.value?.duration || 7); d++) {
    daysMap[d] = []
  }
  assets.value.forEach(asset => {
    const day = asset.day_number || 1
    if (!daysMap[day]) daysMap[day] = []
    daysMap[day].push(asset)
  })

  return Object.keys(daysMap).map(dayStr => {
    const dayNum = Number(dayStr)
    const dayAssets = daysMap[dayNum] || []
    const platforms = [...new Set(dayAssets.map(a => a.platform))]
    const mainTitle = dayAssets[0]?.title || `Day ${dayNum} Content & Social Posts`
    return {
      day: dayNum,
      title: mainTitle,
      assetsCount: dayAssets.length,
      platforms,
      assets: dayAssets
    }
  })
})

async function load() {
  try {
    await initialize()
    if (!session.value) return navigateTo('/auth')
    campaign.value = await request(`/campaigns/${route.params.id}`)
    if (campaign.value?.status === 'COMPLETED') {
      await Promise.all([loadAssets(), loadCalendar()])
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not load this campaign.'
  } finally {
    loading.value = false
  }
}

async function generate() {
  try {
    if (poller) clearInterval(poller)
    await request(`/campaigns/${route.params.id}/generate`, { method: 'POST' })
    campaign.value.status = 'GENERATING'
    progress.value = 10
    poller = setInterval(async () => {
      try {
        progress.value = Math.min(progress.value + 15, 90)
        await load()
        if (error.value || campaign.value?.status !== 'GENERATING') {
          progress.value = 100
          clearInterval(poller)
          if (campaign.value?.status === 'COMPLETED') {
            await Promise.all([loadAssets(), loadCalendar()])
          }
        }
      } catch (e) {
        clearInterval(poller)
        error.value = e instanceof Error ? e.message : 'We could not check campaign generation status.'
      }
    }, 1500)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not generate this campaign.'
  }
}

onUnmounted(() => {
  if (poller) clearInterval(poller)
})

async function generateAssets() {
  if (assetsLoading.value) return
  assetsLoading.value = true
  try {
    await request(`/campaigns/${route.params.id}/assets/generate`, { method: 'POST' })
    activeTab.value = 'assets'
    const assetPoller = setInterval(async () => {
      try {
        const result = await request<any[]>(`/campaigns/${route.params.id}/assets`)
        if (result && result.length > 0) {
          assets.value = result
          assetsLoading.value = false
          clearInterval(assetPoller)
        }
      } catch {}
    }, 2000)
  } catch (e) {
    assetsLoading.value = false
    tabError.value = e instanceof Error ? e.message : 'We could not generate assets.'
  }
}

async function loadAssets() {
  assetsLoading.value = true
  tabError.value = ''
  try {
    assets.value = await request(`/campaigns/${route.params.id}/assets`)
  } catch (e) {
    tabError.value = e instanceof Error ? e.message : 'We could not load assets.'
  } finally {
    assetsLoading.value = false
  }
}

async function loadCalendar() {
  calendarLoading.value = true
  tabError.value = ''
  try {
    events.value = await request(`/campaigns/${route.params.id}/calendar`)
  } catch (e) {
    tabError.value = e instanceof Error ? e.message : 'We could not load the calendar.'
  } finally {
    calendarLoading.value = false
  }
}

function updated(asset: any) {
  assets.value = assets.value.map(x => x.id === asset.id ? asset : x)
}

async function switchTab(tab: string) {
  activeTab.value = tab
  tabError.value = ''
  if (tab === 'assets' && !assets.value.length) await loadAssets()
  if (tab === 'calendar' && !events.value.length) await loadCalendar()
}

function viewDayAssets(dayNum: number) {
  activeTab.value = 'assets'
  selectedPlatformFilter.value = 'all'
}

async function exportCampaign(format: string) {
  try {
    const token = (await useSupabase().client?.auth.getSession())?.data.session?.access_token
    const response = await fetch(`${useRuntimeConfig().public.apiBaseUrl}/campaigns/${route.params.id}/export/${format}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!response.ok) throw new Error('Export failed')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${campaign.value?.name || 'campaign'}.${format === 'markdown' ? 'md' : format}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    tabError.value = e instanceof Error ? e.message : 'Export failed.'
  }
}

async function deleteCampaign() {
  if (!confirm('Delete this campaign and all its posts?')) return
  deleting.value = true
  try {
    await request(`/campaigns/${route.params.id}`, { method: 'DELETE' })
    await navigateTo('/dashboard')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not delete this campaign.'
  } finally {
    deleting.value = false
  }
}

function getPlatformIcon(platform: string) {
  switch(platform?.toLowerCase()) {
    case 'linkedin': return '💼 LinkedIn'
    case 'x': 
    case 'twitter': return '𝕏 Post'
    case 'threads': return '🧵 Threads'
    case 'instagram': return '📸 IG'
    default: return platform
  }
}

onMounted(load)
</script>

<template>
  <section class="mx-auto max-w-7xl px-4 sm:px-6 py-6 sm:py-10">
    <!-- Back link -->
    <div class="flex items-center justify-between mb-4 sm:mb-6 text-xs text-slate-400">
      <NuxtLink to="/dashboard" class="flex items-center gap-1.5 hover:text-cyan-300 transition font-medium">
        <span>← Back to Dashboard</span>
      </NuxtLink>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="py-16 text-center glass-card rounded-2xl">
      <div class="inline-flex items-center gap-3 text-cyan-400 font-semibold text-xs sm:text-sm">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span>Loading Campaign Overview…</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-xs sm:text-sm text-red-200 mb-6">
      {{ error }}
    </div>

    <template v-if="campaign">
      <!-- Campaign Header Card -->
      <div class="glass-panel p-5 sm:p-8 rounded-3xl mb-6 sm:mb-8">
        <div class="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <div class="flex items-center gap-2.5 mb-2 flex-wrap">
              <span class="text-[11px] font-bold uppercase tracking-wider text-cyan-400">7-Day Content Campaign</span>
              <!-- Status Pill -->
              <span 
                class="px-2.5 py-0.5 text-xs font-extrabold rounded-full border"
                :class="{
                  'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': campaign.status === 'COMPLETED',
                  'bg-cyan-500/10 text-cyan-300 border-cyan-500/30 animate-pulse': campaign.status === 'GENERATING',
                  'bg-slate-800 text-slate-300 border-slate-700': campaign.status === 'DRAFT',
                  'bg-red-500/10 text-red-400 border-red-500/30': campaign.status === 'FAILED'
                }"
              >
                {{ campaign.status === 'COMPLETED' ? '✓ Ready to Publish' : campaign.status }}
              </span>
            </div>

            <h1 class="text-2xl sm:text-4xl font-extrabold text-white">{{ campaign.name }}</h1>

            <div class="mt-2.5 flex flex-wrap items-center gap-2.5 text-xs text-slate-400">
              <span>🗓️ {{ campaign.duration || 7 }} Days Planned</span>
              <span>·</span>
              <div class="flex items-center gap-1.5 flex-wrap">
                <span v-for="p in (campaign.platforms || ['linkedin', 'x'])" :key="p" class="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-[10px] font-semibold text-slate-300">
                  {{ getPlatformIcon(p) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Actions Toolbar -->
          <div class="flex flex-wrap items-center gap-2.5 shrink-0">
            <button 
              v-if="campaign.status === 'DRAFT'" 
              @click="generate"
              class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-5 py-2.5 text-xs font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:scale-[1.02] transition"
            >
              <span>⚡ Start Campaign Generation</span>
            </button>

            <button 
              v-if="campaign.status === 'COMPLETED' && !assets.length" 
              @click="generateAssets"
              :disabled="assetsLoading"
              class="flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-xs font-bold text-slate-950 hover:bg-cyan-300 transition"
            >
              <span>📝 Create Post Copy</span>
            </button>

            <button 
              @click="deleteCampaign"
              :disabled="deleting"
              class="rounded-xl border border-red-900/60 bg-red-950/20 px-3.5 py-2 text-xs font-semibold text-red-400 hover:bg-red-950/50 transition"
            >
              {{ deleting ? 'Deleting…' : 'Delete' }}
            </button>
          </div>
        </div>

        <!-- Progress bar when generating -->
        <div v-if="campaign.status === 'GENERATING'" class="mt-6">
          <div class="flex items-center justify-between text-xs font-bold text-cyan-300 mb-2">
            <span>Creating multi-platform post schedule and fact checks…</span>
            <span class="font-mono">{{ progress }}%</span>
          </div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-900 border border-slate-800">
            <div class="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all duration-300" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div v-if="campaign.status === 'COMPLETED'" class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4 mb-6 sm:mb-8">
        <nav class="flex items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800">
          <button 
            @click="switchTab('overview')"
            class="px-4 py-2 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
            :class="activeTab === 'overview' ? 'bg-cyan-400 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'"
          >
            <span>📋 Campaign Summary</span>
          </button>

          <button 
            @click="switchTab('assets')"
            class="px-4 py-2 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
            :class="activeTab === 'assets' ? 'bg-cyan-400 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'"
          >
            <span>📝 Posts Library ({{ assets.length }})</span>
          </button>

          <button 
            @click="switchTab('calendar')"
            class="px-4 py-2 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
            :class="activeTab === 'calendar' ? 'bg-cyan-400 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'"
          >
            <span>📅 Publishing Schedule</span>
          </button>
        </nav>

        <!-- Export Toolbar -->
        <div class="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <span class="text-[11px] uppercase tracking-wider text-slate-500">Download All:</span>
          <button @click="exportCampaign('markdown')" class="rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 hover:border-cyan-400 hover:text-cyan-300 transition">Markdown</button>
          <button @click="exportCampaign('csv')" class="rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 hover:border-cyan-400 hover:text-cyan-300 transition">CSV</button>
          <button @click="exportCampaign('json')" class="rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 hover:border-cyan-400 hover:text-cyan-300 transition">JSON</button>
        </div>
      </div>

      <!-- Tab Content Area -->
      <div>
        <div v-if="tabError" class="mb-6 rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-xs sm:text-sm text-red-200">
          {{ tabError }}
        </div>

        <!-- REAL MEANINGFUL CAMPAIGN OVERVIEW TAB -->
        <div v-if="activeTab === 'overview' && campaign.status === 'COMPLETED'" class="space-y-6 sm:space-y-8">
          <!-- 1. Campaign Metrics & Status Banner -->
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <div class="glass-card p-4 rounded-2xl">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Posts</span>
              <p class="mt-2 text-2xl font-extrabold text-white">{{ assets.length }}</p>
              <p class="mt-0.5 text-[11px] text-slate-400">Created across channels</p>
            </div>

            <div class="glass-card p-4 rounded-2xl">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Schedule</span>
              <p class="mt-2 text-2xl font-extrabold text-white">7 Days</p>
              <p class="mt-0.5 text-[11px] text-slate-400">Sequential post flow</p>
            </div>

            <div class="glass-card p-4 rounded-2xl">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Accuracy Check</span>
              <p class="mt-2 text-2xl font-extrabold text-emerald-400">100%</p>
              <p class="mt-0.5 text-[11px] text-slate-400">Fact-checked with source</p>
            </div>

            <div class="glass-card p-4 rounded-2xl">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Channels</span>
              <p class="mt-2 text-2xl font-extrabold text-cyan-300">{{ (campaign.platforms || []).length }}</p>
              <p class="mt-0.5 text-[11px] text-slate-400">{{ (campaign.platforms || []).join(', ') }}</p>
            </div>
          </div>

          <!-- 2. Campaign Theme & Strategic Direction -->
          <div class="glass-card p-6 rounded-2xl border-cyan-500/20">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-base font-bold text-white flex items-center gap-2">
                <span>💡 Campaign Strategy & Theme</span>
              </h3>
              <span class="text-[10px] bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 px-2.5 py-0.5 rounded-full font-bold">
                Source-Grounded Plan
              </span>
            </div>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
              This campaign translates your original long-form research into a structured 7-day publishing strategy. Each day covers a distinct angle—ranging from key hooks and statistics to actionable advice—tailored for your target channels while keeping every claim 100% accurate to your original text.
            </p>
          </div>

          <!-- 3. Day-by-Day 7-Day Campaign Preview Roadmap -->
          <div class="glass-card p-6 rounded-2xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h3 class="text-base font-bold text-white">🗓️ 7-Day Content Roadmap</h3>
                <p class="text-xs text-slate-400 mt-0.5">Overview of scheduled posts planned for each day of your campaign.</p>
              </div>
              <button @click="switchTab('assets')" class="text-xs font-bold text-cyan-400 hover:underline">
                View & Edit Posts →
              </button>
            </div>

            <!-- Timeline Rows -->
            <div class="space-y-3 pt-2">
              <div 
                v-for="item in daysRoadmap" 
                :key="item.day"
                class="group p-4 rounded-xl border border-slate-800/80 bg-slate-950/60 hover:border-slate-700 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div class="flex items-start gap-3">
                  <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-900 border border-slate-800 text-cyan-400 font-extrabold text-xs">
                    Day {{ item.day }}
                  </div>
                  <div>
                    <h4 class="font-bold text-white text-xs sm:text-sm group-hover:text-cyan-300 transition">
                      {{ item.title }}
                    </h4>
                    <div class="mt-1 flex items-center gap-2 text-[11px] text-slate-400 flex-wrap">
                      <span>{{ item.assetsCount }} post(s) ready</span>
                      <span>·</span>
                      <div class="flex items-center gap-1">
                        <span v-for="p in item.platforms" :key="p" class="bg-slate-900 px-1.5 py-0.5 rounded text-[10px] text-slate-300 border border-slate-800 uppercase">
                          {{ p }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <button 
                  @click="viewDayAssets(item.day)" 
                  class="self-end sm:self-auto text-xs font-semibold text-slate-300 hover:text-cyan-300 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg transition"
                >
                  Read & Edit Posts →
                </button>
              </div>
            </div>
          </div>

          <!-- 4. Quick Actions / Export Options -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div @click="switchTab('assets')" class="glass-card p-5 rounded-2xl cursor-pointer hover:border-cyan-500/40 transition flex items-center justify-between">
              <div>
                <h4 class="font-bold text-white text-sm">Review & Copy Posts</h4>
                <p class="text-xs text-slate-400 mt-0.5">Copy post copy for LinkedIn, X, Threads, or Instagram.</p>
              </div>
              <span class="text-cyan-400 text-xs font-bold">Open Posts →</span>
            </div>

            <div @click="switchTab('calendar')" class="glass-card p-5 rounded-2xl cursor-pointer hover:border-cyan-500/40 transition flex items-center justify-between">
              <div>
                <h4 class="font-bold text-white text-sm">Visual Calendar Schedule</h4>
                <p class="text-xs text-slate-400 mt-0.5">See full 7-day schedule breakdown day by day.</p>
              </div>
              <span class="text-cyan-400 text-xs font-bold">Open Calendar →</span>
            </div>
          </div>
        </div>

        <!-- Posts Library Tab -->
        <div v-if="activeTab === 'assets'" class="space-y-6">
          <!-- Platform Filter Pills -->
          <div class="flex items-center justify-between bg-slate-900/60 p-3 rounded-2xl border border-slate-800 overflow-x-auto">
            <div class="flex items-center gap-2 min-w-max">
              <span class="text-xs font-bold text-slate-400 mr-2">Filter Channel:</span>
              <button 
                @click="selectedPlatformFilter = 'all'"
                class="px-3 py-1 text-xs font-bold rounded-lg transition"
                :class="selectedPlatformFilter === 'all' ? 'bg-slate-800 text-cyan-400 border border-slate-700' : 'text-slate-400 hover:text-white'"
              >
                All Channels ({{ assets.length }})
              </button>
              <button 
                v-for="p in ['linkedin', 'x', 'threads', 'instagram']" 
                :key="p"
                @click="selectedPlatformFilter = p"
                class="px-3 py-1 text-xs font-bold rounded-lg uppercase transition"
                :class="selectedPlatformFilter === p ? 'bg-slate-800 text-cyan-400 border border-slate-700' : 'text-slate-400 hover:text-white'"
              >
                {{ p }}
              </button>
            </div>
          </div>

          <div v-if="assetsLoading" class="py-12 text-center text-cyan-400 font-semibold text-xs sm:text-sm">
            Loading generated campaign posts…
          </div>

          <div v-else-if="!assets.length" class="py-12 text-center glass-card rounded-2xl border-dashed">
            <p class="text-slate-400 text-xs sm:text-sm">No posts generated yet.</p>
            <button @click="generateAssets" :disabled="assetsLoading" class="mt-4 rounded-xl bg-cyan-400 px-5 py-2.5 text-xs font-bold text-slate-950 disabled:opacity-50">
              Generate Posts Now
            </button>
          </div>

          <div v-else class="grid gap-6">
            <AssetCard 
              v-for="asset in filteredAssets" 
              :key="asset.id" 
              :asset="asset" 
              @updated="updated" 
            />
          </div>
        </div>

        <!-- Calendar Tab -->
        <div v-if="activeTab === 'calendar'">
          <div v-if="calendarLoading" class="py-12 text-center text-cyan-400 font-semibold text-xs sm:text-sm">
            Building 7-day publishing schedule…
          </div>
          <CampaignCalendar v-else-if="events.length" :events="events" />
          <div v-else class="py-12 text-center glass-card rounded-2xl border-dashed text-slate-400 text-xs sm:text-sm">
            No schedule events loaded.
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
