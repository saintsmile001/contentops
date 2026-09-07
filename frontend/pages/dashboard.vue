<script setup lang="ts">
const { request } = useApi()
const { session, initialize } = useAuth()
const loading = ref(true)
const error = ref('')
const sources = ref<any[]>([])
const campaigns = ref<any[]>([])
const searchQuery = ref('')
const activeTab = ref('all')

const complete = computed(() => campaigns.value.filter(item => item.status === 'COMPLETED').length)
const generating = computed(() => campaigns.value.filter(item => item.status === 'GENERATING').length)

const filteredCampaigns = computed(() => {
  if (!searchQuery.value.trim()) return campaigns.value
  const q = searchQuery.value.toLowerCase()
  return campaigns.value.filter(c => c.name?.toLowerCase().includes(q) || c.status?.toLowerCase().includes(q))
})

const filteredSources = computed(() => {
  if (!searchQuery.value.trim()) return sources.value
  const q = searchQuery.value.toLowerCase()
  return sources.value.filter(s => s.title?.toLowerCase().includes(q) || s.content_type?.toLowerCase().includes(q))
})

onMounted(async () => {
  try {
    await initialize()
    if (!session.value) return navigateTo('/auth')
    ;[sources.value, campaigns.value] = await Promise.all([
      request('/sources'), 
      request('/campaigns')
    ])
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : 'We could not load your workspace.'
  } finally { 
    loading.value = false 
  }
})

