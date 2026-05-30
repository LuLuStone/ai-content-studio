<template>
  <div class="page" v-loading="loading">
    <div class="page-nav">
      <el-button @click="$router.push('/audiobook')" :icon="ArrowLeft" text>返回列表</el-button>
      <div class="page-nav-actions">
        <el-button type="primary" :icon="Download" @click="handleDownload">下载 MP3</el-button>
        <el-popconfirm title="确定删除？" @confirm="handleDelete">
          <template #reference><el-button :icon="Delete">删除</el-button></template>
        </el-popconfirm>
      </div>
    </div>

    <template v-if="detail">
      <section class="detail-hero">
        <div class="hero-orb hero-orb-sky"></div>
        <h1 class="detail-title">{{ detail.title }}</h1>
        <div class="detail-meta">
          <span class="badge-pill">{{ detail.mode === 'multi' ? '多角色' : '单角色' }}</span>
          <span class="badge-pill">{{ formatDuration(detail.duration_seconds) }}</span>
        </div>
      </section>

      <div class="player-card">
        <audio controls style="width: 100%" :src="`/api/audiobooks/${detail.id}/audio`" />
      </div>

      <!-- Characters -->
      <section class="script-section">
        <h2 class="section-title">角色列表</h2>
        <div class="char-list">
          <div v-for="c in detail.characters_json" :key="c.name" class="char-chip">
            <span class="char-avatar">{{ c.name?.[0] }}</span>
            <span class="char-name">{{ c.name }}</span>
            <span class="char-info">{{ c.gender === 'male' ? '男' : '女' }} · {{ c.age_group }}</span>
          </div>
        </div>
      </section>

      <!-- Script -->
      <section class="script-section">
        <h2 class="section-title">朗读脚本</h2>
        <div class="script-list">
          <div v-for="(seg, i) in detail.script_json?.segments" :key="i" class="script-line">
            <div class="line-avatar">{{ seg.character?.[0] }}</div>
            <div class="line-body">
              <div class="line-header">
                <span class="line-speaker">{{ seg.character }}</span>
                <span class="line-emotion">{{ seg.emotion }}</span>
              </div>
              <p class="line-text">{{ seg.text }}</p>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getAudiobook, deleteAudiobook, type AudiobookDetail } from '../api/audiobook'

const route = useRoute()
const router = useRouter()
const detail = ref<AudiobookDetail | null>(null)
const loading = ref(false)
const audioRef = ref<HTMLAudioElement>()

onMounted(async () => {
  loading.value = true
  try { detail.value = await getAudiobook(route.params.id as string) }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
})

onUnmounted(() => { if (audioRef.value) { audioRef.value.pause(); audioRef.value.currentTime = 0 } })

function handleDownload() {
  const a = document.createElement('a')
  a.href = `/api/audiobooks/${detail.value?.id}/audio`
  a.download = `${detail.value?.title || 'audiobook'}.mp3`
  a.click()
}

async function handleDelete() {
  try { await deleteAudiobook(route.params.id as string); ElMessage.success('删除成功'); router.push('/audiobook') }
  catch { ElMessage.error('删除失败') }
}

function formatDuration(s?: number) {
  if (!s) return '--'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}
</script>

<style scoped>
.page-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xl); }
.page-nav-actions { display: flex; gap: 8px; }

.detail-hero { position: relative; margin-bottom: var(--space-xl); padding: var(--space-xl) 0; }
.hero-orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.3; pointer-events: none; }
.hero-orb-sky { width: 250px; height: 250px; background: var(--gradient-sky); top: -40px; right: -40px; }
.detail-title { font-family: var(--font-display); font-size: 40px; font-weight: 300; color: var(--ink); letter-spacing: -0.8px; position: relative; }
.detail-meta { display: flex; gap: 8px; margin-top: var(--space-base); position: relative; }

.badge-pill {
  display: inline-flex; align-items: center;
  background: var(--surface-strong); color: var(--ink);
  font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
  padding: 4px 12px; border-radius: var(--r-pill);
}

.player-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-lg); margin-bottom: var(--space-xl);
}
.player-card audio { border-radius: var(--r-md); }

.section-title { font-family: var(--font-display); font-size: 24px; font-weight: 300; color: var(--ink); margin-bottom: var(--space-lg); }
.script-section { margin-bottom: var(--space-xl); }

.char-list { display: flex; flex-wrap: wrap; gap: var(--space-sm); }
.char-chip {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: 10px 16px;
}
.char-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--surface-strong); color: var(--ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600;
}
.char-name { font-weight: 600; font-size: 14px; color: var(--ink); }
.char-info { font-size: 13px; color: var(--muted); }

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
.line-emotion {
  font-size: 11px; color: var(--muted); background: var(--surface-strong);
  padding: 1px 8px; border-radius: var(--r-pill); font-weight: 500;
}
.line-text { font-size: 15px; color: var(--body); line-height: 1.6; }
</style>
