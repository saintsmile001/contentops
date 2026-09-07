<template>
  <div class="relative overflow-hidden">
    <!-- Hero Section -->
    <section class="mx-auto max-w-6xl px-6 pt-16 pb-20 lg:pt-24 lg:pb-28">
      <div class="text-center max-w-3xl mx-auto">
        <!-- Top Badge -->
        <div class="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 text-xs font-bold text-cyan-300 shadow-sm backdrop-blur-md mb-8">
          <span class="flex h-2 w-2 rounded-full bg-cyan-400"></span>
          <span>ContentOps AI · Content Engine</span>
        </div>

        <!-- Headline -->
        <h1 class="text-5xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl leading-[1.15]">
          One Source Material.<br />
          <span class="gradient-text">A Full 7-Day Campaign.</span>
        </h1>

        <!-- Subtitle -->
        <p class="mt-6 text-base sm:text-lg leading-relaxed text-slate-300 max-w-2xl mx-auto font-medium">
          Turn long-form articles, whitepapers, and transcripts into multi-channel social posts—fact-checked against your original content.
        </p>

        <!-- CTA Action Buttons -->
        <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
          <NuxtLink 
            to="/create" 
            class="group inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 px-8 py-3.5 text-sm font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/35 hover:scale-[1.02] transition duration-300"
          >
            <span>Create First Campaign</span>
            <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
          </NuxtLink>

          <NuxtLink 
            to="/dashboard" 
            class="inline-flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-6 py-3.5 text-sm font-semibold text-slate-200 hover:border-slate-600 hover:bg-slate-800/80 backdrop-blur-md transition"
          >
            <span>Open Dashboard</span>
          </NuxtLink>
        </div>
      </div>

      <!-- 3-Step Pipeline Cards -->
      <div class="mt-16 grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <!-- Step 1 Card -->
        <div class="glass-card p-6 rounded-2xl relative">
          <div class="flex items-center justify-between mb-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-extrabold text-xs">1</span>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Step 1</span>
          </div>
          <h3 class="text-base font-bold text-white mb-1.5">Add Your Content</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Upload a PDF, Markdown file, or paste your raw article text directly.
          </p>
        </div>

        <!-- Step 2 Card -->
        <div class="glass-card p-6 rounded-2xl relative">
          <div class="flex items-center justify-between mb-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 font-extrabold text-xs">2</span>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Step 2</span>
          </div>
          <h3 class="text-base font-bold text-white mb-1.5">Extract Core Insights</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Automatically pulls your main points, target audience, tone, and key quotes.
          </p>
        </div>

        <!-- Step 3 Card -->
        <div class="glass-card p-6 rounded-2xl relative">
          <div class="flex items-center justify-between mb-4">
            <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-extrabold text-xs">3</span>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Step 3</span>
          </div>
          <h3 class="text-base font-bold text-white mb-1.5">7-Day Campaign + Fact Check</h3>
          <p class="text-xs text-slate-400 leading-relaxed">
            Generates ready-to-publish posts for LinkedIn, X, and Threads, verified for 100% accuracy.
          </p>
        </div>
      </div>

      <!-- Feature Pill Badges -->
      <div class="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs font-semibold text-slate-400 max-w-3xl mx-auto pt-8 border-t border-slate-800/80">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          <span>Fact-Checked Accuracy</span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          <span>Multi-Platform Export</span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          <span>Ready-to-Publish Plans</span>
        </div>
      </div>
    </section>

    <!-- Bottom Quick Launch Banner -->
    <section class="mx-auto max-w-5xl px-6 pb-16">
      <div class="glass-panel p-8 md:p-10 rounded-3xl text-center border-cyan-500/20 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950">
        <h2 class="text-2xl font-extrabold text-white sm:text-3xl">Ready to turn your content into a campaign?</h2>
        <p class="mt-2 text-xs sm:text-sm text-slate-400">Generate a full 7-day post schedule in under 60 seconds.</p>
        <div class="mt-6">
          <NuxtLink to="/create" class="inline-block rounded-xl bg-cyan-400 px-6 py-3 text-xs font-extrabold text-slate-950 hover:bg-cyan-300 transition">
            Start Campaign →
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
