<template>
  <div :class="['ap', { playing: isPlaying }]">
    <!-- Left: Play Button -->
    <button class="ap-play" @click="togglePlay" :aria-label="isPlaying ? '暂停' : '播放'">
      <svg viewBox="0 0 40 40" class="ap-play-svg">
        <circle cx="20" cy="20" r="19" class="ap-ring" />
        <path v-if="!isPlaying" d="M16 12 L30 20 L16 28 Z" class="ap-icon" />
        <template v-else>
          <rect x="14" y="12" width="4" height="16" rx="1" class="ap-icon" />
          <rect x="22" y="12" width="4" height="16" rx="1" class="ap-icon" />
        </template>
      </svg>
    </button>

    <!-- Center -->
    <div class="ap-body">
      <div class="ap-title" v-if="title">{{ title }}</div>

      <!-- Waveform -->
      <div class="ap-wave-wrap">
        <div class="ap-wave">
          <div
            v-for="i in barCount"
            :key="i"
            class="ap-bar"
            :ref="(el) => { if (el) barEls[i - 1] = el as HTMLElement }"
          />
        </div>
        <div class="ap-progress-mask" :style="{ width: progressPct + '%' }" />
      </div>

      <!-- Progress track -->
      <div class="ap-track" ref="trackRef" @click="onTrackClick">
        <div class="ap-track-fill" :style="{ width: progressPct + '%' }">
          <div class="ap-thumb" />
        </div>
      </div>

      <div class="ap-times">
        <span class="ap-time">{{ formatTime(currentTime) }}</span>
        <span class="ap-time">{{ formatTime(duration) }}</span>
      </div>
    </div>

    <audio
      ref="audioRef"
      :src="src"
      @loadedmetadata="onLoaded"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @play="isPlaying = true"
      @pause="isPlaying = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import gsap from 'gsap'

const props = defineProps<{ src: string; title?: string }>()

const audioRef = ref<HTMLAudioElement>()
const trackRef = ref<HTMLElement>()
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progressPct = ref(0)

const barCount = 60
const barEls: HTMLElement[] = []

// Web Audio API
let audioCtx: AudioContext | null = null
let analyser: AnalyserNode | null = null
let sourceNode: MediaElementAudioSourceNode | null = null
let dataArray: Uint8Array | null = null
let rafId = 0
let connected = false

// ===== Setup Web Audio =====
function ensureAudioContext() {
  if (audioCtx) return
  audioCtx = new AudioContext()
  analyser = audioCtx.createAnalyser()
  analyser.fftSize = 256  // 128 frequency bins, we use barCount of them
  analyser.smoothingTimeConstant = 0.55  // lower = more responsive peaks
  dataArray = new Uint8Array(analyser.frequencyBinCount)
}

function connectSource() {
  if (connected || !audioRef.value || !audioCtx || !analyser) return
  sourceNode = audioCtx.createMediaElementSource(audioRef.value)
  sourceNode.connect(analyser)
  analyser.connect(audioCtx.destination)
  connected = true
}

// ===== Playback =====
function togglePlay() {
  if (!audioRef.value) return
  ensureAudioContext()
  connectSource()

  if (audioCtx!.state === 'suspended') {
    audioCtx!.resume()
  }

  isPlaying.value ? audioRef.value.pause() : audioRef.value.play()
}

function onLoaded() {
  duration.value = audioRef.value?.duration || 0
  buildStaticWaveform()
}

function onTimeUpdate() {
  if (!audioRef.value) return
  currentTime.value = audioRef.value.currentTime
  progressPct.value = duration.value ? (currentTime.value / duration.value) * 100 : 0
}

function onEnded() {
  isPlaying.value = false
}

// ===== Seek =====
function onTrackClick(e: MouseEvent) {
  if (!trackRef.value || !audioRef.value || !duration.value) return
  const rect = trackRef.value.getBoundingClientRect()
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  audioRef.value.currentTime = pct * duration.value
}

