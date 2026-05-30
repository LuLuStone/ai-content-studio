<template>
  <div class="page" v-loading="loading">
    <div class="page-nav">
      <el-button @click="$router.push('/video')" :icon="ArrowLeft" text>返回列表</el-button>
      <el-popconfirm title="确定删除？" @confirm="handleDelete">
        <template #reference><el-button :icon="Delete">删除</el-button></template>
      </el-popconfirm>
    </div>

    <template v-if="detail">
      <section class="detail-hero">
        <div class="hero-orb hero-orb-rose"></div>
        <h1 class="detail-title">{{ detail.title }}</h1>
        <div class="detail-meta">
          <span class="badge-pill">{{ detail.style || '--' }}</span>
          <span class="badge-pill">{{ formatDuration(detail.duration_seconds) }}</span>
        </div>
      </section>

      <div v-if="detail.video_file_path" class="player-card">
        <video controls style="width: 100%; border-radius: var(--r-md)" :src="`/api/videos/${detail.id}/video`" />
      </div>
      <div v-else class="info-card">
        <span class="info-icon">🎬</span>
        <span>视频文件生成中，当前仅展示分镜脚本</span>
      </div>

      <!-- Storyboard -->
      <section class="script-section">
        <h2 class="section-title">分镜脚本</h2>
        <div class="scene-grid">
          <div v-for="scene in detail.script_json?.scenes" :key="scene.scene_number" class="scene-card">
            <div class="scene-header">
              <span class="scene-num">场景 {{ scene.scene_number }}</span>
              <span class="scene-duration">{{ scene.duration }}秒</span>
              <span class="scene-transition">{{ scene.transition }}</span>
            </div>
            <p class="scene-visual">{{ scene.visual_description }}</p>
            <p class="scene-narration"><strong>旁白：</strong>{{ scene.narration }}</p>
            <p class="scene-subtitle"><strong>字幕：</strong>{{ scene.subtitle }}</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getVideo, deleteVideo, type VideoDetail } from '../api/video'

const route = useRoute()
const router = useRouter()
const detail = ref<VideoDetail | null>(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try { detail.value = await getVideo(route.params.id as string) }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
})

async function handleDelete() {
  try { await deleteVideo(route.params.id as string); ElMessage.success('删除成功'); router.push('/video') }
  catch { ElMessage.error('删除失败') }
}

function formatDuration(s?: number) {
  if (!s) return '--'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}
</script>

<style scoped>
.page-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xl); }

.detail-hero { position: relative; margin-bottom: var(--space-xl); padding: var(--space-xl) 0; }
.hero-orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.3; pointer-events: none; }
.hero-orb-rose { width: 250px; height: 250px; background: var(--gradient-rose); top: -40px; right: -40px; }
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
  overflow: hidden;
}

.info-card {
  display: flex; align-items: center; gap: var(--space-sm);
  background: var(--canvas-soft); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-lg);
  margin-bottom: var(--space-xl); font-size: 14px; color: var(--muted);
}
.info-icon { font-size: 20px; }

.section-title { font-family: var(--font-display); font-size: 24px; font-weight: 300; color: var(--ink); margin-bottom: var(--space-lg); }
.script-section { margin-bottom: var(--space-xl); }

.scene-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-base); }
.scene-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-lg);
}
.scene-header { display: flex; align-items: center; gap: 8px; margin-bottom: var(--space-sm); }
.scene-num { font-weight: 600; font-size: 14px; color: var(--ink); }
.scene-duration { font-size: 13px; color: var(--muted); }
.scene-transition {
  font-size: 11px; color: var(--muted); background: var(--surface-strong);
  padding: 1px 8px; border-radius: var(--r-pill); font-weight: 500;
}
.scene-visual {
  font-size: 14px; color: var(--body); background: var(--canvas-soft);
  padding: var(--space-sm) var(--space-base); border-radius: var(--r-md);
  margin-bottom: var(--space-sm); line-height: 1.5;
}
.scene-narration, .scene-subtitle { font-size: 13px; color: var(--body); margin-bottom: 4px; line-height: 1.5; }
.scene-narration strong, .scene-subtitle strong { color: var(--ink); font-weight: 600; }
</style>
