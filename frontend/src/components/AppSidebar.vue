<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          <path d="M15 9a3 3 0 0 1-3 3"/>
        </svg>
      </div>
      <div>
        <div class="logo-name">SnoringCare</div>
        <div class="logo-sub">睡眠健康管理系统</div>
      </div>
    </div>

    <!-- Search -->
    <div class="sidebar-search">
      <svg class="s-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
  <input type="text" placeholder="搜索..." v-model="searchQuery" />
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
  <div class="nav-section-label">主菜单</div>
      <component
        v-for="item in mainNav"
        :key="item.path"
        :is="item.path ? 'RouterLink' : 'div'"
        :to="item.path || undefined"
        class="nav-item"
        :exact-active-class="item.path === '/' ? 'nav-item--active' : ''"
        :active-class="item.path && item.path !== '/' ? 'nav-item--active' : ''"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
      </component>

  <div class="nav-section-label" style="margin-top:16px">系统</div>
      <div class="nav-item nav-settings">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </span>
  <span class="nav-label">设置</span>
      </div>
    </nav>

    <!-- User Footer -->
    <div class="sidebar-footer">
      <div class="user-card">
        <div class="user-avatar">王</div>
        <div class="user-meta">
          <div class="user-name">王明医生</div>
          <div class="user-role">主治医师</div>
        </div>
        <svg class="user-more" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>
        </svg>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const searchQuery = ref('')

const mainNav = [
  {
    path: '/',
    label: '数据看板',
    badge: null,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>`,
  },
  {
    path: '/records',
    label: '患者管理',
    badge: '6',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>`,
  },
  {
    path: '/upload',
    label: '睡眠检测',
    badge: null,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>`,
  },
  {
    path: '/reports',
    label: '检测报告',
    badge: '3',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>`,
  },
  {
    path: '/search',
    label: '健康搜索',
    badge: null,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
    </svg>`,
  },
]
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0; top: 0;
  width: 260px;
  height: 100vh;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  z-index: 100;
  box-shadow: 2px 0 20px rgba(0,0,0,0.15);
  overflow-y: auto;
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.logo-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  background: var(--primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-icon svg { width: 22px; height: 22px; color: #fff; }
.logo-name { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 0.3px; }
.logo-sub  { font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 1px; letter-spacing: 0.3px; }

/* Search */
.sidebar-search {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 14px 16px 6px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.07);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.s-icon { width: 15px; height: 15px; color: rgba(255,255,255,0.4); flex-shrink: 0; }
.sidebar-search input {
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255,255,255,0.8);
  font-size: 13px;
  width: 100%;
  font-family: inherit;
}
.sidebar-search input::placeholder { color: rgba(255,255,255,0.3); }

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.nav-section-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255,255,255,0.25);
  letter-spacing: 0.8px;
  padding: 8px 8px 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  cursor: pointer;
}
.nav-item:hover { background: var(--sidebar-hover); color: rgba(255,255,255,0.9); }
.nav-item--active { background: var(--primary); color: #fff !important; }
.nav-item--active .nav-icon svg { color: #fff; }
.nav-settings { opacity: 0.7; }

.nav-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-icon svg { width: 16px; height: 16px; }
.nav-label { flex: 1; }
.nav-badge {
  background: var(--danger);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 5px;
}

/* Footer */
.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  width: 34px; height: 34px;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  flex-shrink: 0;
}
.user-meta { flex: 1; min-width: 0; }
.user-name { font-size: 13px; font-weight: 600; color: #fff; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 1px; }
.user-more { width: 16px; height: 16px; color: rgba(255,255,255,0.3); cursor: pointer; flex-shrink: 0; }
</style>