// ===== Static waveform (when not playing) =====
function buildStaticWaveform() {
  const seed = (props.src?.length || 0) + barCount
  for (let i = 0; i < barCount; i++) {
    const el = barEls[i]
    if (!el) continue
    const center = barCount / 2
    const dist = Math.abs(i - center) / center
    const base = 0.25 + 0.75 * (1 - dist * 0.6)
    const noise = Math.sin(i * 0.7 + seed) * 0.15 + Math.cos(i * 1.4 + seed * 1.7) * 0.1
    const h = Math.max(0.12, Math.min(1, base + noise))
    el.dataset.base = String(h)
    gsap.set(el, { scaleY: h })
  }
}

// ===== Real-time frequency visualization =====
function startVisualization() {
  if (!analyser || !dataArray) return

  const currentValues = new Float32Array(barCount)
  for (let i = 0; i < barCount; i++) {
    currentValues[i] = parseFloat(barEls[i]?.dataset.base || '0.15')
  }

  const binCount = analyser!.frequencyBinCount

  // Pre-compute logarithmic bin mapping for each bar
  // Low frequencies get more bins (where the detail matters)
  const barBins: Array<{ start: number; end: number }> = []
  for (let i = 0; i < barCount; i++) {
    // Log scale: map bar index → bin range
    const logStart = Math.pow(i / barCount, 1.5) * binCount
    const logEnd = Math.pow((i + 1) / barCount, 1.5) * binCount
    barBins.push({
      start: Math.floor(logStart),
      end: Math.min(Math.ceil(logEnd) + 1, binCount),
    })
  }

  // Pre-compute center distance for shape weighting
  const centerDist = new Float32Array(barCount)
  for (let i = 0; i < barCount; i++) {
    centerDist[i] = 1 - Math.abs(i - barCount / 2) / (barCount / 2) * 0.5
  }

  let runningFreqMax = 60
  let runningOverall = 30
  const decay = 0.993

  function draw() {
    if (!isPlaying.value || !analyser || !dataArray) return
    rafId = requestAnimationFrame(draw)

    analyser.getByteFrequencyData(dataArray)

    // Overall level (RMS-ish) — drives ALL bars
    let totalSum = 0
    let frameMax = 0
    for (let i = 0; i < binCount; i++) {
      totalSum += dataArray[i]
      if (dataArray[i] > frameMax) frameMax = dataArray[i]
    }
    const overallLevel = totalSum / binCount
    runningOverall = Math.max(runningOverall * decay, overallLevel, 15)
    runningFreqMax = Math.max(runningFreqMax * decay, frameMax, 20)

    // Normalized overall level (0-1)
    const overallNorm = Math.min(1, overallLevel / runningOverall)

    for (let i = 0; i < barCount; i++) {
      const el = barEls[i]
      if (!el) continue

      // Per-bar frequency peak
      const { start, end } = barBins[i]
      let peak = 0
      for (let j = start; j < end; j++) {
        if (dataArray[j] > peak) peak = dataArray[j]
      }
      const freqNorm = Math.min(1, peak / runningFreqMax)

      // Blend: 40% overall level + 60% frequency detail
      // This ensures high-frequency bars still move from overall level
      const blended = overallNorm * 0.4 + freqNorm * 0.6

      // Apply center shape and power curve
      const curved = Math.pow(blended, 0.55) * centerDist[i]
      const target = Math.max(0.06, Math.min(1, curved))

      // Lerp
      currentValues[i] += (target - currentValues[i]) * 0.45
      el.style.transform = `scaleY(${currentValues[i].toFixed(3)})`
    }
  }

  draw()
}

function stopVisualization() {
  if (rafId) { cancelAnimationFrame(rafId); rafId = 0 }
}

// ===== Idle breathing (when paused but loaded) =====
let idleRaf = 0
let idleStart = 0

function startIdleBreathing() {
  idleStart = performance.now()
  function breathe() {
    idleRaf = requestAnimationFrame(breathe)
    const t = (performance.now() - idleStart) / 1000
    for (let i = 0; i < barCount; i++) {
      const el = barEls[i]
      if (!el) continue
      const base = parseFloat(el.dataset.base || '0.3')
      // Each bar has a unique frequency and phase
      const phase = i * 0.15
      const freq = 0.4 + (i % 5) * 0.08
      const wave = Math.sin(t * freq * Math.PI * 2 + phase) * 0.12
      el.style.transform = `scaleY(${Math.max(0.06, base + wave).toFixed(3)})`
    }
  }
  breathe()
}

