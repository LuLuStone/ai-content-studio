<template>
  <div class="page">
    <div class="page-header">
      <h1 class="page-title">音色管理</h1>
      <el-button type="primary" @click="showAddDialog = true">添加音色</el-button>
    </div>

    <!-- System Preset Voices -->
    <section class="section">
      <h2 class="section-title">系统音色</h2>
      <div class="voice-list" v-loading="loadingPresets">
        <div v-for="v in presetVoices" :key="'preset-'+v.id" class="voice-row">
          <div class="voice-main">
            <span class="voice-badge badge-preset">系统</span>
            <div class="voice-info">
              <span class="voice-name">{{ presetCustomNames[v.id] || v.name }}</span>
              <span class="voice-desc">{{ v.description }}</span>
            </div>
          </div>
          <div class="voice-actions">
            <el-button
              size="small"
              :loading="previewingId === 'preset:'+v.id"
              @click="handlePresetPreview(v)"
            >
              {{ previewingId === 'preset:'+v.id ? '生成中...' : v.has_preview ? '播放' : '试听' }}
            </el-button>
            <el-button v-if="v.has_preview" size="small" text :loading="previewingId === 'preset:'+v.id" @click="handlePresetPreview(v, true)">重新生成</el-button>
            <el-button size="small" text @click="openRename('preset', v.id, presetCustomNames[v.id] || v.name)">改名</el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Custom Voices -->
    <section class="section">
      <h2 class="section-title">自定义音色</h2>
      <div class="voice-list" v-loading="loadingCustom">
        <div v-for="v in customVoices" :key="v.id" class="voice-row">
          <div class="voice-main">
            <span class="voice-badge badge-custom">自定义</span>
            <div class="voice-info">
              <span class="voice-name">{{ v.name }}</span>
              <span class="voice-desc">{{ v.description || '无描述' }}</span>
            </div>
          </div>
          <div class="voice-actions">
            <el-button
              size="small"
              :loading="previewingId === v.id"
              @click="handleCustomPreview(v, false)"
            >
              {{ previewingId === v.id ? '生成中...' : v.preview_file_path ? '播放' : '试听' }}
            </el-button>
            <el-button v-if="v.preview_file_path" size="small" text :loading="previewingId === v.id" @click="handleCustomPreview(v, true)">重新生成</el-button>
            <el-button size="small" text @click="playSample(v)">播放样本</el-button>
            <el-button size="small" text @click="openRename('custom', v.id, v.name, v.description || '')">改名</el-button>
            <el-popconfirm title="确定删除该音色？删除后不可恢复。" @confirm="handleDelete(v.id)">
              <template #reference><el-button size="small" type="danger" text>删除</el-button></template>
            </el-popconfirm>
          </div>
        </div>
        <el-empty v-if="!loadingCustom && customVoices.length === 0" description="暂无自定义音色，点击右上角添加" />
      </div>
    </section>

    <!-- Add Voice Dialog -->
    <el-dialog v-model="showAddDialog" title="添加自定义音色" width="480px" @closed="resetForm">
      <div class="add-form">
        <div class="form-row">
          <label class="form-label">音色名称</label>
          <el-input v-model="addForm.name" placeholder="例如：我的声音" maxlength="50" />
        </div>
        <div class="form-row">
          <label class="form-label">描述</label>
          <el-input v-model="addForm.description" placeholder="可选，描述音色特点" maxlength="200" />
        </div>
        <div class="form-row">
          <label class="form-label">音频样本</label>
          <div class="upload-area" @click="triggerUpload" @drop.prevent="onDrop" @dragover.prevent>
            <input ref="fileInput" type="file" accept=".mp3,.wav" hidden @change="onFileChange" />
            <template v-if="!addForm.file">
              <span class="upload-icon">📁</span>
              <span class="upload-text">点击或拖拽上传</span>
              <span class="upload-hint">mp3 / wav，10-30 秒清晰单人音频，≤ 10MB</span>
            </template>
            <template v-else>
              <span class="upload-icon">🎵</span>
              <span class="upload-text">{{ addForm.file.name }}</span>
              <span class="upload-hint">{{ formatFileSize(addForm.file.size) }}</span>
            </template>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="!addForm.name || !addForm.file" @click="handleUpload">
          上传并保存
        </el-button>
      </template>
    </el-dialog>

    <!-- Rename Dialog -->
    <el-dialog v-model="showRenameDialog" title="重命名" width="400px">
      <div class="add-form">
        <div class="form-row">
          <label class="form-label">名称</label>
          <el-input v-model="renameForm.name" maxlength="50" />
        </div>
      </div>
      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" :loading="renaming" :disabled="!renameForm.name" @click="handleRename">保存</el-button>
      </template>
    </el-dialog>

    <!-- Audio Player -->
    <audio ref="audioRef" :src="playerSrc" @ended="playingId = null" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getPresetVoices, previewPresetVoice, getPresetAudioUrl,
  getVoices, createVoice, renameVoice, previewVoice, getVoiceSampleUrl, deleteVoice,
  type PresetVoice, type VoiceItem,
} from '../api/voice'

