<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="brand-icon">🫁</span>
      <div>
        <div class="brand-name">SnoringCare</div>
        <div class="brand-sub">睡眠健康管理平台</div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :exact-active-class="item.path === '/' ? 'nav-item--active' : ''"
        :active-class="item.path !== '/' ? 'nav-item--active' : ''"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">王</div>
        <div>
          <div class="user-name">王医生</div>
          <div class="user-role">主治医师</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
const navItems = [
  { path: '/',        label: '系统主页', icon: '🏠' },
  { path: '/upload',  label: '睡眠检测', icon: '🎙️' },
  { path: '/reports', label: '检测报告', icon: '📋' },
  { path: '/records', label: '病历管理', icon: '📁' },
  { path: '/search',  label: '健康搜索', icon: '🔍' },
]
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0; top: 0;
  width: 240px;
  height: 100vh;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  z-index: 100;
  box-shadow: 2px 0 12px rgba(0,0,0,0.15);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.brand-icon { font-size: 32px; line-height: 1; }
.brand-name { font-size: 18px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }
.brand-sub  { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 2px; }

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: 8px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}
.nav-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.nav-item--active {
  background: var(--sidebar-active);
  color: #fff;
  box-shadow: 0 2px 8px rgba(43,108,176,0.4);
}

.nav-icon  { font-size: 18px; width: 24px; text-align: center; }
.nav-label { font-size: 14px; }

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}
.user-name { font-size: 13px; font-weight: 600; color: #fff; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 1px; }
</style>
