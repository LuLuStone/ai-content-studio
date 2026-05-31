<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">🎙️ 播客</h2>
      <el-button type="primary" @click="$router.push('/')">新建播客</el-button>
    </div>

    <div class="card-grid" v-loading="loading">
      <div v-for="item in list" :key="item.id" class="content-card" @click="$router.push(`/podcast/${item.id}`)">
        <div class="card-top">
          <span class="card-icon">🎙️</span>
          <span class="badge-pill">{{ item.speaker_count || '-' }}人</span>
        </div>
        <h3 class="card-title">{{ item.title }}</h3>
        <div class="card-meta">
          <span>{{ item.style || '--' }}</span>
          <span>{{ formatDuration(item.duration_seconds) }}</span>
        </div>
        <div class="card-footer">
          <span class="card-time">{{ new Date(item.created_at).toLocaleDateString() }}</span>
          <div class="card-actions">
            <el-button link type="primary" size="small" @click.stop="$router.push(`/podcast/${item.id}`)">查看</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(item.id)">
              <template #reference><el-button link type="danger" size="small" @click.stop>删除</el-button></template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && list.length === 0" description="暂无播客" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getPodcasts, deletePodcast, type PodcastListItem } from '../api/podcast'
import gsap from 'gsap'

const list = ref<PodcastListItem[]>([])
const loading = ref(false)

onMounted(() => fetchList())

async function fetchList() {
  loading.value = true
  try {
    list.value = await getPodcasts()
    nextTick(() => {
      const cards = document.querySelectorAll('.content-card')
      if (cards.length) gsap.fromTo(cards, { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, stagger: 0.06, ease: 'power2.out' })
    })
  }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

async function handleDelete(id: string) {
  try { await deletePodcast(id); ElMessage.success('删除成功'); fetchList() }
  catch { ElMessage.error('删除失败') }
}

function formatDuration(s?: number) {
  if (!s) return '--'
  return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xl); }
.page-title { font-family: var(--font-display); font-size: 28px; font-weight: 300; color: var(--ink); }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-base); }
.content-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-lg);
  cursor: pointer; transition: all 0.2s ease;
}
.content-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.card-icon { font-size: 24px; }
.card-title { font-size: 16px; font-weight: 600; color: var(--ink); margin-bottom: 6px; line-height: 1.4; }
.card-meta { display: flex; gap: var(--space-sm); font-size: 13px; color: var(--muted); margin-bottom: var(--space-base); }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: var(--space-sm); border-top: 1px solid var(--hairline-soft); }
.card-time { font-size: 13px; color: var(--muted-soft); }
.card-actions { display: flex; gap: 4px; }
.badge-pill {
  display: inline-flex; align-items: center;
  background: var(--surface-strong); color: var(--ink);
  font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  padding: 3px 8px; border-radius: var(--r-pill);
}
</style>