// ===== State =====
const presetVoices = ref<PresetVoice[]>([])
const customVoices = ref<VoiceItem[]>([])
const loadingPresets = ref(false)
const loadingCustom = ref(false)
const uploading = ref(false)
const renaming = ref(false)
const previewingId = ref<string | null>(null)
const playingId = ref<string | null>(null)

const showAddDialog = ref(false)
const showRenameDialog = ref(false)

const addForm = reactive({ name: '', description: '', file: null as File | null })
const renameForm = reactive({ type: '', id: '', name: '', description: '' })
const fileInput = ref<HTMLInputElement>()
const audioRef = ref<HTMLAudioElement>()
const playerSrc = ref('')

// Preset custom names from localStorage
const presetCustomNames = ref<Record<string, string>>({})

// ===== Init =====
onMounted(() => {
  const saved = localStorage.getItem('preset_voice_names')
  if (saved) presetCustomNames.value = JSON.parse(saved)
  fetchPresets()
  fetchCustom()
})

onUnmounted(() => {
  stopAudio()
})

function stopAudio() {
  if (audioRef.value) {
    audioRef.value.pause()
    audioRef.value.currentTime = 0
  }
  playerSrc.value = ''
  playingId.value = null
}

// ===== Fetch =====
async function fetchPresets() {
  loadingPresets.value = true
  try { presetVoices.value = await getPresetVoices() }
  catch { ElMessage.error('加载预置音色失败') }
  finally { loadingPresets.value = false }
}

async function fetchCustom() {
  loadingCustom.value = true
  try { customVoices.value = await getVoices() }
  catch { ElMessage.error('加载自定义音色失败') }
  finally { loadingCustom.value = false }
}

// ===== Preview =====
function playAudio(url: string, id: string) {
  playerSrc.value = url
  playingId.value = id
  setTimeout(() => audioRef.value?.play(), 100)
}

async function handlePresetPreview(v: PresetVoice, force = false) {
  const id = 'preset:' + v.id
  previewingId.value = id
  try {
    if (!force && v.has_preview) {
      // 直接播放缓存
      playAudio(getPresetAudioUrl(v.id), id)
    } else {
      // 调 API 生成
      const blob = await previewPresetVoice(v.id, force)
      playAudio(URL.createObjectURL(blob), id)
      fetchPresets() // 刷新 has_preview 状态
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '试听失败')
  } finally {
    previewingId.value = null
  }
}

async function handleCustomPreview(v: VoiceItem, force = false) {
  previewingId.value = v.id
  try {
    if (!force && v.preview_file_path) {
      // 直接播放缓存 - 需要获取文件 URL
      const blob = await previewVoice(v.id, false)
      playAudio(URL.createObjectURL(blob), v.id)
    } else {
      const blob = await previewVoice(v.id, force)
      playAudio(URL.createObjectURL(blob), v.id)
      fetchCustom()
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '试听失败')
  } finally {
    previewingId.value = null
  }
}

