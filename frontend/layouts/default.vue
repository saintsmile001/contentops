<script setup lang="ts">
const { session, initialize, signOut } = useAuth()
const route = useRoute()
const mobileMenuOpen = ref(false)

onMounted(initialize)

async function leave() {
  await signOut()
  await navigateTo('/')
}

const navLinks = computed(() => [
  { name: 'Dashboard', path: '/dashboard', authRequired: true },
  { name: 'New Source', path: '/create', authRequired: true },
  { name: 'New Campaign', path: '/campaigns/create', authRequired: true },
  { name: 'Creator Profile', path: '/profile', authRequired: true },
])
</script>

<template>
  <div class="min-h-screen bg-[#030712] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
    <!-- Dark Mesh Background Gradients -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl animate-pulse-glow"></div>
      <div class="absolute top-1/3 -right-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl animate-pulse-glow" style="animation-delay: 2s;"></div>
      <div class="absolute -bottom-40 left-1/3 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl animate-pulse-glow" style="animation-delay: 4s;"></div>
    </div>

    <!-- Navigation Header -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-slate-950/80 border-b border-slate-800/60">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <!-- Logo -->
        <NuxtLink to="/" class="group flex items-center gap-3 transition">
          <div class="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition duration-300">
            <div class="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
              <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div>
            <span class="text-lg font-extrabold tracking-tight text-white group-hover:text-cyan-400 transition">ContentOps<span class="text-cyan-400">.ai</span></span>
            <span class="hidden sm:block text-[10px] uppercase font-semibold tracking-wider text-slate-400">Content Engine</span>
          </div>
        </NuxtLink>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center gap-1 bg-slate-900/60 border border-slate-800/80 rounded-full px-4 py-1.5 backdrop-blur-md">
          <NuxtLink 
            to="/" 
            class="px-3.5 py-1.5 text-sm font-medium rounded-full transition"
            :class="route.path === '/' ? 'text-white bg-slate-800 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
          >
            Home
          </NuxtLink>
          <template v-if="session">
            <NuxtLink 
              v-for="link in navLinks" 
              :key="link.path" 
              :to="link.path" 
              class="px-3.5 py-1.5 text-sm font-medium rounded-full transition"
              :class="route.path === link.path ? 'text-cyan-300 bg-slate-800/90 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
            >
              {{ link.name }}
            </NuxtLink>
          </template>
        </nav>

        <!-- Right User / Auth Actions -->
        <div class="hidden md:flex items-center gap-3">
          <template v-if="!session">
            <NuxtLink to="/auth" class="text-sm font-medium text-slate-300 hover:text-white px-4 py-2 transition">
              Sign In
            </NuxtLink>
            <NuxtLink to="/auth" class="relative group overflow-hidden rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-400 p-[1px] font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition">
              <span class="flex items-center gap-2 rounded-[11px] bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 group-hover:bg-opacity-95 transition">
                <span>Get Started</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
              </span>
            </NuxtLink>
          </template>
          <template v-else>
            <NuxtLink to="/campaigns/create" class="flex items-center gap-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 px-3.5 py-2 text-xs font-bold text-cyan-300 hover:bg-cyan-500/20 hover:border-cyan-500/50 transition shadow-sm">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              <span>New Campaign</span>
            </NuxtLink>

            <div class="h-5 w-[1px] bg-slate-800"></div>

            <button 
              @click="leave" 
              class="flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-red-400 px-3 py-2 rounded-lg hover:bg-slate-900 transition"
              title="Sign out"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
              <span>Sign Out</span>
            </button>
          </template>
        </div>

        <!-- Mobile Menu Button -->
        <button 
          @click="mobileMenuOpen = !mobileMenuOpen" 
          class="md:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile Dropdown -->
      <div v-if="mobileMenuOpen" class="md:hidden border-b border-slate-800 bg-slate-950/95 px-6 py-4 space-y-3">
        <NuxtLink to="/" @click="mobileMenuOpen = false" class="block text-slate-300 hover:text-white py-1">Home</NuxtLink>
        <template v-if="session">
          <NuxtLink v-for="link in navLinks" :key="link.path" :to="link.path" @click="mobileMenuOpen = false" class="block text-slate-300 hover:text-cyan-300 py-1">
            {{ link.name }}
          </NuxtLink>
          <button @click="leave(); mobileMenuOpen = false" class="block text-red-400 hover:text-red-300 py-1 w-full text-left">Sign Out</button>
        </template>
        <template v-else>
          <NuxtLink to="/auth" @click="mobileMenuOpen = false" class="block rounded-lg bg-cyan-400 px-4 py-2.5 text-center font-bold text-slate-950">Sign In / Register</NuxtLink>
        </template>
      </div>
    </header>

    <!-- Main Content Container -->
    <main class="relative z-10">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="relative z-10 border-t border-slate-800/60 bg-slate-950/60 mt-20">
      <div class="mx-auto max-w-7xl px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-6 text-slate-400 text-sm">
        <div class="flex items-center gap-3">
          <div class="h-7 w-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold text-xs">
            ⚡
          </div>
          <span class="font-semibold text-slate-300">ContentOps AI Engine</span>
          <span class="text-slate-600">|</span>
          <span class="text-xs text-slate-500">100% Source-Grounded Content Workflows</span>
        </div>
        <div class="flex items-center gap-6 text-xs text-slate-500">
          <span>Supabase RLS Secured</span>
          <span>·</span>
          <span>FastAPI + Gemini AI</span>
          <span>·</span>
          <span>Nuxt 3</span>
        </div>
      </div>
    </footer>
  </div>
</template>
