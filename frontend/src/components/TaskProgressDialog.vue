<template>
  <el-dialog
    :model-value="visible"
    :title="null"
    width="700px"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    @close="$emit('close')"
  >
    <div class="progress-dialog">
      <!-- Header -->
      <div class="pd-header">
        <h2 class="pd-title">{{ typeLabel }} · {{ isDone ? '已完成' : '生成中' }}</h2>
        <div class="pd-header-right">
          <span v-if="!isDone" class="pd-pct">{{ progress }}%</span>
          <template v-if="isDone">
            <el-button size="small" class="pd-btn" @click="handlePlay">
              <span class="pd-btn-icon">{{ isPlaying ? '⏸' : '▶' }}</span> {{ isPlaying ? '暂停' : '播放' }}
            </el-button>
            <el-button size="small" class="pd-btn pd-btn-primary" @click="emit('done', resultId!)">
              查看详情 →
            </el-button>
          </template>
        </div>
      </div>
      <div class="pd-bar">
        <div class="pd-bar-fill" :style="{ width: progress + '%' }"></div>
      </div>

      <!-- Body: Timeline + Content -->
      <div class="pd-body">
        <!-- Left: Timeline -->
        <div class="pd-timeline">
          <div
            v-for="(step, i) in steps"
            :key="step.key"
            :class="['pd-step', { active: isStepActive(step.key), done: isStepDone(step.key) }]"
          >
            <div class="pd-step-dot">
              <span v-if="isStepDone(step.key)">✓</span>
              <span v-else-if="step.key === currentStep" class="pd-step-spin"></span>
            </div>
            <div class="pd-step-line" v-if="i < steps.length - 1"></div>
            <span class="pd-step-label">{{ step.label }}</span>
          </div>
        </div>

        <!-- Right: Content -->
        <div class="pd-content">
          <!-- Script not ready -->
          <div v-if="!scriptData" class="pd-placeholder">
            <span class="pd-placeholder-icon">✨</span>
            <span>AI 正在创作脚本...</span>
          </div>

          <!-- Script ready: show all revealed content -->
          <template v-else>
            <!-- Title -->
            <transition name="fade-up">
              <div v-if="revealStage >= 0" class="pd-section">
                <span class="pd-section-label">名称</span>
                <h3 class="pd-script-title">{{ scriptData.title }}</h3>
              </div>
            </transition>

            <!-- Description -->
            <transition name="fade-up">
              <div v-if="revealStage >= 1" class="pd-section">
                <span class="pd-section-label">概述</span>
                <p class="pd-script-desc">{{ scriptData.description }}</p>
              </div>
            </transition>

            <!-- Characters -->
            <transition name="fade-up">
              <div v-if="revealStage >= 2" class="pd-section">
                <span class="pd-section-label">角色</span>
                <div class="pd-characters">
                  <div v-for="sp in scriptData.speakers" :key="sp.name" class="pd-char-chip">
                    <span class="pd-char-avatar">{{ sp.name[0] }}</span>
                    <div class="pd-char-info">
                      <span class="pd-char-name">{{ sp.name }}</span>
                      <span class="pd-char-role">{{ sp.role }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </transition>

            <!-- Lines -->
            <transition name="fade-up">
              <div v-if="revealStage >= 3" class="pd-section">
                <span class="pd-section-label">对话内容</span>
                <div class="pd-lines">
                  <div v-for="(line, i) in visibleLines" :key="i" class="pd-line">
                    <span class="pd-line-speaker">{{ line.speaker }}</span>
                    <span class="pd-line-text">{{ line.text }}</span>
                    <span class="pd-line-status" v-if="revealStage >= 4">
                      <template v-if="getAudioStatus(i) === 'done'">✅</template>
                      <template v-else-if="getAudioStatus(i) === 'doing'"><span class="pd-line-spin"></span></template>
                      <template v-else>⬜</template>
                    </span>
                  </div>
                </div>
              </div>
            </transition>
          </template>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="pd-error">
        <span>❌ {{ error }}</span>
      </div>

      <!-- Inline player (hidden) -->
      <audio ref="playRef" :src="playSrc" @ended="isPlaying = false" @pause="isPlaying = false" @play="isPlaying = true" />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'

interface StepData {
  stage?: string
  script?: {
    title?: string
    description?: string
    speakers?: Array<{ name: string; role: string; voice_id: string }>
    script?: Array<{ speaker: string; text: string; emotion: string }>
    segments?: Array<{ character: string; text: string; emotion: string }>
  }
  audio_status?: Record<string, string>
}

const props = defineProps<{
  visible: boolean
  type: string
  progress: number
  stepData: StepData | null
  error?: string | null
  resultId?: string | null
}>()

const emit = defineEmits<{
  close: []
  done: [resultId: string]
}>()

// ===== Timeline steps =====
const steps = [
  { key: 'name', label: '名称' },
  { key: 'desc', label: '概述' },
  { key: 'chars', label: '角色' },
  { key: 'content', label: '内容' },
  { key: 'audio', label: '音频生成' },
]

// Map backend stage to timeline step
const currentStep = computed(() => {
  if (isDone.value) return 'done'
  const s = props.stepData?.stage
  if (!s || s === 'generating_script') return 'name'
  if (s === 'script_ready' || s === 'synthesizing_audio' || s === 'merging') {
    if (revealStage.value < 1) return 'name'
    if (revealStage.value < 2) return 'desc'
    if (revealStage.value < 3) return 'chars'
    if (revealStage.value < 4) return 'content'
    return 'audio'
  }
  return 'name'
})

function isStepDone(key: string) {
  if (isDone.value) return true
  const order = steps.map(s => s.key)
  const cur = order.indexOf(currentStep.value)
  return order.indexOf(key) < cur
}

function isStepActive(key: string) {
  if (isDone.value) return false
  return key === currentStep.value
}

// ===== Script data =====
const scriptData = computed(() => props.stepData?.script || null)
const audioStatus = computed(() => props.stepData?.audio_status || null)

const isDone = computed(() => props.progress >= 100 || props.stepData?.stage === 'done')
const typeLabel = computed(() => {
  return { podcast: '播客', audiobook: '有声书', video: '视频', image: '图片' }[props.type] || props.type
})

// Play/pause audio
const playSrc = ref('')
const playRef = ref<HTMLAudioElement>()
const isPlaying = ref(false)

function handlePlay() {
  if (!playRef.value || !playSrc.value) {
    // First click: set source and play
    if (!props.resultId) return
    const m: Record<string, string> = { podcast: '/api/podcasts/', audiobook: '/api/audiobooks/' }
    const prefix = m[props.type] || '/api/podcasts/'
    playSrc.value = prefix + props.resultId + '/audio'
    setTimeout(() => {
      playRef.value?.play()
      isPlaying.value = true
    }, 100)
    return
  }
  if (isPlaying.value) {
    playRef.value.pause()
    isPlaying.value = false
  } else {
    playRef.value.play()
    isPlaying.value = true
  }
}

// ===== Animated reveal =====
const revealStage = ref(-1)  // -1=none, 0=title, 1=desc, 2=chars, 3=content streaming, 4=audio progress
const visibleLineCount = ref(0)
let stageTimers: ReturnType<typeof setTimeout>[] = []
let lineTimer: ReturnType<typeof setInterval> | null = null

function cleanupTimers() {
  stageTimers.forEach(t => clearTimeout(t))
  stageTimers = []
  if (lineTimer) { clearInterval(lineTimer); lineTimer = null }
}

// When script first arrives, start the staged reveal
watch(() => props.stepData?.stage, (stage, oldStage) => {
  if (stage === 'script_ready' && oldStage === 'generating_script') {
    startRevealAnimation()
  }
  if (stage === 'done') {
    cleanupTimers()
    revealStage.value = 4
    visibleLineCount.value = allLines.value.length
    // Don't auto-navigate, user clicks button
  }
})

// Handle dialog open/close
watch(() => props.visible, (vis) => {
  if (vis) {
    if (!scriptData.value) {
      // Still generating, just show placeholder
      revealStage.value = -1
    } else if (props.progress >= 100 || props.stepData?.stage === 'done') {
      // Already done, show all
      revealStage.value = 4
      visibleLineCount.value = allLines.value.length
    } else if (revealStage.value < 0) {
      // Script ready but haven't animated yet
      startRevealAnimation()
    }
  } else {
    cleanupTimers()
  }
})

function startRevealAnimation() {
  cleanupTimers()
  revealStage.value = -1
  visibleLineCount.value = 0

  // Staged reveal: name(0.5s) → desc(0.8s) → chars(1s) → content streaming(2s+) → audio
  const delays = [500, 800, 1000, 2000]
  let acc = 0
  delays.forEach((delay, i) => {
    acc += delay
    stageTimers.push(setTimeout(() => { revealStage.value = i }, acc))
  })

  // Streaming lines
  const total = allLines.value.length
  acc += 300
  stageTimers.push(setTimeout(() => {
    visibleLineCount.value = 1
    lineTimer = setInterval(() => {
      if (visibleLineCount.value < total) {
        visibleLineCount.value++
      } else {
        if (lineTimer) clearInterval(lineTimer)
        // Lines done, move to audio stage after a beat
        stageTimers.push(setTimeout(() => { revealStage.value = 4 }, 500))
      }
    }, 300)
  }, acc))
}

const allLines = computed(() => {
  if (!scriptData.value) return []
  return scriptData.value.script || scriptData.value.segments || []
})

const visibleLines = computed(() => {
  return allLines.value.slice(0, visibleLineCount.value)
})

function getAudioStatus(idx: number): string {
  if (!audioStatus.value) return 'pending'
  return audioStatus.value[String(idx)] || 'pending'
}

onUnmounted(cleanupTimers)
</script>

<style scoped>
.progress-dialog { padding: 0; }

.pd-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-base);
}
.pd-title {
  font-family: var(--font-display); font-size: 24px; font-weight: 300;
  color: var(--ink);
}
.pd-header-right { display: flex; align-items: center; gap: 8px; }
.pd-btn {
  border-radius: var(--r-pill) !important;
  font-size: 13px !important; font-weight: 500 !important;
  padding: 5px 14px !important; height: auto !important;
  border-color: var(--hairline-strong) !important; color: var(--ink) !important;
  background: var(--surface-card) !important;
}
.pd-btn:hover { border-color: var(--ink-primary) !important; }
.pd-btn-primary {
  background: var(--ink-primary) !important;
  border-color: var(--ink-primary) !important;
  color: var(--on-primary) !important;
}
.pd-btn-primary:hover { background: var(--ink-primary-active) !important; }
.pd-btn-icon { margin-right: 2px; }
.pd-pct {
  font-size: 14px; font-weight: 600; color: var(--ink);
  background: var(--surface-strong); padding: 4px 12px;
  border-radius: var(--r-pill);
}
.pd-bar {
  height: 4px; background: var(--hairline-soft);
  border-radius: 2px; overflow: hidden; margin-bottom: var(--space-lg);
}
.pd-bar-fill {
  height: 100%; border-radius: 2px;
  background: var(--ink-primary);
  transition: width 0.5s ease;
}

