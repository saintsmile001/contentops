<script setup lang="ts">
const { request } = useApi()
const { session, initialize } = useAuth()
const route = useRoute()

const sources = ref<any[]>([])
const readySourceIds = ref<string[]>([])
const sourceId = ref('')
const name = ref('')
const platforms = ref(['linkedin', 'x', 'instagram'])
const loading = ref(true)
const saving = ref(false)
const analyzing = ref(false)
const error = ref('')

const platformOptions = [
  { id: 'linkedin', label: 'LinkedIn', icon: '💼', desc: 'Long-form professional posts & carousels' },
  { id: 'x', label: 'X (Twitter)', icon: '𝕏', desc: 'Punchy threads & short updates' },
  { id: 'instagram', label: 'Instagram', icon: '📸', desc: 'Visual captions & reel copy' },
  { id: 'threads', label: 'Threads', icon: '🧵', desc: 'Casual text conversations' }
]

const selectedReady = computed(() => readySourceIds.value.includes(sourceId.value))
const selectedSource = computed(() => sources.value.find(source => source.id === sourceId.value))

async function checkReadiness() {
  const checks = await Promise.all(sources.value.map(async source => {
    const status = await request<{ ready: boolean }>(`/sources/${source.id}/dna/status`)
    return status.ready ? source.id : null
  }))
  readySourceIds.value = checks.filter(Boolean) as string[]
}

onMounted(async () => {
  try {
    await initialize()
    if (!session.value) return navigateTo('/auth')
    sources.value = await request('/sources')
    const requestedSource = typeof route.query.source === 'string' ? route.query.source : ''
    sourceId.value = sources.value.some(source => source.id === requestedSource) ? requestedSource : (sources.value[0]?.id || '')
    await checkReadiness()
    if (selectedSource.value && !name.value) {
      name.value = `${selectedSource.value.title} Campaign`
    }
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not load your sources.' 
  } finally { 
    loading.value = false 
  }
})

watch(sourceId, (newId) => {
  const s = sources.value.find(item => item.id === newId)
  if (s && (!name.value || name.value.endsWith('Campaign'))) {
    name.value = `${s.title} Campaign`
  }
})

function togglePlatform(id: string) {
  if (platforms.value.includes(id)) {
    if (platforms.value.length > 1) {
      platforms.value = platforms.value.filter(p => p !== id)
    }
  } else {
    platforms.value.push(id)
  }
}

async function analyzeSelected() {
  if (!sourceId.value) return
  analyzing.value = true
  error.value = ''
  try {
    await request(`/sources/${sourceId.value}/dna`, { method: 'POST' })
    readySourceIds.value = [...new Set([...readySourceIds.value, sourceId.value])]
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not analyze this source.' 
  } finally { 
    analyzing.value = false 
  }
}

async function createCampaign() {
  if (!selectedReady.value) return
  saving.value = true
  error.value = ''
  try {
    const campaign = await request<any>('/campaigns', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify({ 
        source_id: sourceId.value, 
        name: name.value, 
        duration: 7, 
        platforms: platforms.value 
      }) 
    })
    await navigateTo(`/campaigns/${campaign.id}`)
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not create this campaign.' 
  } finally { 
    saving.value = false 
  }
}
</script>

