<script setup lang="ts">
defineProps<{ report: any }>()
</script>

<template>
  <section class="rounded-xl border border-slate-800 bg-slate-950/70 p-5 space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold uppercase tracking-wider text-cyan-400">🔍 Source QA Verification Audit</span>
      </div>
      <span 
        class="px-2.5 py-0.5 text-xs font-extrabold rounded-full border"
        :class="{
          'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': report.status === 'PASS',
          'bg-amber-500/10 text-amber-400 border-amber-500/30': report.status === 'WARNING',
          'bg-red-500/10 text-red-400 border-red-500/30': report.status === 'FAIL'
        }"
      >
        {{ report.status === 'PASS' ? '✓ VERIFIED GROUNDED' : report.status }}
      </span>
    </div>

    <!-- Scores Grid -->
    <div class="grid grid-cols-3 gap-3">
      <div class="rounded-xl bg-slate-900/80 p-3 border border-slate-800 text-center">
        <p 
          class="text-2xl font-extrabold font-mono" 
          :class="report.faithfulness_score >= 80 ? 'text-emerald-400' : report.faithfulness_score >= 60 ? 'text-amber-400' : 'text-red-400'"
        >
          {{ report.faithfulness_score }}%
        </p>
        <p class="mt-0.5 text-[10px] uppercase font-bold text-slate-400">Faithfulness</p>
      </div>

      <div class="rounded-xl bg-slate-900/80 p-3 border border-slate-800 text-center">
        <p 
          class="text-2xl font-extrabold font-mono" 
          :class="report.source_coverage_score >= 80 ? 'text-emerald-400' : report.source_coverage_score >= 60 ? 'text-amber-400' : 'text-red-400'"
        >
          {{ report.source_coverage_score }}%
        </p>
        <p class="mt-0.5 text-[10px] uppercase font-bold text-slate-400">Source Coverage</p>
      </div>

      <div class="rounded-xl bg-slate-900/80 p-3 border border-slate-800 text-center">
        <p 
          class="text-2xl font-extrabold font-mono" 
          :class="report.brand_alignment_score >= 80 ? 'text-emerald-400' : report.brand_alignment_score >= 60 ? 'text-amber-400' : 'text-red-400'"
        >
          {{ report.brand_alignment_score }}%
        </p>
        <p class="mt-0.5 text-[10px] uppercase font-bold text-slate-400">Brand Fit</p>
      </div>
    </div>

    <!-- Unsupported Claims Warning -->
    <div v-if="report.unsupported_claims?.length" class="space-y-2">
      <div class="flex items-center gap-1.5 text-xs font-bold text-red-400">
        <span>⚠️ Flagged Unsupported Claims ({{ report.unsupported_claims.length }})</span>
      </div>
      <ul class="space-y-1.5 text-xs text-red-200">
        <li v-for="claim in report.unsupported_claims" :key="claim" class="rounded-lg bg-red-950/40 border border-red-900/50 p-2.5">
          {{ claim }}
        </li>
      </ul>
    </div>
    <div v-else class="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
      <span>✓ Zero unsupported claims detected. 100% grounded in source text.</span>
    </div>

    <!-- Supported Claims with Raw Quotes Evidence -->
    <div v-if="report.supported_claims?.length" class="space-y-2">
      <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Verified Evidence Citations</p>
      <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
        <div 
          v-for="item in report.supported_claims" 
          :key="item.claim" 
          class="rounded-lg bg-slate-900/90 border border-slate-800 p-2.5 text-xs space-y-1"
        >
          <p class="font-bold text-slate-200">✓ {{ item.claim }}</p>
          <p class="text-[11px] text-slate-400 font-mono italic">Source quote: "{{ item.evidence }}"</p>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="report.recommendations?.length" class="text-xs text-slate-400 space-y-1 border-t border-slate-800 pt-3">
      <p class="font-bold text-slate-300">AI Audit Recommendations:</p>
      <ul class="list-disc pl-4 space-y-1">
        <li v-for="rec in report.recommendations" :key="rec">{{ rec }}</li>
      </ul>
    </div>
  </section>
</template>