function playSample(v: VoiceItem) {
  playAudio(getVoiceSampleUrl(v.id), 'sample:' + v.id)
}

// ===== Add Voice =====
function triggerUpload() { fileInput.value?.click() }
function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) addForm.file = input.files[0]
}
function onDrop(e: DragEvent) {
  const file = e.dataTransfer?.files[0]
  if (file && (file.name.endsWith('.mp3') || file.name.endsWith('.wav'))) addForm.file = file
  else ElMessage.warning('仅支持 mp3 和 wav 格式')
}
function resetForm() { addForm.name = ''; addForm.description = ''; addForm.file = null }

async function handleUpload() {
  if (!addForm.name || !addForm.file) return
  uploading.value = true
  try {
    await createVoice(addForm.name, addForm.description, addForm.file)
    ElMessage.success('音色创建成功')
    showAddDialog.value = false
    fetchCustom()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// ===== Rename =====
function openRename(type: string, id: string, name: string, description = '') {
  renameForm.type = type
  renameForm.id = id
  renameForm.name = name
  renameForm.description = description
  showRenameDialog.value = true
}

async function handleRename() {
  if (!renameForm.name) return
  renaming.value = true
  try {
    if (renameForm.type === 'preset') {
      // Preset names stored in localStorage
      presetCustomNames.value[renameForm.id] = renameForm.name
      localStorage.setItem('preset_voice_names', JSON.stringify(presetCustomNames.value))
      ElMessage.success('已重命名')
    } else {
      await renameVoice(renameForm.id, renameForm.name)
      ElMessage.success('已重命名')
      fetchCustom()
    }
    showRenameDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '重命名失败')
  } finally {
    renaming.value = false
  }
}

// ===== Delete =====
async function handleDelete(id: string) {
  try { await deleteVoice(id); ElMessage.success('删除成功'); fetchCustom() }
  catch { ElMessage.error('删除失败') }
}

// ===== Utils =====
function formatFileSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.page { max-width: 800px; margin: 0 auto; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-xl);
}
.page-title {
  font-family: var(--font-display); font-size: 32px; font-weight: 300;
  color: var(--ink);
}

/* Sections */
.section { margin-bottom: var(--space-xl); }
.section-title {
  font-size: 14px; font-weight: 600; letter-spacing: 0.5px;
  text-transform: uppercase; color: var(--muted);
  margin-bottom: var(--space-base);
}

/* Voice List */
.voice-list {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); overflow: hidden;
}
.voice-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px var(--space-lg);
  border-bottom: 1px solid var(--hairline-soft);
  transition: background 0.15s;
}
.voice-row:last-child { border-bottom: none; }
.voice-row:hover { background: var(--canvas-soft); }
.voice-main { display: flex; align-items: center; gap: var(--space-sm); flex: 1; min-width: 0; }
.voice-badge {
  font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  padding: 2px 8px; border-radius: var(--r-pill); flex-shrink: 0;
}
.badge-preset { background: var(--surface-strong); color: var(--muted); }
.badge-custom { background: var(--gradient-mint); color: var(--ink); }
.voice-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.voice-name { font-size: 15px; font-weight: 600; color: var(--ink); }
.voice-desc { font-size: 13px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.voice-actions { display: flex; gap: 4px; flex-shrink: 0; }

/* Dialog Form */
.add-form { display: flex; flex-direction: column; gap: var(--space-base); }
.form-row { display: flex; align-items: center; gap: var(--space-base); }
.form-label { min-width: 72px; font-size: 14px; font-weight: 500; color: var(--muted); text-align: right; }
.upload-area {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: var(--space-xl); border: 2px dashed var(--hairline);
  border-radius: var(--r-lg); cursor: pointer; transition: all 0.2s;
  background: var(--canvas-soft);
}
.upload-area:hover { border-color: var(--hairline-strong); background: var(--surface-card); }
.upload-icon { font-size: 28px; }
.upload-text { font-size: 14px; font-weight: 500; color: var(--ink); }
.upload-hint { font-size: 12px; color: var(--muted-soft); }
</style>