/* Body */
.pd-body {
  display: flex; gap: var(--space-lg);
  min-height: 300px; max-height: 480px;
}

/* Timeline */
.pd-timeline {
  width: 110px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 0;
  padding-top: 4px;
}
.pd-step {
  display: flex; flex-direction: column; align-items: flex-start;
  position: relative; padding-left: 26px;
  padding-bottom: var(--space-base);
}
.pd-step:last-child { padding-bottom: 0; }
.pd-step-dot {
  position: absolute; left: 0; top: 0;
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--hairline);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; color: var(--muted-soft);
  transition: all 0.3s;
}
.pd-step.done .pd-step-dot {
  background: var(--ink-primary); color: var(--on-primary);
}
.pd-step.active .pd-step-dot {
  background: var(--canvas-soft); border: 2px solid var(--ink-primary);
}
.pd-step-spin {
  width: 8px; height: 8px; border: 2px solid var(--hairline-strong);
  border-top-color: var(--ink-primary); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.pd-step-line {
  position: absolute; left: 8px; top: 20px;
  width: 2px; bottom: 0; background: var(--hairline);
  transition: background 0.3s;
}
.pd-step.done .pd-step-line { background: var(--ink-primary); }
.pd-step-label {
  font-size: 12px; font-weight: 500;
  color: var(--muted-soft); line-height: 18px;
  transition: color 0.3s;
}
.pd-step.done .pd-step-label { color: var(--ink); }
.pd-step.active .pd-step-label { color: var(--ink); font-weight: 600; }

/* Content */
.pd-content { flex: 1; overflow-y: auto; padding-right: var(--space-xs); }

.pd-placeholder {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; height: 200px; gap: 12px;
  color: var(--muted); font-size: 15px;
}
.pd-placeholder-icon { font-size: 32px; animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.pd-section { margin-bottom: var(--space-base); }
.pd-section-label {
  display: block; font-size: 11px; font-weight: 600;
  letter-spacing: 0.5px; text-transform: uppercase;
  color: var(--muted); margin-bottom: 4px;
}
.pd-script-title {
  font-family: var(--font-display); font-size: 18px; font-weight: 300;
  color: var(--ink); letter-spacing: -0.3px;
}
.pd-script-desc { font-size: 13px; color: var(--body); line-height: 1.6; }

/* Characters */
.pd-characters { display: flex; flex-wrap: wrap; gap: 6px; }
.pd-char-chip {
  display: flex; align-items: center; gap: 6px;
  background: var(--canvas-soft); border: 1px solid var(--hairline);
  border-radius: var(--r-md); padding: 5px 10px;
}
.pd-char-avatar {
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--surface-strong); color: var(--ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
}
.pd-char-info { display: flex; flex-direction: column; }
.pd-char-name { font-size: 12px; font-weight: 600; color: var(--ink); }
.pd-char-role { font-size: 10px; color: var(--muted); }

/* Lines */
.pd-lines { display: flex; flex-direction: column; gap: 2px; }
.pd-line {
  display: flex; align-items: center; gap: 6px;
  padding: 4px 8px; border-radius: var(--r-sm);
  background: var(--canvas-soft); font-size: 12px;
  animation: lineIn 0.25s ease;
}
@keyframes lineIn { from { opacity: 0; transform: translateY(3px); } }
.pd-line-speaker { font-weight: 600; color: var(--ink); min-width: 40px; flex-shrink: 0; }
.pd-line-text { flex: 1; color: var(--body); line-height: 1.4; }
.pd-line-status { font-size: 12px; flex-shrink: 0; width: 18px; text-align: center; }
.pd-line-spin {
  display: inline-block; width: 10px; height: 10px;
  border: 2px solid var(--hairline-strong);
  border-top-color: var(--ink-primary); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.pd-error {
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: var(--r-lg); padding: var(--space-sm) var(--space-base);
  margin-top: var(--space-base); font-size: 13px; color: var(--semantic-error);
}

/* Transition */
.fade-up-enter-active { transition: all 0.35s ease; }
.fade-up-enter-from { opacity: 0; transform: translateY(8px); }
</style>
