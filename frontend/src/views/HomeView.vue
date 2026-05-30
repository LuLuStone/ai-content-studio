<template>
  <div class="home">
    <!-- Hero Section with gradient orb -->
    <section class="hero">
      <div class="hero-orb hero-orb-mint"></div>
      <div class="hero-orb hero-orb-peach"></div>
      <h1 class="hero-title">AI 全能创作</h1>
      <p class="hero-subtitle">输入一段文字，生成播客、有声书、视频、图片</p>
    </section>

    <!-- Input Section -->
    <div class="input-card">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="4"
        placeholder="输入你想创作的内容，例如：帮我生成一段关于人工智能未来发展的播客对话……"
        resize="none"
        class="main-input"
      />
      <div class="input-footer">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          @change="handleFileUpload"
          accept=".txt,.md,.docx"
        >
          <el-button :icon="Upload" text size="small">上传文件</el-button>
        </el-upload>
        <span v-if="uploadedFileName" class="file-tag">
          {{ uploadedFileName }}
          <el-icon class="file-remove" @click="uploadedFileName = ''; inputText = ''"><Close /></el-icon>
        </span>
      </div>
    </div>

    <!-- Type Selection Cards -->
    <div class="type-grid">
      <div
        v-for="item in typeOptions"
        :key="item.type"
        :class="['type-card', { active: selectedType === item.type }]"
        @click="selectType(item.type)"
      >
        <span class="type-icon">{{ item.icon }}</span>
        <span class="type-name">{{ item.name }}</span>
        <span class="type-desc">{{ item.desc }}</span>
      </div>
    </div>

    <!-- Config Panel -->
    <transition name="fade">
      <div v-if="selectedType" class="config-card">
        <!-- Podcast -->
        <template v-if="selectedType === 'podcast'">
          <div class="config-row">
            <label class="config-label">人数</label>
            <el-segmented v-model="podcastConfig.speaker_count" :options="[2, 3, 4]" />
          </div>
          <div class="config-row">
            <label class="config-label">风格</label>
            <el-select v-model="podcastConfig.style" size="default">
              <el-option label="轻松闲聊" value="轻松闲聊" />
              <el-option label="深度访谈" value="深度访谈" />
              <el-option label="新闻播报" value="新闻播报" />
              <el-option label="故事讲述" value="故事讲述" />
            </el-select>
          </div>
          <div class="config-row">
            <label class="config-label">音色</label>
            <div class="voice-grid">
              <div v-for="(voice, role) in podcastConfig.voices" :key="role" class="voice-pair">
                <span class="voice-role">{{ role }}</span>
                <el-select v-model="podcastConfig.voices[role]" size="small" style="width:140px">
                  <el-option v-for="v in voiceOptions" :key="v.id" :label="v.label" :value="v.id" />
                  <template v-if="customVoices.length > 0">
                    <el-option disabled value="---" label="── 自定义音色 ──" />
                    <el-option v-for="cv in customVoices" :key="'custom:'+cv.id" :label="cv.name" :value="'custom:'+cv.id" />
                  </template>
                </el-select>
              </div>
            </div>
          </div>
        </template>

        <!-- Audiobook -->
        <template v-if="selectedType === 'audiobook'">
          <div class="config-row">
            <label class="config-label">模式</label>
            <el-segmented v-model="audiobookConfig.mode" :options="[{label:'单角色',value:'single'},{label:'多角色',value:'multi'}]" />
          </div>
          <div class="config-row" v-if="audiobookConfig.mode === 'single'">
            <label class="config-label">音色</label>
            <el-select v-model="audiobookConfig.voice_id" size="default">
              <el-option v-for="v in voiceOptions" :key="v.id" :label="v.label" :value="v.id" />
              <template v-if="customVoices.length > 0">
                <el-option disabled value="---" label="── 自定义音色 ──" />
                <el-option v-for="cv in customVoices" :key="'custom:'+cv.id" :label="cv.name" :value="'custom:'+cv.id" />
              </template>
            </el-select>
          </div>
          <div class="config-row">
            <label class="config-label">风格</label>
            <el-select v-model="audiobookConfig.style" size="default">
              <el-option label="自然" value="自然" />
              <el-option label="有感情" value="有感情" />
              <el-option label="播音腔" value="播音腔" />
            </el-select>
          </div>
        </template>

        <!-- Video -->
        <template v-if="selectedType === 'video'">
          <div class="config-row">
            <label class="config-label">风格</label>
            <el-select v-model="videoConfig.style" size="default">
              <el-option label="科技感" value="科技感" />
              <el-option label="温暖治愈" value="温暖治愈" />
              <el-option label="搞笑幽默" value="搞笑幽默" />
              <el-option label="纪录片" value="纪录片" />
              <el-option label="电影感" value="电影感" />
            </el-select>
          </div>
          <div class="config-row">
            <label class="config-label">时长</label>
            <el-slider v-model="videoConfig.duration" :min="5" :max="120" :step="5" show-input style="flex:1" />
          </div>
        </template>

        <!-- Image -->
        <template v-if="selectedType === 'image'">
          <div class="config-row">
            <label class="config-label">风格</label>
            <el-select v-model="imageConfig.style" size="default">
              <el-option label="写实" value="写实" />
              <el-option label="动漫" value="动漫" />
              <el-option label="油画" value="油画" />
              <el-option label="赛博朋克" value="赛博朋克" />
              <el-option label="水彩" value="水彩" />
            </el-select>
          </div>
          <div class="config-row">
            <label class="config-label">比例</label>
            <el-segmented v-model="imageConfig.aspect_ratio" :options="['1:1','4:3','16:9','9:16']" />
          </div>
        </template>

        <div class="config-action">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="!inputText.trim()"
            @click="handleSubmit"
          >
            开始创作
          </el-button>
        </div>
      </div>
    </transition>

    <!-- Task Progress -->
    <transition name="fade">
      <div v-if="currentTask" class="task-card">
        <div class="task-top">
          <span class="task-label">{{ getTaskTypeLabel(currentTask.type) }} · {{ getStatusLabel(currentTask.status) }}</span>
          <span class="badge-pill">{{ currentTask.progress }}%</span>
        </div>
        <div class="task-bar">
          <div class="task-bar-fill" :style="{ width: currentTask.progress + '%' }"></div>
        </div>
        <p v-if="currentTask.error_message" class="task-error">{{ currentTask.error_message }}</p>
        <div class="task-bottom">
          <el-button v-if="currentTask.status === 'completed'" type="primary" size="small" @click="goToResult">查看结果</el-button>
          <el-button v-if="currentTask.status !== 'completed'" size="small" @click="showProgressDialog = true">查看进度</el-button>
          <el-button v-if="currentTask.status === 'failed'" size="small" text @click="currentTask = null">关闭</el-button>
        </div>
      </div>
    </transition>

    <!-- Recent Creations -->
    <section v-if="recentItems.length > 0" class="recent-section">
      <div class="section-header">
        <h2 class="section-title">最近创作</h2>
        <el-button text type="primary" size="small" @click="$router.push('/creations')">查看全部</el-button>
      </div>
      <div class="recent-list">
        <div
          v-for="item in recentItems"
          :key="item.id"
          class="recent-item"
          @click="goToDetail(item)"
        >
          <span class="ri-icon">{{ getTypeIcon(item._type) }}</span>
          <div class="ri-info">
            <span class="ri-title">{{ item.title }}</span>
            <span class="ri-time">{{ formatTime(item.created_at) }}</span>
          </div>
          <span class="badge-pill badge-sm">{{ getTypeLabel(item._type) }}</span>
        </div>
      </div>
    </section>

    <!-- Progress Dialog -->
    <TaskProgressDialog
      :visible="showProgressDialog"
      :type="currentTask?.type || ''"
      :progress="currentTask?.progress || 0"
      :step-data="currentTask?.step_data || null"
      :error="currentTask?.error_message"
      :result-id="currentTask?.result_id"
      @close="showProgressDialog = false"
      @done="onProgressDialogDone"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createContent } from '../api/create'