async function deleteSource(id: string) {
  if (!confirm('Delete this source and its Content DNA?')) return
  try {
    await request(`/sources/${id}`, { method: 'DELETE' })
    sources.value = sources.value.filter(s => s.id !== id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not delete this source.'
  }
}

async function deleteCampaign(id: string) {
  if (!confirm('Delete this campaign and all its assets?')) return
  try {
    await request(`/campaigns/${id}`, { method: 'DELETE' })
    campaigns.value = campaigns.value.filter(c => c.id !== id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not delete this campaign.'
  }
}

function getPlatformIcon(platform: string) {
  switch(platform.toLowerCase()) {
    case 'linkedin': return '💼 LinkedIn'
    case 'x': 
    case 'twitter': return '𝕏 Post'
    case 'threads': return '🧵 Threads'
    case 'instagram': return '📸 IG'
    default: return platform
  }
}
</script>

<template>
  <section class="mx-auto max-w-7xl px-4 sm:px-6 py-6 sm:py-10">
    <!-- Header Banner -->
    <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-6 sm:pb-8">
      <div>
        <div class="flex items-center gap-2 text-[11px] sm:text-xs font-bold uppercase tracking-widest text-cyan-400">
          <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
          <span>Content Workspace</span>
        </div>
        <h1 class="mt-2 text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
          Dashboard
        </h1>
        <p class="mt-1.5 text-xs sm:text-sm text-slate-400 max-w-2xl">
          Organize your source materials and manage your 7-day content plans.
        </p>
      </div>

      <!-- Quick Action Buttons (Mobile Optimized) -->
      <div class="grid grid-cols-2 sm:flex sm:items-center gap-2.5 sm:gap-3 w-full sm:w-auto">
        <NuxtLink 
          to="/create" 
          class="flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-200 hover:border-slate-500 hover:bg-slate-800 active:scale-95 transition"
        >
          <svg class="w-4 h-4 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          <span>Add Source</span>
        </NuxtLink>
        
        <NuxtLink 
          to="/campaigns/create" 
          class="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-4 py-2.5 text-xs sm:text-sm font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 active:scale-95 transition"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          <span>New Campaign</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="mt-6 rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-xs sm:text-sm text-red-200 flex items-center justify-between">
      <span>{{ error }}</span>
      <button @click="error = ''" class="text-xs text-red-400 hover:text-red-300 font-bold p-1">Dismiss</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-16 text-center">
      <div class="inline-flex items-center gap-3 rounded-full bg-slate-900 px-5 py-2.5 border border-slate-800 text-cyan-400 font-semibold text-xs sm:text-sm">
        <svg class="w-4 h-4 sm:w-5 sm:h-5 animate-spin text-cyan-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span>Loading workspace data…</span>
      </div>
    </div>

    <template v-else>
      <!-- Stats Metric Grid (2x2 on Mobile, 4x1 on Desktop) -->
      <div class="mt-6 sm:mt-8 grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <!-- Stat Card 1 -->
        <div class="glass-card p-4 sm:p-5 rounded-2xl relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-400">Source Library</span>
            <div class="h-7 w-7 sm:h-8 sm:w-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 text-xs sm:text-sm">
              📄
            </div>
          </div>
          <p class="mt-2 sm:mt-3 text-2xl sm:text-3xl font-extrabold text-white">{{ sources.length }}</p>
          <p class="mt-0.5 text-[10px] sm:text-xs text-slate-400 truncate">Indexed documents</p>
        </div>

        <!-- Stat Card 2 -->
        <div class="glass-card p-4 sm:p-5 rounded-2xl relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-400">Total Campaigns</span>
            <div class="h-7 w-7 sm:h-8 sm:w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 text-xs sm:text-sm">
              🚀
            </div>
          </div>
          <p class="mt-2 sm:mt-3 text-2xl sm:text-3xl font-extrabold text-white">{{ campaigns.length }}</p>
          <p class="mt-0.5 text-[10px] sm:text-xs text-slate-400 truncate">7-day content plans</p>
        </div>

        <!-- Stat Card 3 -->
        <div class="glass-card p-4 sm:p-5 rounded-2xl relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-400">Ready & Grounded</span>
            <div class="h-7 w-7 sm:h-8 sm:w-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-xs sm:text-sm">
              ✅
            </div>
          </div>
          <p class="mt-2 sm:mt-3 text-2xl sm:text-3xl font-extrabold text-emerald-400">{{ complete }}</p>
          <p class="mt-0.5 text-[10px] sm:text-xs text-slate-400 truncate">Generated & QA audited</p>
        </div>

        <!-- Stat Card 4 -->
        <div class="glass-card p-4 sm:p-5 rounded-2xl relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-400">In Progress</span>
            <div class="h-7 w-7 sm:h-8 sm:w-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xs sm:text-sm">
              ⚡
            </div>
          </div>
          <p class="mt-2 sm:mt-3 text-2xl sm:text-3xl font-extrabold text-cyan-300">{{ generating }}</p>
          <p class="mt-0.5 text-[10px] sm:text-xs text-slate-400 truncate">Generating now</p>
        </div>
      </div>

      <!-- Controls & Search Bar (Mobile Responsive Filter Tabs & Search) -->
      <div class="mt-8 sm:mt-10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4 bg-slate-900/60 p-2.5 sm:p-3 rounded-2xl border border-slate-800/80">
        <!-- Tabs Bar -->
        <div class="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
          <button 
            @click="activeTab = 'all'"
            class="px-3.5 py-1.5 text-xs font-bold rounded-xl whitespace-nowrap transition"
            :class="activeTab === 'all' ? 'bg-slate-800 text-white border border-slate-700 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
          >
            All Items
          </button>
          <button 
            v-if="campaigns.length > 0"
            @click="activeTab = 'campaigns'"
            class="px-3.5 py-1.5 text-xs font-bold rounded-xl whitespace-nowrap transition"
            :class="activeTab === 'campaigns' ? 'bg-slate-800 text-white border border-slate-700 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
          >
            Campaigns ({{ campaigns.length }})
          </button>
          <button 
            @click="activeTab = 'sources'"
            class="px-3.5 py-1.5 text-xs font-bold rounded-xl whitespace-nowrap transition"
            :class="activeTab === 'sources' ? 'bg-slate-800 text-white border border-slate-700 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
          >
            Sources ({{ sources.length }})
          </button>
        </div>

        <!-- Search Input -->
        <div class="relative w-full sm:w-72">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search workspace…" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3.5 py-2 pl-9 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none transition"
          />
          <svg class="w-4 h-4 absolute left-3 top-2.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
      </div>

      <!-- Recent Campaigns Section (ONLY SHOWN IF CAMPAIGNS EXIST) -->
      <section v-if="campaigns.length > 0 && (activeTab === 'all' || activeTab === 'campaigns')" class="mt-8">
        <div class="glass-card p-4 sm:p-6 rounded-2xl">
          <div class="flex items-center justify-between mb-4 sm:mb-6">
            <div>
              <h2 class="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                <span>Recent Campaigns</span>
                <span class="text-xs bg-slate-800 border border-slate-700 text-cyan-400 px-2.5 py-0.5 rounded-full font-mono">{{ campaigns.length }}</span>
              </h2>
              <p class="text-xs text-slate-400 mt-0.5 hidden sm:block">Multi-platform 7-day content plans grounded in your Content DNA.</p>
            </div>

            <NuxtLink to="/campaigns/create" class="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition">
              <span>+ New Campaign</span>
            </NuxtLink>
          </div>

          <!-- Campaigns List -->
          <div v-if="filteredCampaigns.length" class="divide-y divide-slate-800/80">
            <div 
              v-for="campaign in filteredCampaigns" 
              :key="campaign.id" 
              class="group py-3.5 sm:py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 transition hover:bg-slate-800/20 px-2 rounded-xl"
            >
              <div class="flex-1 min-w-0">
                <NuxtLink :to="`/campaigns/${campaign.id}`" class="block">
                  <div class="flex items-center gap-2.5 flex-wrap">
                    <h3 class="font-bold text-white group-hover:text-cyan-300 transition text-sm sm:text-base truncate max-w-full sm:max-w-md">{{ campaign.name }}</h3>
                    <!-- Status Pill -->
                    <span 
                      class="px-2 py-0.5 text-[10px] sm:text-[11px] font-bold rounded-full border shadow-xs"
                      :class="{
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': campaign.status === 'COMPLETED',
                        'bg-cyan-500/10 text-cyan-300 border-cyan-500/30 animate-pulse': campaign.status === 'GENERATING',
                        'bg-slate-800 text-slate-400 border-slate-700': campaign.status === 'DRAFT'
                      }"
                    >
                      {{ campaign.status }}
                    </span>
                  </div>

                  <div class="mt-1.5 flex flex-wrap items-center gap-2 text-[11px] sm:text-xs text-slate-400">
                    <span>🗓️ {{ campaign.duration || 7 }}-day plan</span>
                    <span>·</span>
                    <div class="flex items-center gap-1 flex-wrap">
                      <span v-for="p in (campaign.platforms || ['linkedin', 'x'])" :key="p" class="bg-slate-800 px-1.5 py-0.5 rounded text-[10px] font-semibold text-slate-300 border border-slate-700">
                        {{ getPlatformIcon(p) }}
                      </span>
                    </div>
                  </div>
                </NuxtLink>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-2.5 shrink-0 self-end sm:self-auto pt-1 sm:pt-0">
                <NuxtLink :to="`/campaigns/${campaign.id}`" class="rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 transition">
                  Open Campaign →
                </NuxtLink>
                <button 
                  @click="deleteCampaign(campaign.id)"
                  class="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition"
                  title="Delete Campaign"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Source Library Section -->
      <section v-if="activeTab === 'all' || activeTab === 'sources'" class="mt-8">
        <div class="glass-card p-4 sm:p-6 rounded-2xl">
          <div class="flex items-center justify-between mb-4 sm:mb-6">
            <div>
              <h2 class="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                <span>Source Material Library</span>
                <span class="text-xs bg-slate-800 border border-slate-700 text-cyan-400 px-2.5 py-0.5 rounded-full font-mono">{{ sources.length }}</span>
              </h2>
              <p class="text-xs text-slate-400 mt-0.5 hidden sm:block">The evidence & original text grounding every generated campaign asset.</p>
            </div>

            <NuxtLink to="/create" class="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition">
              <span>+ Add Source</span>
            </NuxtLink>
          </div>

          <div v-if="filteredSources.length" class="grid gap-3.5 sm:gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <div 
              v-for="source in filteredSources" 
              :key="source.id" 
              class="group relative rounded-xl border border-slate-800 bg-slate-950/60 p-4 sm:p-5 hover:border-cyan-500/40 transition flex flex-col justify-between"
            >
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[10px] font-bold uppercase tracking-wider bg-slate-800 border border-slate-700 text-cyan-400 px-2 py-0.5 rounded">
                    {{ source.content_type || 'TEXT' }}
                  </span>
                  <span class="text-xs text-slate-500 font-mono">{{ source.word_count || 0 }} words</span>
                </div>

                <NuxtLink :to="`/sources/${source.id}/dna`" class="block">
                  <h3 class="font-bold text-white group-hover:text-cyan-300 transition text-sm leading-snug line-clamp-2">
                    {{ source.title }}
                  </h3>
                </NuxtLink>
              </div>

              <div class="mt-4 pt-3.5 border-t border-slate-800/80 flex items-center justify-between">
                <NuxtLink :to="`/sources/${source.id}/dna`" class="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                  <span>View Content DNA</span>
                  <span>→</span>
                </NuxtLink>

                <button 
                  @click="deleteSource(source.id)" 
                  class="text-xs text-slate-500 hover:text-red-400 font-medium transition"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>

          <!-- Empty Sources State -->
          <div v-else class="py-10 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/40 px-4">
            <div class="h-10 w-10 sm:h-12 sm:w-12 rounded-full bg-slate-900 border border-slate-800 mx-auto flex items-center justify-center text-lg sm:text-xl mb-3">
              📄
            </div>
            <h4 class="font-bold text-white text-xs sm:text-sm">No source materials added yet</h4>
            <p class="text-[11px] sm:text-xs text-slate-400 max-w-sm mx-auto mt-1">Upload an article, PDF, whitepaper, or podcast transcript to begin.</p>
            <NuxtLink to="/create" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 text-xs font-bold text-slate-950 hover:bg-cyan-300 transition">
              <span>Add Your First Source</span>
            </NuxtLink>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>
