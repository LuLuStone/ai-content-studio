<template>
  <div class="page settings">
    <h1 class="page-title">⚙️ 设置</h1>

    <div class="settings-card">
      <h3 class="card-title">API 配置</h3>
      <el-form label-width="120px" class="settings-form">
        <el-form-item label="MiMo API Key">
          <el-input v-model="settings.mimo_api_key" type="password" show-password placeholder="输入小米 MiMo API Key" />
        </el-form-item>
        <el-form-item label="MiMo Base URL">
          <el-input v-model="settings.mimo_base_url" placeholder="https://api.xiaomimimo.com/v1" />
        </el-form-item>
        <el-form-item label="火山引擎 AK">
          <el-input v-model="settings.volcengine_ak" type="password" show-password placeholder="输入火山引擎 Access Key" />
        </el-form-item>
        <el-form-item label="火山引擎 SK">
          <el-input v-model="settings.volcengine_sk" type="password" show-password placeholder="输入火山引擎 Secret Key" />
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-card">
      <h3 class="card-title">默认设置</h3>
      <el-form label-width="120px" class="settings-form">
        <el-form-item label="默认音色">
          <el-select v-model="settings.default_voice" style="width: 100%">
            <el-option label="冰糖（女声，甜美）" value="冰糖" />
            <el-option label="茉莉（女声，稳重）" value="茉莉" />
            <el-option label="苏打（男声，活力）" value="苏打" />
            <el-option label="白桦（男声，磁性）" value="白桦" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <div class="save-row">
      <el-button type="primary" @click="handleSave">保存设置</el-button>
    </div>

    <div class="info-note">
      <span class="info-icon">ℹ️</span>
      <span>设置保存在浏览器本地（localStorage）。如需修改后端 API Key，请直接编辑 <code>.env</code> 文件。</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const settings = reactive({
  mimo_api_key: '',
  mimo_base_url: 'https://api.xiaomimimo.com/v1',
  volcengine_ak: '',
  volcengine_sk: '',
  default_voice: '冰糖',
})

onMounted(() => {
  const saved = localStorage.getItem('ai_studio_settings')
  if (saved) Object.assign(settings, JSON.parse(saved))
})

function handleSave() {
  localStorage.setItem('ai_studio_settings', JSON.stringify(settings))
  ElMessage.success('设置已保存')
}
</script>

<style scoped>
.settings { max-width: 640px; margin: 0 auto; }
.page-title {
  font-family: var(--font-display); font-size: 32px; font-weight: 300;
  color: var(--ink); margin-bottom: var(--space-xl);
}
.settings-card {
  background: var(--surface-card); border: 1px solid var(--hairline);
  border-radius: var(--r-xl); padding: var(--space-xl);
  margin-bottom: var(--space-base);
}
.card-title {
  font-size: 16px; font-weight: 600; color: var(--ink);
  margin-bottom: var(--space-lg); padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--hairline-soft);
}
.settings-form :deep(.el-form-item__label) { color: var(--muted); font-weight: 500; }
.save-row { margin: var(--space-lg) 0; }
.info-note {
  display: flex; align-items: flex-start; gap: var(--space-sm);
  font-size: 13px; color: var(--muted); line-height: 1.5;
  background: var(--canvas-soft); border: 1px solid var(--hairline-soft);
  border-radius: var(--r-lg); padding: var(--space-base) var(--space-lg);
}
.info-note code {
  background: var(--surface-strong); padding: 1px 6px;
  border-radius: var(--r-sm); font-size: 12px;
}
</style>
