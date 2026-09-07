<script setup lang="ts">
const route = useRoute()
const { request } = useApi()
const { session, initialize } = useAuth()

const dna = ref<Record<string, any> | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

async function analyze() {
  dna.value = await request(`/sources/${route.params.id}/dna`, { method: 'POST' })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    await initialize()
    if (!session.value) return navigateTo('/auth')
    
    const status = await request<{ ready: boolean }>(`/sources/${route.params.id}/dna/status`)
    if (status.ready) {
      dna.value = await request(`/sources/${route.params.id}/dna`)
    } else {
      await analyze()
    }
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not load Content DNA.' 
  } finally { 
    loading.value = false 
  }
}

async function save() {
  if (!dna.value) return
  saving.value = true
  error.value = ''
  saved.value = false
  try {
    dna.value = await request(`/sources/${route.params.id}/dna`, { 
      method: 'PUT', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify(dna.value) 
    })
    saved.value = true
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not save Content DNA.' 
  } finally { 
    saving.value = false 
  }
}

onMounted(load)
</script>

<template>
  <section class="mx-auto max-w-4xl px-6 py-12">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-xs text-slate-400 mb-6">
      <NuxtLink to="/dashboard" class="hover:text-cyan-300">Dashboard</NuxtLink>
      <span>/</span>
      <span class="text-cyan-400 font-semibold">Step 2: Content DNA Extraction</span>
    </div>

    <!-- Header Panel -->
    <div class="glass-panel p-8 rounded-3xl mb-8">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">
            <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
            <span>Fact-Grounded Knowledge Matrix</span>
          </div>
          <h1 class="text-3xl font-extrabold text-white sm:text-4xl">Content DNA Review</h1>
          <p class="mt-2 text-sm text-slate-300">
            Review and adjust the extracted core thesis, tone, audience, and key claims before generating campaign posts.
          </p>
        </div>

        <div class="hidden sm:block">
          <div class="h-12 w-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-2xl text-cyan-400">
            🧬
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="py-20 text-center glass-card rounded-2xl">
      <div class="inline-flex items-center gap-3 text-cyan-400 font-bold text-sm">
        <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span>Extracting Content DNA with AI…</span>
      </div>
      <p class="text-xs text-slate-400 mt-2">Analyzing thesis, tone, audience segments, and quote references.</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="mb-6 rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-sm text-red-200">
      {{ error }}
    </div>

    <!-- Form & Fields -->
    <form v-if="dna" class="space-y-6" @submit.prevent="save">
      <!-- Title -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
          Source Title
        </label>
        <input 
          v-model="dna.title" 
          type="text" 
          class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none transition"
        />
      </div>

      <!-- Main Thesis -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2">
          Main Core Thesis
        </label>
        <textarea 
          v-model="dna.main_thesis" 
          rows="3" 
          class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none leading-relaxed transition"
        ></textarea>
      </div>

      <!-- Grid for Audience, Tone, CTA -->
      <div class="grid gap-6 md:grid-cols-3">
        <div class="glass-card p-5 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Target Audience
          </label>
          <input 
            v-model="dna.target_audience" 
            type="text" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-3.5 py-2.5 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div class="glass-card p-5 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Brand Tone
          </label>
          <input 
            v-model="dna.tone" 
            type="text" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-3.5 py-2.5 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div class="glass-card p-5 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Primary Call to Action (CTA)
          </label>
          <input 
            v-model="dna.cta" 
            type="text" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-3.5 py-2.5 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      <!-- Summary -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          Executive Content Summary
        </label>
        <textarea 
          v-model="dna.summary" 
          rows="4" 
          class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-slate-300 focus:border-cyan-500 focus:outline-none leading-relaxed transition"
        ></textarea>
      </div>

      <!-- Action Footer -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <button 
          type="submit" 
          :disabled="saving"
          class="w-full sm:w-auto rounded-xl bg-slate-800 border border-slate-700 px-6 py-3 text-xs font-bold text-white hover:bg-slate-700 transition"
        >
          {{ saving ? 'Saving Changes…' : 'Save DNA Settings' }}
        </button>

        <NuxtLink 
          :to="`/campaigns/create?source=${route.params.id}`" 
          class="w-full sm:w-auto flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-7 py-3 text-sm font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:scale-[1.02] transition"
        >
          <span>Create 7-Day Campaign Now</span>
          <span>→</span>
        </NuxtLink>
      </div>

      <div v-if="saved" class="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/30 text-xs text-emerald-300 flex items-center gap-2 font-bold">
        <span>✓ Content DNA saved successfully. You are ready to generate a campaign.</span>
      </div>
    </form>
  </section>
</template>
