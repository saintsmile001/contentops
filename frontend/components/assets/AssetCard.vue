<script setup lang="ts">
const props = defineProps<{ asset: any, dayNumber?: number }>()
const emit = defineEmits<{ updated: [asset: any] }>()
const { request } = useApi()

const editing = ref(false)
const regenerating = ref(false)
const showRegenModal = ref(false)
const regenInstruction = ref('')
const copied = ref(false)
const error = ref('')
const qaLoading = ref(false)
const qaReport = ref<any>(null)
const draft = ref({ ...props.asset, hashtags: (props.asset.hashtags || []).join(' ') })

watch(() => props.asset, (asset) => {
  draft.value = { ...asset, hashtags: (asset.hashtags || []).join(' ') }
}, { deep: true })

const quickPrompts = [
  'Make it shorter & punchier',
  'Add strong Call-to-Action',
  'Adopt a conversational tone',
  'Focus on key metrics & ROI'
]

async function copy() {
  await navigator.clipboard.writeText(props.asset.content)
  copied.value = true
  setTimeout(() => (copied.value = false), 1800)
}

async function save() {
  error.value = ''
  try {
    const updated = await request(`/assets/${props.asset.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: draft.value.title,
        hook: draft.value.hook || '',
        content: draft.value.content,
        cta: draft.value.cta || '',
        hashtags: typeof draft.value.hashtags === 'string' ? draft.value.hashtags.split(/\s+/).filter(Boolean) : draft.value.hashtags,
      }),
    })
    emit('updated', updated)
    editing.value = false
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not save this asset.'
  }
}

async function regenerate(promptText?: string) {
  const instructionToUse = promptText || regenInstruction.value
  regenerating.value = true
  error.value = ''
  try {
    const result = await request(`/assets/${props.asset.id}/regenerate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instruction: instructionToUse || undefined }),
    })
    draft.value = { ...result, hashtags: (result.hashtags || []).join(' ') }
    emit('updated', result)
    showRegenModal.value = false
    regenInstruction.value = ''
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'We could not regenerate this asset.'
  } finally {
    regenerating.value = false
  }
}

async function runQA() {
  qaLoading.value = true
  error.value = ''
  try {
    qaReport.value = await request(`/assets/${props.asset.id}/qa`, { method: 'POST' })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'QA check failed.'
  } finally {
    qaLoading.value = false
  }
}

async function loadQA() {
  try {
    qaReport.value = await request(`/assets/${props.asset.id}/qa`)
  } catch {}
}

function getPlatformBadge(platform: string) {
  switch (platform?.toLowerCase()) {
    case 'linkedin': return { label: 'LinkedIn Post', color: 'bg-blue-500/10 text-blue-300 border-blue-500/30' }
    case 'x': 
    case 'twitter': return { label: '𝕏 Post', color: 'bg-slate-800 text-cyan-300 border-cyan-500/30' }
    case 'threads': return { label: 'Threads', color: 'bg-purple-500/10 text-purple-300 border-purple-500/30' }
    case 'instagram': return { label: 'Instagram', color: 'bg-pink-500/10 text-pink-300 border-pink-500/30' }
    default: return { label: platform, color: 'bg-slate-800 text-slate-300 border-slate-700' }
  }
}

onMounted(loadQA)
</script>

