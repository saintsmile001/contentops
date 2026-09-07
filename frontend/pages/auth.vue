<script setup lang="ts">
const { configured, session, initialize, signIn, signUp } = useAuth()
const email = ref('')
const password = ref('')
const mode = ref<'signin' | 'signup'>('signin')
const loading = ref(false)
const message = ref('')
const error = ref('')

onMounted(initialize)
watch(session, value => { if (value) navigateTo('/dashboard') })

async function submit() {
  loading.value = true
  message.value = ''
  error.value = ''
  try { 
    if (mode.value === 'signin') {
      await signIn(email.value, password.value)
    } else { 
      message.value = await signUp(email.value, password.value) ? 'Check your email to confirm your account, then sign in.' : 'Your account is ready.' 
    } 
  } catch (caught) { 
    error.value = caught instanceof Error ? caught.message : 'We could not complete authentication.' 
  } finally { 
    loading.value = false 
  }
}
</script>

<template>
  <section class="mx-auto max-w-md px-6 py-20">
    <div class="glass-card p-8 rounded-3xl relative">
      <div class="text-center mb-8">
        <div class="h-12 w-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 text-2xl font-bold mx-auto mb-3">
          ⚡
        </div>
        <h1 class="text-2xl font-extrabold text-white">
          {{ mode === 'signin' ? 'Welcome back' : 'Create your account' }}
        </h1>
        <p class="mt-2 text-xs text-slate-400">
          Access your grounded Content DNA & campaign workspace.
        </p>
      </div>

      <div v-if="!configured" class="rounded-xl border border-amber-900/80 bg-amber-950/40 p-4 text-xs text-amber-200">
        Authentication configuration warning. Please ensure Supabase credentials are set.
      </div>

      <form v-else class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Email Address</label>
          <input 
            v-model="email" 
            type="email" 
            autocomplete="email" 
            placeholder="you@company.com" 
            required 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Password</label>
          <input 
            v-model="password" 
            type="password" 
            autocomplete="current-password" 
            placeholder="••••••••" 
            minlength="6" 
            required 
            class="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-xs text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        <div v-if="error" class="rounded-xl border border-red-900/80 bg-red-950/40 p-3 text-xs text-red-200">
          {{ error }}
        </div>

        <div v-if="message" class="rounded-xl border border-emerald-900/80 bg-emerald-950/40 p-3 text-xs text-emerald-200">
          {{ message }}
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-5 py-3 text-xs font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 disabled:opacity-50 transition"
        >
          {{ loading ? 'Please wait…' : mode === 'signin' ? 'Sign In to Workspace →' : 'Create Account →' }}
        </button>
      </form>

      <div class="mt-6 pt-4 border-t border-slate-800/80 text-center">
        <button 
          @click="mode = mode === 'signin' ? 'signup' : 'signin'" 
          class="text-xs font-semibold text-cyan-400 hover:underline"
        >
          {{ mode === 'signin' ? "Don't have an account? Sign up" : 'Already have an account? Sign in' }}
        </button>
      </div>
    </div>
  </section>
</template>