<template>
  <section class="mx-auto max-w-3xl px-6 py-12">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-xs text-slate-400 mb-6">
      <NuxtLink to="/dashboard" class="hover:text-cyan-300">Dashboard</NuxtLink>
      <span>/</span>
      <span class="text-cyan-400 font-semibold">Step 3: Create 7-Day Campaign</span>
    </div>

    <!-- Header Panel -->
    <div class="glass-panel p-8 rounded-3xl mb-8">
      <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">
        <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
        <span>Multi-Channel Content Plan</span>
      </div>
      <h1 class="text-3xl font-extrabold text-white sm:text-4xl">Configure Campaign</h1>
      <p class="mt-2 text-sm text-slate-300">
        Generate a 7-day scheduled plan across selected platforms grounded in your Content DNA.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-12 text-center text-cyan-400 font-semibold text-sm">
      Checking source library readiness…
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="mb-6 rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-sm text-red-200">
      {{ error }}
    </div>

    <!-- No Sources State -->
    <div v-else-if="!sources.length" class="glass-card p-8 rounded-2xl text-center">
      <div class="h-12 w-12 rounded-full bg-slate-900 border border-slate-800 mx-auto flex items-center justify-center text-xl mb-3">
        📄
      </div>
      <h3 class="font-bold text-white text-base">No source material found</h3>
      <p class="text-xs text-slate-400 mt-1">Please add a source document or text paste first before creating a campaign.</p>
      <NuxtLink to="/create" class="mt-4 inline-block rounded-xl bg-cyan-400 px-5 py-2.5 text-xs font-bold text-slate-950">
        + Add Source Material
      </NuxtLink>
    </div>

    <!-- Campaign Form -->
    <form v-else class="space-y-6" @submit.prevent="createCampaign">
      <!-- Select Source Material -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Select Source Document
        </label>
        
        <select 
          v-model="sourceId" 
          class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none"
        >
          <option v-for="source in sources" :key="source.id" :value="source.id">
            {{ source.title }} {{ readySourceIds.includes(source.id) ? '✓ (DNA Ready)' : '⚠️ (Needs DNA Analysis)' }}
          </option>
        </select>

        <!-- Unanalyzed Source Notice -->
        <div v-if="!selectedReady" class="mt-4 rounded-xl border border-amber-500/30 bg-amber-950/20 p-4">
          <div class="flex items-center gap-2 text-xs font-bold text-amber-300">
            <span>⚠️ Content DNA Analysis Required</span>
          </div>
          <p class="mt-1 text-xs text-amber-200/80">
            This source needs its thesis, tone, and audience mapped before generating campaign assets.
          </p>
          <div class="mt-3 flex items-center gap-4">
            <button 
              type="button" 
              :disabled="analyzing"
              @click="analyzeSelected"
              class="rounded-lg bg-amber-400 px-4 py-2 text-xs font-extrabold text-slate-950 hover:bg-amber-300 disabled:opacity-50 transition"
            >
              {{ analyzing ? 'Analyzing Content DNA…' : 'Extract Content DNA Now' }}
            </button>
            <NuxtLink v-if="selectedSource" :to="`/sources/${selectedSource.id}/dna`" class="text-xs font-bold text-cyan-300 hover:underline">
              Open DNA Editor →
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Campaign Name -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
          Campaign Name
        </label>
        <input 
          v-model="name" 
          type="text" 
          placeholder="e.g. AI Automation Lead Generation Campaign" 
          required 
          class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
        />
      </div>

      <!-- Platform Selector Cards -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Target Channels & Platforms
        </label>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div 
            v-for="platform in platformOptions" 
            :key="platform.id"
            @click="togglePlatform(platform.id)"
            class="p-4 rounded-xl border cursor-pointer transition flex items-start gap-3 select-none"
            :class="platforms.includes(platform.id) ? 'border-cyan-500/60 bg-cyan-950/20 shadow-md' : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'"
          >
            <div class="h-9 w-9 rounded-lg flex items-center justify-center text-lg bg-slate-900 border border-slate-800 shrink-0">
              {{ platform.icon }}
            </div>
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-white">{{ platform.label }}</span>
                <span v-if="platforms.includes(platform.id)" class="text-cyan-400 text-xs font-bold">✓</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5">{{ platform.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Submit Action -->
      <div class="flex items-center justify-between pt-4">
        <NuxtLink to="/dashboard" class="text-xs font-semibold text-slate-400 hover:text-white">
          ← Cancel
        </NuxtLink>

        <button 
          type="submit" 
          :disabled="saving || !platforms.length || !selectedReady"
          class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-8 py-3.5 text-sm font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:scale-[1.02] disabled:opacity-50 transition"
        >
          <span>{{ saving ? 'Generating 7-Day Plan…' : 'Generate 7-Day Campaign →' }}</span>
        </button>
      </div>
    </form>
  </section>
</template>
