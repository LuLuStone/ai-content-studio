<template>
  <div class="page">
    <div class="page-nav">
      <el-button @click="$router.push('/')" :icon="ArrowLeft" text>返回首页</el-button>
    </div>

    <h1 class="page-title">全部创作</h1>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button :class="['filter-tab', { active: filterType === '' }]" @click="filterType = ''; fetchList()">全部</button>
        <button :class="['filter-tab', { active: filterType === 'podcast' }]" @click="filterType = 'podcast'; fetchList()">🎙️ 播客</button>
        <button :class="['filter-tab', { active: filterType === 'audiobook' }]" @click="filterType = 'audiobook'; fetchList()">📖 有声书</button>
        <button :class="['filter-tab', { active: filterType === 'video' }]" @click="filterType = 'video'; fetchList()">🎬 视频</button>
        <button :class="['filter-tab', { active: filterType === 'image' }]" @click="filterType = 'image'; fetchList()">🖼️ 图片</button>
      </div>
      <el-input
        v-model="keyword"
        placeholder="搜索标题..."
        :prefix-icon="Search"
        clearable
        style="width: 240px"
        @input="handleSearch"
      />
    </div>

    <!-- Active Tasks -->
    <div v-if="activeTasks.length > 0" class="active-tasks">
      <div v-for="task in activeTasks" :key="task.task_id" class="active-task-item">
        <span class="at-icon">{{ getTypeIcon(task.type) }}</span>
        <div class="at-info">
          <span class="at-label">{{ getTypeLabel(task.type) }} · 生成中</span>
          <el-progress :percentage="task.progress" :show-text="false" :stroke-width="3" :color="'var(--ink-primary)'" style="flex:1" />
        </div>
        <span class="at-pct">{{ task.progress }}%</span>
        <el-button v-if="task.status === 'completed'" type="primary" size="small" text @click="goToTaskResult(task)">查看</el-button>
      </div>
    </div>

    <!-- List -->
    <div class="creation-list" v-loading="loading">
      <div v-for="item in items" :key="item.id" class="creation-row" @click="goToDetail(item)">
        <span class="row-icon">{{ getTypeIcon(item._type) }}</span>
        <div class="row-info">
          <span class="row-title">{{ item.title }}</span>
          <span class="row-meta">
            <template v-if="item._type === 'podcast'">{{ item.speaker_count || '-' }}人 · {{ item.style }}</template>
            <template v-else-if="item._type === 'audiobook'">{{ item.mode === 'multi' ? '多角色' : '单角色' }}</template>
            <template v-else>{{ item.style || '--' }}</template>
          </span>
        </div>
        <span class="badge-pill badge-sm">{{ getTypeLabel(item._type) }}</span>
        <span class="row-time">{{ new Date(item.created_at).toLocaleDateString() }}</span>
        <div class="row-actions">
          <el-popconfirm title="确定删除？" @confirm="handleDelete(item)">
            <template #reference><el-button link type="danger" size="small" @click.stop>删除</el-button></template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && items.length === 0" description="暂无创作" />

    <!-- Pagination -->
    <div class="pagination-bar" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getAllCreations, type CreationItem } from '../api/create'
import { getActiveTasks, type TaskStatus } from '../api/task'
import { deletePodcast } from '../api/podcast'
import { deleteAudiobook } from '../api/audiobook'
import { deleteVideo } from '../api/video'
import { deleteImage } from '../api/image'

const router = useRouter()
const items = ref<CreationItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterType = ref('')
const keyword = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null
const activeTasks = ref<TaskStatus[]>([])

onMounted(() => { fetchList(); loadActiveTasks() })

async function loadActiveTasks() {
  try {
    activeTasks.value = await getActiveTasks()
    if (activeTasks.value.length > 0) {
      const timer = setInterval(async () => {
        activeTasks.value = await getActiveTasks()
        if (activeTasks.value.length === 0) { clearInterval(timer); fetchList() }
      }, 3000)
    }
  } catch {}
}