import { getTaskStatus, getActiveTasks, type TaskStatus } from '../api/task'
import { getPodcasts } from '../api/podcast'
import { getAudiobooks } from '../api/audiobook'
import { getVideos } from '../api/video'
import { getImages } from '../api/image'
import { getVoices, type VoiceItem } from '../api/voice'
import TaskProgressDialog from '../components/TaskProgressDialog.vue'

const router = useRouter()
const inputText = ref('')
const uploadedFileName = ref('')
const selectedType = ref('')
const submitting = ref(false)
const currentTask = ref<TaskStatus | null>(null)
const showProgressDialog = ref(false)
const recentItems = ref<any[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => { fetchRecent(); restoreActiveTask(); loadCustomVoices() })
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })

async function restoreActiveTask() {
  try {
    const tasks = await getActiveTasks()
    if (tasks.length > 0) {
      currentTask.value = tasks[0]
      startPolling(tasks[0].task_id)
    }
  } catch {}
}

async function fetchRecent() {
  try {
    const [p, a, v, i] = await Promise.all([
      getPodcasts(1, 5).catch(() => []),
      getAudiobooks(1, 5).catch(() => []),
      getVideos(1, 5).catch(() => []),
      getImages(1, 5).catch(() => []),
    ])
    const all = [
      ...p.map((x: any) => ({ ...x, _type: 'podcast' })),
      ...a.map((x: any) => ({ ...x, _type: 'audiobook' })),
      ...v.map((x: any) => ({ ...x, _type: 'video' })),
      ...i.map((x: any) => ({ ...x, _type: 'image' })),
    ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    recentItems.value = all.slice(0, 10)
  } catch {}
}

function getTypeIcon(t: string) { return { podcast: '🎙️', audiobook: '📖', video: '🎬', image: '🖼️' }[t] || '📄' }
function getTypeLabel(t: string) { return { podcast: '播客', audiobook: '有声书', video: '视频', image: '图片' }[t] || t }

function formatTime(t: string) {
  const diff = Date.now() - new Date(t).getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  return new Date(t).toLocaleDateString()
}

function goToDetail(item: any) {
  const m: Record<string, string> = { podcast: '/podcast/', audiobook: '/audiobook/', video: '/video/', image: '/image/' }
  router.push((m[item._type] || '/') + item.id)
}

const typeOptions = [
  { type: 'podcast', icon: '🎙️', name: '播客', desc: '多人对话音频' },
  { type: 'audiobook', icon: '📖', name: '有声书', desc: '多角色朗读' },
  { type: 'video', icon: '🎬', name: '视频', desc: 'AI 生成视频' },
  { type: 'image', icon: '🖼️', name: '图片', desc: 'AI 生成图片' },
]

const voiceOptions = [
  { id: '冰糖', label: '冰糖 · 女声甜美' },
  { id: '茉莉', label: '茉莉 · 女声稳重' },
  { id: '苏打', label: '苏打 · 男声活力' },
  { id: '白桦', label: '白桦 · 男声磁性' },
]
const customVoices = ref<VoiceItem[]>([])

// Load custom voices
async function loadCustomVoices() {
  try { customVoices.value = await getVoices() } catch {}
}

const podcastConfig = reactive({
  speaker_count: 2 as number,
  style: '轻松闲聊',
  voices: { '主持人': '冰糖', '嘉宾': '苏打', '嘉宾A': '苏打', '嘉宾B': '茉莉', '嘉宾C': '白桦' } as Record<string, string>,
})
const audiobookConfig = reactive({ mode: 'single', voice_id: '冰糖', style: '自然' })
const videoConfig = reactive({ style: '科技感', duration: 30 })
const imageConfig = reactive({ style: '写实', aspect_ratio: '16:9' })

function selectType(type: string) {
  selectedType.value = type
  if (type === 'podcast') updatePodcastVoices()
}

function updatePodcastVoices() {
  const n = podcastConfig.speaker_count
  podcastConfig.voices = n === 2
    ? { '主持人': '冰糖', '嘉宾': '苏打' }
    : n === 3
      ? { '主持人': '冰糖', '嘉宾A': '苏打', '嘉宾B': '茉莉' }
      : { '主持人': '冰糖', '嘉宾A': '苏打', '嘉宾B': '茉莉', '嘉宾C': '白桦' }
}

watch(() => podcastConfig.speaker_count, () => {
  if (selectedType.value === 'podcast') updatePodcastVoices()
})

function handleFileUpload(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => { inputText.value = e.target?.result as string; uploadedFileName.value = file.name }
  reader.readAsText(file.raw)
}

async function handleSubmit() {
  if (!inputText.value.trim()) return ElMessage.warning('请输入创作内容')
  submitting.value = true
  try {
    const opts: Record<string, any> = { podcast: { ...podcastConfig }, audiobook: { ...audiobookConfig }, video: { ...videoConfig }, image: { ...imageConfig } }
    const res = await createContent({ input_text: inputText.value, type: selectedType.value as any, options: opts[selectedType.value] || {} })
    currentTask.value = { task_id: res.task_id, type: selectedType.value, status: 'pending', progress: 0 }
    startPolling(res.task_id)
  } catch (e: any) { ElMessage.error(e.message || '提交失败') }
  finally { submitting.value = false }
}

function startPolling(taskId: string) {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const s = await getTaskStatus(taskId)
      currentTask.value = s
      if (s.status === 'completed' || s.status === 'failed') {
        clearInterval(pollTimer!)
        if (s.status === 'completed') { ElMessage.success('创作完成！'); fetchRecent() }
      }
    } catch {}
  }, 2000)
}

