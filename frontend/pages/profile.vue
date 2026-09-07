<script setup lang="ts">
const { request } = useApi()
const { session, initialize } = useAuth()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

const profile = ref({
  name: '',
  description: '',
  industry: '',
  audience: '',
  tone: '',
  default_cta: '',
  primary_platform: 'linkedin',
})

const platformOptions = [
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'x', label: 'X (Twitter)' },
  { id: 'instagram', label: 'Instagram' },
  { id: 'threads', label: 'Threads' }
]

onMounted(async () => {
  try {
    await initialize()
    if (!session.value) return navigateTo('/auth')
    const existing = await request<any>('/profile')
    if (existing) {
      profile.value = {
        name: existing.name || '',
        description: existing.description || '',
        industry: existing.industry || '',
        audience: existing.audience || '',
        tone: existing.tone || '',
        default_cta: existing.default_cta || '',
        primary_platform: existing.primary_platform || 'linkedin',
      }
    }
  } catch {
    // Fine if profile empty
  } finally {
    loading.value = false
  }
})

async function saveProfile() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await request('/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile.value),
    })
    success.value = 'Creator profile saved successfully.'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not save your profile.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="mx-auto max-w-3xl px-6 py-12">
    <!-- Header -->
    <div class="glass-panel p-8 rounded-3xl mb-8">
      <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-cyan-400 mb-2">
        <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
        <span>Brand & Tone Personalization</span>
      </div>
      <h1 class="text-3xl font-extrabold text-white sm:text-4xl">Creator Profile</h1>
      <p class="mt-2 text-sm text-slate-300">
        Your profile preferences steer the tone, voice, and CTA across all AI-generated campaign posts.
      </p>
    </div>

    <div v-if="loading" class="py-12 text-center text-cyan-400 font-semibold text-sm">
      Loading profile preferences…
    </div>

    <form v-else class="space-y-6" @submit.prevent="saveProfile">
      <!-- Name & Industry -->
      <div class="grid gap-6 md:grid-cols-2">
        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Creator / Brand Name
          </label>
          <input 
            v-model="profile.name" 
            type="text" 
            placeholder="e.g. Sarah Chen or TechOps Daily" 
            required 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Industry Domain
          </label>
          <input 
            v-model="profile.industry" 
            type="text" 
            placeholder="e.g. B2B SaaS, AI & Cloud Computing" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      <!-- Description -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
          Brand & Expertise Summary
        </label>
        <textarea 
          v-model="profile.description" 
          rows="3" 
          placeholder="Summarize your background, core topics, and expertise..." 
          class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none leading-relaxed"
        ></textarea>
      </div>

      <!-- Audience & Tone Grid -->
      <div class="grid gap-6 md:grid-cols-2">
        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Target Audience
          </label>
          <input 
            v-model="profile.audience" 
            type="text" 
            placeholder="e.g. CTOs, VP of Engineering, Founders" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Preferred Brand Tone
          </label>
          <input 
            v-model="profile.tone" 
            type="text" 
            placeholder="e.g. Authoritative, direct, data-driven" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
          />
        </div>
      </div>

      <!-- CTA & Platform -->
      <div class="grid gap-6 md:grid-cols-2">
        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Default Call to Action
          </label>
          <input 
            v-model="profile.default_cta" 
            type="text" 
            placeholder="e.g. Subscribe to our newsletter for weekly guides" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-white focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div class="glass-card p-6 rounded-2xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            Primary Target Channel
          </label>
          <select 
            v-model="profile.primary_platform" 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option v-for="p in platformOptions" :key="p.id" :value="p.id">{{ p.label }}</option>
          </select>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="error" class="rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-xs text-red-200">
        {{ error }}
      </div>

      <div v-if="success" class="rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-xs text-emerald-300 font-bold">
        ✓ {{ success }}
      </div>

      <!-- Action -->
      <div class="flex justify-end pt-2">
        <button 
          type="submit" 
          :disabled="saving"
          class="rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-7 py-3 text-xs font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 disabled:opacity-50 transition"
        >
          {{ saving ? 'Saving Profile…' : 'Save Creator Profile →' }}
        </button>
      </div>
    </form>
  </section>
</template>