function goToTaskResult(task: TaskStatus) {
  if (!task.result_id) return
  const m: Record<string, string> = { podcast: '/podcast/', audiobook: '/audiobook/', video: '/video/', image: '/image/' }
  router.push((m[task.type] || '/') + task.result_id)
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getAllCreations({ page: currentPage.value, page_size: pageSize.value, type: filterType.value, keyword: keyword.value })
    items.value = res.items
    total.value = res.total
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { currentPage.value = 1; fetchList() }, 300)
}

function getTypeLabel(t: string) { return { podcast: '播客', audiobook: '有声书', video: '视频', image: '图片' }[t] || t }
function getTypeIcon(t: string) { return { podcast: '🎙️', audiobook: '📖', video: '🎬', image: '🖼️' }[t] || '📄' }

function goToDetail(row: CreationItem) {
  const m: Record<string, string> = { podcast: `/podcast/${row.id}`, audiobook: `/audiobook/${row.id}`, video: `/video/${row.id}`, image: `/image/${row.id}` }
  router.push(m[row._type] || '/')
}

async function handleDelete(row: CreationItem) {
  try {
    const dm: Record<string, (id: string) => Promise<any>> = { podcast: deletePodcast, audiobook: deleteAudiobook, video: deleteVideo, image: deleteImage }
    await dm[row._type](row.id)
    ElMessage.success('删除成功'); fetchList()
  } catch { ElMessage.error('删除失败') }
}
</script>

<style scoped>
.page-nav { margin-bottom: var(--space-lg); }
.page-title {
  font-family: var(--font-display); font-size: 32px; font-weight: 300;
  color: var(--ink); margin-bottom: var(--space-xl);
}

/* Filter */
.filter-bar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--space-lg); flex-wrap: wrap; gap: var(--space-sm);
}
.filter-tabs { display: flex; gap: 2px; }
.filter-tab {
  padding: 8px 16px; border-radius: var(--r-pill); border: none;
  background: transparent; font-size: 14px; font-weight: 500;
  color: var(--muted); cursor: pointer; transition: all 0.15s;
  font-family: var(--font-body);
}
.filter-tab:hover { color: var(--ink); background: var(--hairline-soft); }
.filter-tab.active { color: var(--ink); background: var(--surface-strong); font-weight: 600; }

/* Active Tasks */
.active-tasks { margin-bottom: var(--space-lg); }
.active-task-item {
  display: flex; align-items: center; gap: var(--space-base);
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-base) var(--space-lg);
  margin-bottom: var(--space-xs);
}
.at-icon { font-size: 20px; }
.at-info { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.at-label { font-size: 14px; font-weight: 500; color: var(--ink); }
.at-pct { font-size: 13px; color: var(--muted); min-width: 40px; text-align: right; }

/* List */
.creation-list {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); overflow: hidden;
}
.creation-row {
  display: flex; align-items: center; gap: var(--space-base);
  padding: 14px var(--space-lg); cursor: pointer;
  transition: background 0.15s; border-bottom: 1px solid var(--hairline-soft);
}
.creation-row:last-child { border-bottom: none; }
.creation-row:hover { background: var(--canvas-soft); }
.row-icon { font-size: 20px; flex-shrink: 0; }
.row-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.row-title { font-size: 15px; font-weight: 500; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-meta { font-size: 13px; color: var(--muted); }
.row-time { font-size: 13px; color: var(--muted-soft); min-width: 80px; text-align: right; }
.row-actions { flex-shrink: 0; }

.badge-pill {
  display: inline-flex; align-items: center;
  background: var(--surface-strong); color: var(--ink);
  font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  padding: 3px 8px; border-radius: var(--r-pill);
}

.pagination-bar { display: flex; justify-content: flex-end; margin-top: var(--space-lg); }
</style>