function stopIdleBreathing() {
  if (idleRaf) { cancelAnimationFrame(idleRaf); idleRaf = 0 }
  // Return to base
  barEls.forEach(el => {
    if (!el) return
    const base = parseFloat(el.dataset.base || '0.3')
    gsap.to(el, { scaleY: base, duration: 0.4, ease: 'power2.out', overwrite: true })
  })
}

// ===== Watch play state =====
watch(isPlaying, (playing) => {
  if (playing) {
    stopIdleBreathing()
    startVisualization()
    gsap.fromTo('.ap-play-svg', { scale: 0.9 }, { scale: 1, duration: 0.3, ease: 'back.out(2)' })
  } else {
    stopVisualization()
    startIdleBreathing()
  }
})

onMounted(() => {
  nextTick(() => {
    for (let i = 0; i < barCount; i++) {
      const el = barEls[i]
      if (el) gsap.set(el, { scaleY: 0.15 })
    }
    startIdleBreathing()
  })
})

onUnmounted(() => {
  stopVisualization()
  stopIdleBreathing()
  audioCtx?.close()
})

function formatTime(s: number) {
  if (!s || !isFinite(s)) return '0:00'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}

defineExpose({ audioRef })
</script>

<style scoped>
.ap {
  display: flex; align-items: center; gap: var(--space-base);
  background: var(--surface-card);
  border: 1px solid var(--hairline);
  border-radius: var(--r-xl);
  padding: var(--space-base) var(--space-lg);
  transition: border-color 0.3s, box-shadow 0.3s;
}
.ap.playing {
  border-color: var(--hairline-strong);
  box-shadow: 0 2px 20px rgba(0,0,0,0.04);
}

.ap-play {
  flex-shrink: 0; width: 44px; height: 44px;
  background: none; border: none; cursor: pointer;
  padding: 0; display: flex; align-items: center; justify-content: center;
}
.ap-play-svg { width: 44px; height: 44px; }
.ap-ring {
  fill: none; stroke: var(--hairline-strong); stroke-width: 1.5;
  transition: stroke 0.3s;
}
.ap.playing .ap-ring { stroke: var(--ink-primary); }
.ap-play:hover .ap-ring { stroke: var(--ink); }
.ap-icon { fill: var(--ink); }

.ap-body { flex: 1; min-width: 0; }
.ap-title {
  font-size: 13px; font-weight: 600; color: var(--ink);
  margin-bottom: 8px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
}

.ap-wave-wrap {
  position: relative; height: 36px;
  overflow: hidden; border-radius: var(--r-sm);
}
.ap-wave {
  display: flex; align-items: flex-end; gap: 2px;
  height: 100%; padding: 2px 0;
}
.ap-bar {
  flex: 1; min-width: 0;
  height: 100%;
  background: var(--hairline-strong);
  border-radius: 1px;
  transform-origin: bottom;
  will-change: transform;
  transition: background 0.2s;
}
.ap.playing .ap-bar { background: var(--ink-primary); }
.ap-progress-mask {
  position: absolute; top: 0; left: 0; bottom: 0;
  background: rgba(12, 10, 9, 0.05);
  pointer-events: none;
  transition: width 0.1s linear;
}

.ap-track {
  position: relative; height: 6px; margin-top: 8px;
  background: var(--hairline-soft);
  border-radius: 3px; cursor: pointer;
  overflow: visible;
}
.ap-track:hover { height: 8px; }
.ap-track-fill {
  height: 100%; border-radius: 3px;
  background: var(--ink-primary);
  position: relative;
  transition: width 0.1s linear;
}
.ap-thumb {
  position: absolute; right: -5px; top: 50%;
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--ink);
  transform: translateY(-50%) scale(0);
  transition: transform 0.15s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.ap-track:hover .ap-thumb,
.ap.playing .ap-thumb { transform: translateY(-50%) scale(1); }

.ap-times {
  display: flex; justify-content: space-between;
  margin-top: 6px;
}
.ap-time {
  font-size: 11px; font-weight: 500;
  color: var(--muted-soft); letter-spacing: 0.3px;
  font-variant-numeric: tabular-nums;
}
</style>