function onProgressDialogDone(resultId: string) {
  const taskType = currentTask.value?.type || ''
  showProgressDialog.value = false
  currentTask.value = null
  const m: Record<string, string> = { podcast: '/podcast/', audiobook: '/audiobook/', video: '/video/', image: '/image/' }
  router.push((m[taskType] || '/') + resultId)
  fetchRecent()
}

function goToResult() {
  if (!currentTask.value?.result_id) return
  const m: Record<string, string> = { podcast: '/podcast/', audiobook: '/audiobook/', video: '/video/', image: '/image/' }
  router.push((m[currentTask.value.type] || '/') + currentTask.value.result_id)
  showProgressDialog.value = false
  currentTask.value = null
}

function getTaskTypeLabel(t: string) { return { podcast: '播客', audiobook: '有声书', video: '视频', image: '图片' }[t] || t }
function getStatusLabel(s: string) { return { pending: '排队中', processing: '生成中', completed: '已完成', failed: '失败' }[s] || s }
</script>

<style scoped>
.home {
  max-width: 720px;
  margin: 0 auto;
  padding: var(--space-xl) 0 var(--space-section);
}

/* ===== Hero ===== */
.hero {
  text-align: center;
  margin-bottom: var(--space-xxl);
  position: relative;
  padding: var(--space-xl) 0;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  pointer-events: none;
}
.hero-orb-mint {
  width: 300px; height: 300px;
  background: var(--gradient-mint);
  top: -60px; left: -80px;
}
.hero-orb-peach {
  width: 250px; height: 250px;
  background: var(--gradient-peach);
  top: -40px; right: -60px;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 300;
  color: var(--ink);
  letter-spacing: -1.5px;
  line-height: 1.05;
  position: relative;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--muted);
  margin-top: var(--space-sm);
  letter-spacing: 0.16px;
  position: relative;
}

