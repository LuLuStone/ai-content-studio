<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <header class="top-nav">
        <router-link to="/" class="logo">
          <span class="logo-mark">✦</span>
          <span class="logo-text">AI Studio</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/podcast" class="nav-link">播客</router-link>
          <router-link to="/audiobook" class="nav-link">有声书</router-link>
          <router-link to="/video" class="nav-link">视频</router-link>
          <router-link to="/image" class="nav-link">图片</router-link>
          <router-link to="/creations" class="nav-link">全部创作</router-link>
          <div class="nav-dropdown">
            <router-link to="/settings" class="nav-link nav-icon">
              <el-icon><Setting /></el-icon>
            </router-link>
            <div class="dropdown-menu">
              <router-link to="/voices" class="dropdown-item">
                <span class="dropdown-icon">🎙️</span>
                <span>音色管理</span>
              </router-link>
              <router-link to="/settings" class="dropdown-item">
                <span class="dropdown-icon">⚙️</span>
                <span>API 配置</span>
              </router-link>
            </div>
          </div>
        </nav>
      </header>
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { Setting } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
/* ===== ElevenLabs-inspired Design System ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=EB+Garamond:wght@300;400;500&display=swap');

:root {
  /* Colors */
  --ink: #0c0a09;
  --ink-primary: #292524;
  --ink-primary-active: #0c0a09;
  --body: #4e4e4e;
  --body-strong: #292524;
  --muted: #777169;
  --muted-soft: #a8a29e;
  --hairline: #e7e5e4;
  --hairline-soft: #f0efed;
  --hairline-strong: #d6d3d1;
  --canvas: #f5f5f5;
  --canvas-soft: #fafafa;
  --surface-card: #ffffff;
  --surface-strong: #f0efed;
  --on-primary: #ffffff;
  --gradient-mint: #a7e5d3;
  --gradient-peach: #f4c5a8;
  --gradient-lavender: #c8b8e0;
  --gradient-sky: #a8c8e8;
  --gradient-rose: #e8b8c4;
  --semantic-error: #dc2626;
  --semantic-success: #16a34a;

  /* Typography */
  --font-display: 'EB Garamond', 'Times New Roman', serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;

  /* Spacing */
  --space-xs: 8px;
  --space-sm: 12px;
  --space-base: 16px;
  --space-md: 20px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-xxl: 48px;
  --space-section: 96px;

  /* Radius */
  --r-sm: 6px;
  --r-md: 8px;
  --r-lg: 12px;
  --r-xl: 16px;
  --r-xxl: 24px;
  --r-pill: 9999px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-body);
  background: var(--canvas);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  font-size: 15px;
  line-height: 1.5;
  letter-spacing: 0.15px;
}

.app-container { min-height: 100vh; }

/* ===== Top Navigation ===== */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 var(--space-xl);
  background: var(--canvas);
  border-bottom: 1px solid var(--hairline);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--r-md);
  background: var(--ink);
  color: var(--on-primary);
  font-size: 16px;
  font-weight: 600;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 300;
  color: var(--ink);
  letter-spacing: -0.3px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
}

.nav-link {
  padding: 8px 14px;
  border-radius: var(--r-pill);
  font-size: 15px;
  font-weight: 500;
  color: var(--body);
  text-decoration: none;
  transition: all 0.15s ease;
  letter-spacing: 0.15px;
}

.nav-link:hover { color: var(--ink); background: var(--hairline-soft); }
.nav-link.router-link-active { color: var(--ink); font-weight: 600; }
.nav-icon { font-size: 18px; padding: 8px 10px; }

/* Dropdown */
.nav-dropdown { position: relative; }
.dropdown-menu {
  display: none;
  position: absolute; top: 100%; right: 0;
  min-width: 160px;
  background: var(--surface-card);
  border: 1px solid var(--hairline);
  border-radius: var(--r-lg);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  padding: 4px;
  z-index: 200;
  margin-top: 4px;
}
.nav-dropdown:hover .dropdown-menu { display: block; }
.dropdown-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px;
  border-radius: var(--r-md);
  font-size: 14px; font-weight: 500;
  color: var(--body);
  text-decoration: none;
  transition: all 0.15s;
}
.dropdown-item:hover { background: var(--canvas-soft); color: var(--ink); }
.dropdown-item.router-link-active { color: var(--ink); font-weight: 600; }
.dropdown-icon { font-size: 16px; }

/* ===== Main Content ===== */
.app-main {
  max-width: 1080px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
}

/* ===== Element Plus Overrides ===== */
.el-button--primary {
  background: var(--ink-primary) !important;
  border-color: var(--ink-primary) !important;
  border-radius: var(--r-pill) !important;
  font-weight: 500 !important;
  font-size: 15px !important;
  letter-spacing: 0 !important;
  height: 40px !important;
  padding: 0 20px !important;
}
.el-button--primary:hover {
  background: var(--ink-primary-active) !important;
  border-color: var(--ink-primary-active) !important;
}
.el-button--default {
  border-radius: var(--r-pill) !important;
  border-color: var(--hairline-strong) !important;
  color: var(--body) !important;
  font-weight: 500 !important;
  font-size: 15px !important;
}
.el-button--default:hover {
  border-color: var(--ink-primary) !important;
  color: var(--ink) !important;
}
.el-button--danger {
  border-radius: var(--r-pill) !important;
}
.el-button.is-link {
  border: none !important;
  border-radius: var(--r-sm) !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
}
.el-button.is-link:hover {
  color: var(--ink) !important;
}
.el-button.is-link.el-button--primary {
  color: var(--muted) !important;
  background: transparent !important;
}
.el-button.is-link.el-button--primary:hover {
  color: var(--ink) !important;
}
.el-button.is-link.el-button--danger {
  color: var(--muted-soft) !important;
}
.el-button.is-link.el-button--danger:hover {
  color: var(--semantic-error) !important;
}

.el-card {
  border-radius: var(--r-xl) !important;
  border: 1px solid var(--hairline) !important;
  box-shadow: none !important;
}
.el-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
}

.el-input__wrapper {
  border-radius: var(--r-md) !important;
}
.el-textarea__inner {
  border-radius: var(--r-md) !important;
}

.el-tag {
  border-radius: var(--r-pill) !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  letter-spacing: 0.5px !important;
}

.el-table {
  border-radius: var(--r-xl) !important;
  overflow: hidden;
}
.el-table th.el-table__cell {
  background: var(--canvas-soft) !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
}

.el-dialog {
  border-radius: var(--r-xxl) !important;
}

.el-segmented {
  border-radius: var(--r-pill) !important;
}
</style>
