<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">🖼️ 图片</h2>
      <el-button type="primary" @click="$router.push('/')">新建图片</el-button>
    </div>

    <div class="image-grid" v-loading="loading">
      <div v-for="img in list" :key="img.id" class="image-card" @click="$router.push(`/image/${img.id}`)">
        <div class="image-preview">
          <img v-if="img.image_file_path" :src="`/api/images/${img.id}/file`" :alt="img.title" />
          <div v-else class="placeholder">
            <span class="placeholder-icon">🖼️</span>
            <span class="placeholder-text">待生成</span>
          </div>
        </div>
        <div class="image-info">
          <span class="image-title">{{ img.title }}</span>
          <span class="image-style">{{ img.style || '--' }}</span>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && list.length === 0" description="暂无图片" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getImages, type ImageListItem } from '../api/image'

const list = ref<ImageListItem[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try { list.value = await getImages() }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-xl); }
.page-title { font-family: var(--font-display); font-size: 28px; font-weight: 300; color: var(--ink); }

.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-base); }
.image-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); overflow: hidden;
  cursor: pointer; transition: all 0.2s ease;
}
.image-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.image-preview {
  height: 180px; overflow: hidden; background: var(--canvas-soft);
  display: flex; align-items: center; justify-content: center;
}
.image-preview img { width: 100%; height: 100%; object-fit: cover; }
.placeholder { text-align: center; color: var(--muted-soft); }
.placeholder-icon { font-size: 32px; display: block; margin-bottom: 4px; }
.placeholder-text { font-size: 13px; }
.image-info { padding: var(--space-base) var(--space-lg); }
.image-title { display: block; font-weight: 600; font-size: 15px; color: var(--ink); margin-bottom: 2px; }
.image-style { font-size: 13px; color: var(--muted); }
</style>