/* ===== Input Card ===== */
.input-card {
  background: var(--surface-card);
  border-radius: var(--r-xl);
  border: 1px solid var(--hairline);
  overflow: hidden;
  margin-bottom: var(--space-lg);
  transition: border-color 0.2s;
}
.input-card:focus-within { border-color: var(--hairline-strong); }
.main-input :deep(.el-textarea__inner) {
  border: none !important;
  box-shadow: none !important;
  padding: var(--space-base) var(--space-lg);
  font-size: 15px;
  font-family: var(--font-body);
  background: transparent;
}
.input-footer {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-top: 1px solid var(--hairline-soft);
}
.file-tag {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 12px; color: var(--semantic-success); background: #e8ffea;
  padding: 2px 10px; border-radius: var(--r-pill);
}
.file-remove { cursor: pointer; font-size: 12px; }
.file-remove:hover { color: var(--semantic-error); }

/* ===== Type Grid ===== */
.type-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: var(--space-lg) var(--space-base);
  border-radius: var(--r-xl);
  background: var(--surface-card);
  border: 1px solid var(--hairline);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.type-card:hover {
  border-color: var(--hairline-strong);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.type-card.active {
  border-color: var(--ink-primary);
  background: var(--canvas-soft);
}
.type-icon { font-size: 28px; }
.type-name { font-size: 15px; font-weight: 600; color: var(--ink); }
.type-desc { font-size: 13px; color: var(--muted); }

/* ===== Config Card ===== */
.config-card {
  background: var(--surface-card);
  border-radius: var(--r-xl);
  border: 1px solid var(--hairline);
  padding: var(--space-xl);
  margin-bottom: var(--space-lg);
}
.config-row {
  display: flex; align-items: center; gap: var(--space-base);
  margin-bottom: var(--space-base);
}
.config-row:last-of-type { margin-bottom: 0; }
.config-label {
  min-width: 48px; font-size: 14px; font-weight: 500;
  color: var(--muted); text-align: right; letter-spacing: 0.14px;
}
.voice-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.voice-pair { display: flex; align-items: center; gap: 8px; }
.voice-role { font-size: 14px; color: var(--body); min-width: 52px; font-weight: 500; }
.config-action {
  text-align: center; margin-top: var(--space-lg);
  padding-top: var(--space-base); border-top: 1px solid var(--hairline-soft);
}

/* ===== Task Card ===== */
.task-card {
  background: var(--surface-card);
  border-radius: var(--r-xl);
  border: 1px solid var(--hairline);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}
.task-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.task-label { font-size: 15px; font-weight: 600; color: var(--ink); }
.task-error { font-size: 13px; color: var(--semantic-error); margin: 8px 0 0; }
.task-bottom { margin-top: var(--space-sm); text-align: right; }
.task-bar {
  height: 4px; background: var(--hairline-soft);
  border-radius: 2px; overflow: hidden;
}
.task-bar-fill {
  height: 100%; border-radius: 2px;
  background: var(--ink-primary);
  transition: width 0.5s ease;
}

/* ===== Badge ===== */
.badge-pill {
  display: inline-flex; align-items: center;
  background: var(--surface-strong); color: var(--ink);
  font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
  padding: 4px 10px; border-radius: var(--r-pill);
  text-transform: uppercase;
}
.badge-sm { font-size: 11px; padding: 3px 8px; }

/* ===== Recent Section ===== */
.recent-section { margin-top: var(--space-xl); }
.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-base);
}
.section-title {
  font-family: var(--font-display);
  font-size: 24px; font-weight: 300; color: var(--ink);
  letter-spacing: 0;
}
.recent-list {
  background: var(--surface-card);
  border-radius: var(--r-xl);
  border: 1px solid var(--hairline);
  overflow: hidden;
}
.recent-item {
  display: flex; align-items: center; gap: var(--space-base);
  padding: 14px var(--space-lg);
  cursor: pointer; transition: background 0.15s;
  border-bottom: 1px solid var(--hairline-soft);
}
.recent-item:last-child { border-bottom: none; }
.recent-item:hover { background: var(--canvas-soft); }
.ri-icon { font-size: 20px; flex-shrink: 0; }
.ri-info { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ri-title { font-size: 15px; font-weight: 500; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ri-time { font-size: 13px; color: var(--muted-soft); }

/* ===== Animation ===== */
.fade-enter-active, .fade-leave-active { transition: all 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* ===== Responsive ===== */
@media (max-width: 640px) {
  .hero-title { font-size: 36px; }
  .type-grid { grid-template-columns: repeat(2, 1fr); }
  .hero-orb { opacity: 0.25; }
}
</style>
