<template>
  <div class="topbar">
    <!-- Left: title + subtitle -->
    <div class="topbar-left">
      <h1 class="topbar-title">{{ title }}</h1>
      <p v-if="subtitle" class="topbar-subtitle">{{ subtitle }}</p>
    </div>

    <!-- Right: actions -->
    <div class="topbar-right">
      <!-- Date Range Filter -->
      <div class="date-filter">
        <button
          v-for="r in ranges"
          :key="r.value"
          :class="['range-btn', activeRange === r.value ? 'range-btn--active' : '']"
          @click="activeRange = r.value"
        >{{ r.label }}</button>
      </div>

      <!-- Divider -->
      <div class="topbar-divider"></div>

      <!-- PDF Export -->
      <button class="topbar-action-btn pdf-btn" title="Export PDF" @click="exportPdf">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="12" y1="18" x2="12" y2="12"/>
          <polyline points="9 15 12 18 15 15"/>
        </svg>
        <span>Export PDF</span>
      </button>

      <!-- Settings -->
      <button class="topbar-icon-btn" title="Settings">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>

      <!-- Notifications -->
      <button class="topbar-icon-btn notif-btn" title="Notifications">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span class="notif-badge">3</span>
      </button>

      <!-- User -->
      <div class="topbar-user">
        <div class="topbar-avatar">王</div>
        <div class="topbar-user-info">
          <div class="topbar-user-name">Dr. 王明</div>
          <div class="topbar-user-date">{{ dateStr }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ title: string; subtitle?: string }>()

const ranges = [
  { label: 'Last Night', value: 'night' },
  { label: 'Last Week',  value: 'week' },
  { label: 'Last Month', value: 'month' },
]
const activeRange = ref('night')

const now = new Date()
const dateStr = now.toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric',
})

// TODO: integrate a PDF generation library (e.g. jsPDF or server-side) to replace this placeholder
function exportPdf () {
  console.warn('[PDF Export] PDF generation is not yet implemented.')
  window.print()
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  background: var(--card-bg);
  padding: 14px 24px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.topbar-title    { font-size: 20px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.topbar-subtitle { font-size: 12px; color: var(--text-secondary); margin-top: 3px; }

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* Date filter */
.date-filter {
  display: flex;
  background: var(--bg);
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
  border: 1px solid var(--border);
}
.range-btn {
  padding: 5px 12px;
  border-radius: 6px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
  white-space: nowrap;
}
.range-btn:hover { color: var(--primary); }
.range-btn--active {
  background: var(--card-bg);
  color: var(--primary);
  font-weight: 600;
  box-shadow: var(--shadow);
}

.topbar-divider {
  width: 1px; height: 28px;
  background: var(--border);
  flex-shrink: 0;
}

/* PDF button */
.pdf-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: none;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  font-family: inherit;
}
.pdf-btn svg { width: 15px; height: 15px; }
.pdf-btn:hover { background: var(--primary-dark); }

/* Icon buttons */
.topbar-icon-btn {
  position: relative;
  width: 36px; height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}
.topbar-icon-btn svg { width: 17px; height: 17px; }
.topbar-icon-btn:hover { border-color: var(--primary); color: var(--primary); }

/* Notification badge */
.notif-badge {
  position: absolute; top: -5px; right: -5px;
  background: var(--danger); color: #fff;
  font-size: 9px; font-weight: 700;
  min-width: 16px; height: 16px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 3px;
  border: 2px solid var(--card-bg);
}

/* User */
.topbar-user {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer;
}
.topbar-avatar {
  width: 34px; height: 34px;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
  flex-shrink: 0;
}
.topbar-user-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.topbar-user-date { font-size: 11px; color: var(--text-secondary); }
</style>
