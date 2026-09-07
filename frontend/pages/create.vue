<script setup lang="ts">
const { request } = useApi()
const { session, initialize } = useAuth()
const title = ref('')
const content = ref('')
const file = ref<File | null>(null)
const mode = ref<'text' | 'file'>('text')
const saving = ref(false)
const success = ref('')
const error = ref('')
const isDragging = ref(false)

const wordCount = computed(() => {
  if (!content.value.trim()) return 0
  return content.value.trim().split(/\s+/).length
})

onMounted(async () => {
  await initialize()
  if (!session.value) navigateTo('/auth')
})

function selectFile(event: Event) {
  const selected = (event.target as HTMLInputElement).files?.[0] || null
  handleFile(selected)
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const dropped = event.dataTransfer?.files?.[0] || null
  if (dropped) {
    mode.value = 'file'
    handleFile(dropped)
  }
}

function handleFile(selected: File | null) {
  success.value = ''
  error.value = ''
  if (selected && selected.size > 10 * 1024 * 1024) {
    error.value = 'Files must be smaller than 10 MB.'
    file.value = null
    return
  }
  file.value = selected
  if (selected && !title.value) {
    title.value = selected.name.replace(/\.[^/.]+$/, '')
  }
}

async function saveSource() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    if (mode.value === 'file' && file.value) {
      const source = await request<{ id: string }>('/sources/upload', {
        method: 'POST',
        headers: { 
          'Content-Type': file.value.type || 'application/octet-stream', 
          'X-File-Name': file.value.name 
        },
        body: file.value
      })
      await navigateTo(`/sources/${source.id}/dna`)
    } else {
      const source = await request<{ id: string }>('/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.value, content: content.value })
      })
      await navigateTo(`/sources/${source.id}/dna`)
    }
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : 'We could not save your source right now.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="mx-auto max-w-4xl px-6 py-12">
    <!-- Breadcrumb & Step -->
    <div class="flex items-center gap-2 text-xs text-slate-400 mb-6">
      <NuxtLink to="/dashboard" class="hover:text-cyan-300">Dashboard</NuxtLink>
      <span>/</span>
      <span class="text-cyan-400 font-semibold">Step 1: Add Source Material</span>
    </div>

    <!-- Header -->
    <div class="glass-panel p-8 rounded-3xl mb-8">
      <div class="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-cyan-400 mb-3">
        <span class="flex h-2 w-2 rounded-full bg-cyan-400"></span>
        <span>Source Grounding Engine</span>
      </div>
      <h1 class="text-3xl font-extrabold text-white sm:text-4xl">Add Source Material</h1>
      <p class="mt-2 text-sm text-slate-300 max-w-2xl">
        Paste your raw article, whitepaper, or transcript text, or upload a document file (.pdf, .md, .txt).
      </p>

      <!-- Input Mode Switcher -->
      <div class="mt-8 flex gap-2 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 max-w-md">
        <button 
          type="button" 
          @click="mode = 'text'" 
          class="flex-1 py-2.5 px-4 text-xs font-bold rounded-xl transition flex items-center justify-center gap-2"
          :class="mode === 'text' ? 'bg-slate-800 text-white shadow-sm border border-slate-700' : 'text-slate-400 hover:text-slate-200'"
        >
          <span>✍️ Direct Text Paste</span>
        </button>
        <button 
          type="button" 
          @click="mode = 'file'" 
          class="flex-1 py-2.5 px-4 text-xs font-bold rounded-xl transition flex items-center justify-center gap-2"
          :class="mode === 'file' ? 'bg-slate-800 text-white shadow-sm border border-slate-700' : 'text-slate-400 hover:text-slate-200'"
        >
          <span>📁 File Upload (.PDF / .MD)</span>
        </button>
      </div>
    </div>

    <!-- Feedback messages -->
    <div v-if="error" class="mb-6 rounded-2xl border border-red-900/80 bg-red-950/40 p-4 text-sm text-red-200">
      {{ error }}
    </div>

    <!-- Form Container -->
    <form @submit.prevent="saveSource" class="space-y-6">
      <!-- Title Input -->
      <div class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2" for="title">
          Source Title <span class="text-cyan-400">*</span>
        </label>
        <input 
          id="title" 
          v-model="title" 
          type="text" 
          placeholder="e.g. Q3 Enterprise AI Automation Playbook" 
          required 
          class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none transition"
        />
      </div>

      <!-- Mode 1: Text Paste -->
      <div v-if="mode === 'text'" class="glass-card p-6 rounded-2xl">
        <div class="flex items-center justify-between mb-2">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300" for="content">
            Source Content <span class="text-cyan-400">*</span>
          </label>
          <span class="text-xs font-mono text-cyan-400">{{ wordCount }} words</span>
        </div>
        <textarea 
          id="content" 
          v-model="content" 
          placeholder="Paste your original article, transcript, whitepaper, or long-form post here…" 
          required 
          rows="10" 
          class="w-full rounded-xl border border-slate-800 bg-slate-950/90 px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none font-mono text-xs leading-relaxed transition"
        ></textarea>
      </div>

      <!-- Mode 2: File Upload Dropzone -->
      <div v-else class="glass-card p-6 rounded-2xl">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Upload File Document
        </label>

        <div 
          @dragover.prevent="isDragging = true" 
          @dragleave.prevent="isDragging = false" 
          @drop.prevent="handleDrop"
          class="relative border-2 border-dashed rounded-2xl p-8 text-center transition flex flex-col items-center justify-center cursor-pointer"
          :class="isDragging ? 'border-cyan-400 bg-cyan-950/30' : file ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-800 hover:border-slate-600 bg-slate-950/40'"
        >
          <input 
            id="file" 
            type="file" 
            accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf" 
            @change="selectFile" 
            class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
          />

          <div v-if="!file" class="space-y-3">
            <div class="h-12 w-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-xl mx-auto text-cyan-400">
              📄
            </div>
            <div>
              <p class="text-sm font-bold text-white">Drag & drop your document here, or <span class="text-cyan-400 underline">browse</span></p>
              <p class="text-xs text-slate-400 mt-1">Supports PDF, Markdown (.md), or Plain Text (.txt) up to 10MB</p>
            </div>
          </div>

          <div v-else class="flex items-center gap-3 text-left">
            <div class="h-10 w-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-lg font-bold">
              ✓
            </div>
            <div>
              <p class="text-sm font-bold text-emerald-300">{{ file.name }}</p>
              <p class="text-xs text-slate-400">{{ (file.size / 1024).toFixed(1) }} KB</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Action -->
      <div class="flex items-center justify-between pt-4">
        <NuxtLink to="/dashboard" class="text-xs font-semibold text-slate-400 hover:text-white">
          ← Cancel
        </NuxtLink>

        <button 
          type="submit" 
          :disabled="saving || (mode === 'text' && (!title || !content)) || (mode === 'file' && !file)"
          class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-400 to-emerald-400 px-7 py-3 text-sm font-extrabold text-slate-950 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:scale-[1.02] disabled:opacity-50 transition"
        >
          <span>{{ saving ? 'Ingesting & Saving…' : 'Proceed to Content DNA →' }}</span>
        </button>
      </div>
    </form>
  </section>
</template>