<template>
  <article class="glass-card p-6 rounded-2xl relative transition hover:border-slate-700">
    <!-- Header Badge & Status -->
    <div class="flex items-center justify-between gap-4 border-b border-slate-800/80 pb-4 mb-4">
      <div class="flex items-center gap-3">
        <span 
          class="px-2.5 py-1 text-xs font-bold rounded-lg border shadow-xs"
          :class="getPlatformBadge(asset.platform).color"
        >
          {{ getPlatformBadge(asset.platform).label }}
        </span>
        <span class="text-xs text-slate-400 font-mono">Day {{ dayNumber || 1 }}</span>
      </div>

      <span 
        class="px-2.5 py-0.5 text-xs font-extrabold rounded-full border"
        :class="{
          'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': asset.status === 'READY',
          'bg-amber-500/10 text-amber-400 border-amber-500/30': asset.status === 'WARNING',
          'bg-slate-800 text-slate-400 border-slate-700': asset.status === 'DRAFT'
        }"
      >
        {{ asset.status }}
      </span>
    </div>

    <!-- Edit Mode -->
    <div v-if="editing" class="space-y-4">
      <div>
        <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Asset Title</label>
        <input v-model="draft.title" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-white" />
      </div>

      <div>
        <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Content Body</label>
        <textarea v-model="draft.content" rows="6" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-slate-200 font-mono leading-relaxed" />
      </div>

      <div>
        <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Call to Action (CTA)</label>
        <input v-model="draft.cta" class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-slate-200" />
      </div>

      <div class="flex items-center gap-3 pt-2">
        <button @click="save" class="rounded-xl bg-cyan-400 px-4 py-2 text-xs font-bold text-slate-950">Save Edits</button>
        <button @click="editing = false" class="text-xs font-semibold text-slate-400 hover:text-white">Cancel</button>
      </div>
    </div>

    <!-- View Mode -->
    <div v-else class="space-y-4">
      <h3 class="font-bold text-white text-base leading-snug">{{ asset.title }}</h3>

      <div class="rounded-xl bg-slate-950/80 p-4 border border-slate-800/80">
        <p class="whitespace-pre-line text-xs font-mono text-slate-200 leading-relaxed">{{ asset.content }}</p>
      </div>

      <div v-if="asset.cta" class="text-xs text-cyan-300 font-medium flex items-center gap-1.5">
        <span class="text-slate-500 font-bold uppercase text-[10px]">CTA:</span>
        <span>{{ asset.cta }}</span>
      </div>

      <div v-if="asset.hashtags?.length" class="flex flex-wrap gap-1.5">
        <span v-for="tag in asset.hashtags" :key="tag" class="text-xs text-cyan-400 font-mono">#{{ tag.replace('#', '') }}</span>
      </div>

      <!-- Action Toolbar -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div class="flex flex-wrap items-center gap-2">
          <button 
            @click="copy" 
            class="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-xs font-bold text-slate-200 hover:border-cyan-500/50 hover:text-cyan-300 transition"
          >
            <span v-if="copied" class="text-emerald-400 font-bold">✓ Copied!</span>
            <span v-else>📋 Copy Post</span>
          </button>

          <button 
            @click="editing = true" 
            class="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-slate-500 transition"
          >
            ✏️ Edit
          </button>

          <button 
            @click="showRegenModal = !showRegenModal" 
            class="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-slate-500 transition"
          >
            ⚡ Regenerate
          </button>
        </div>

        <button 
          @click="runQA" 
          :disabled="qaLoading"
          class="flex items-center gap-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 px-3 py-1.5 text-xs font-bold text-cyan-300 hover:bg-cyan-500/20 transition disabled:opacity-50"
        >
          <span v-if="qaLoading" class="animate-spin text-xs">⚡</span>
          <span>{{ qaLoading ? 'Auditing Claims…' : '🔍 Run Grounded QA' }}</span>
        </button>
      </div>
    </div>

    <!-- Inline Regeneration Modal -->
    <div v-if="showRegenModal" class="mt-4 rounded-xl border border-slate-700 bg-slate-950/90 p-4 space-y-3">
      <div class="flex items-center justify-between text-xs font-bold text-slate-300">
        <span>AI Regeneration Prompt</span>
        <button @click="showRegenModal = false" class="text-slate-500 hover:text-white">✕</button>
      </div>

      <!-- Quick Preset Prompt Pills -->
      <div class="flex flex-wrap gap-1.5">
        <button 
          v-for="preset in quickPrompts" 
          :key="preset"
          @click="regenerate(preset)"
          class="text-[10px] font-semibold bg-slate-900 border border-slate-800 text-slate-300 hover:border-cyan-400 hover:text-cyan-300 px-2.5 py-1 rounded-full transition"
        >
          {{ preset }}
        </button>
      </div>

      <input 
        v-model="regenInstruction" 
        type="text" 
        placeholder="Or type custom instructions (e.g. Add 3 bullet points)..." 
        class="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500"
      />

      <div class="flex justify-end gap-2">
        <button @click="showRegenModal = false" class="text-xs text-slate-400 px-3 py-1.5">Cancel</button>
        <button 
          @click="regenerate()" 
          :disabled="regenerating"
          class="rounded-lg bg-cyan-400 px-4 py-1.5 text-xs font-bold text-slate-950 disabled:opacity-50"
        >
          {{ regenerating ? 'Generating…' : 'Regenerate Post' }}
        </button>
      </div>
    </div>

    <!-- Inline QA Report -->
    <QAReport v-if="qaReport" :report="qaReport" class="mt-4" />

    <!-- Error message -->
    <p v-if="error" class="mt-3 text-xs text-red-400 font-medium">{{ error }}</p>
  </article>
</template>
