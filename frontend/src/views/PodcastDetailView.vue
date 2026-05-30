<template>
  <div class="page" v-loading="loading">
    <div class="page-nav">
      <el-button @click="$router.push('/podcast')" :icon="ArrowLeft" text>返回列表</el-button>
      <div class="page-nav-actions">
        <el-button type="primary" :icon="Download" @click="handleDownload">下载 MP3</el-button>
        <el-popconfirm title="确定删除？" @confirm="handleDelete">
          <template #reference><el-button :icon="Delete">删除</el-button></template>
        </el-popconfirm>
      </div>
    </div>

    <template v-if="detail">
      <!-- Hero -->
      <section class="detail-hero">
        <div class="hero-orb hero-orb-lavender"></div>
        <h1 class="detail-title">{{ detail.title }}</h1>
        <div class="detail-meta">
          <span class="badge-pill">{{ formatDuration(detail.duration_seconds) }}</span>
          <span class="badge-pill">{{ detail.speaker_count }}人对话</span>
          <span class="badge-pill">{{ detail.style || '--' }}</span>
        </div>
        <p v-if="detail.description" class="detail-desc">{{ detail.description }}</p>
      </section>

      <!-- Player -->
      <div class="player-card">
        <audio ref="audioRef" controls style="width: 100%" :src="audioUrl" />
      </div>

      <!-- Script -->
      <section class="script-section">
        <h2 class="section-title">播客脚本</h2>
        <div class="script-list">
          <div
            v-for="(line, i) in detail.script_json?.script"
            :key="i"
            class="script-line"
          >
            <div class="line-avatar">{{ line.speaker?.[0] }}</div>
            <div class="line-body">
              <div class="line-header">
                <span class="line-speaker">{{ line.speaker }}</span>
                <span class="line-role">{{ line.role }}</span>
                <span class="line-emotion">{{ line.emotion }}</span>
              </div>
              <p class="line-text">{{ line.text }}</p>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getPodcast, deletePodcast, getPodcastAudioUrl, type PodcastDetail } from '../api/podcast'

const route = useRoute()
const router = useRouter()
const detail = ref<PodcastDetail | null>(null)
const loading = ref(false)
const audioRef = ref<HTMLAudioElement>()

const audioUrl = computed(() => detail.value ? getPodcastAudioUrl(detail.value.id) : '')

onMounted(() => fetchDetail())
onUnmounted(() => { if (audioRef.value) { audioRef.value.pause(); audioRef.value.currentTime = 0 } })

async function fetchDetail() {
  loading.value = true
  try { detail.value = await getPodcast(route.params.id as string) }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function handleDownload() {
  if (audioUrl.value) {
    const a = document.createElement('a')
    a.href = audioUrl.value
    a.download = `${detail.value?.title || 'podcast'}.mp3`
    a.click()
  }
}

async function handleDelete() {
  try { await deletePodcast(route.params.id as string); ElMessage.success('删除成功'); router.push('/podcast') }
  catch { ElMessage.error('删除失败') }
}

function formatDuration(seconds?: number) {
  if (!seconds) return '--'
  return `${Math.floor(seconds / 60)}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`
}
</script>

<style scoped>
.page-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xl); }
.page-nav-actions { display: flex; gap: 8px; }

/* Hero */
.detail-hero { position: relative; margin-bottom: var(--space-xl); padding: var(--space-xl) 0; }
.hero-orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.3; pointer-events: none; }
.hero-orb-lavender { width: 250px; height: 250px; background: var(--gradient-lavender); top: -40px; right: -40px; }
.detail-title {
  font-family: var(--font-display); font-size: 40px; font-weight: 300;
  color: var(--ink); letter-spacing: -0.8px; line-height: 1.1; position: relative;
}
.detail-meta { display: flex; gap: 8px; margin-top: var(--space-base); flex-wrap: wrap; position: relative; }
.detail-desc { font-size: 15px; color: var(--body); margin-top: var(--space-sm); line-height: 1.6; position: relative; }

/* Badge */
.badge-pill {
  display: inline-flex; align-items: center;
  background: var(--surface-strong); color: var(--ink);
  font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
  padding: 4px 12px; border-radius: var(--r-pill);
}

/* Player */
.player-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-lg);
  margin-bottom: var(--space-xl);
}
.player-card audio { border-radius: var(--r-md); }

/* Script */
.section-title {
  font-family: var(--font-display); font-size: 24px; font-weight: 300;
  color: var(--ink); margin-bottom: var(--space-lg);
}
.script-list { display: flex; flex-direction: column; gap: var(--space-sm); }
.script-line {
  display: flex; gap: var(--space-base);
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-base) var(--space-lg);
}
.line-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--surface-strong); color: var(--ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; flex-shrink: 0;
}
.line-body { flex: 1; min-width: 0; }
.line-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.line-speaker { font-weight: 600; font-size: 14px; color: var(--ink); }
.line-role { font-size: 12px; color: var(--muted-soft); }
.line-emotion {
  font-size: 11px; color: var(--muted); background: var(--surface-strong);
  padding: 1px 8px; border-radius: var(--r-pill); font-weight: 500;
}
.line-text { font-size: 15px; color: var(--body); line-height: 1.6; }
</style>
