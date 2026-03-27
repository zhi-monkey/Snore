<template>
  <div class="topbar">
    <div class="topbar-left">
      <h1 class="topbar-title">{{ title }}</h1>
      <p v-if="subtitle" class="topbar-subtitle">{{ subtitle }}</p>
    </div>
    <div class="topbar-right">
      <div class="topbar-date">{{ dateStr }}</div>
      <div class="topbar-notifications">
        <button class="notif-btn" title="通知">
          🔔
          <span class="notif-badge">3</span>
        </button>
      </div>
      <div class="topbar-user">
        <div class="user-avatar-sm">王</div>
        <span>王医生</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()

const now = new Date()
const dateStr = now.toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  background: var(--card-bg);
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: var(--shadow);
}
.topbar-title    { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.topbar-subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.topbar-right    { display: flex; align-items: center; gap: 16px; }
.topbar-date     { font-size: 13px; color: var(--text-secondary); }

.notif-btn {
  position: relative;
  background: none; border: none;
  font-size: 20px; cursor: pointer; padding: 4px; line-height: 1;
}
.notif-badge {
  position: absolute; top: -2px; right: -4px;
  background: var(--danger); color: #fff;
  font-size: 10px; font-weight: 700;
  width: 16px; height: 16px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.topbar-user {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 500; color: var(--text-primary);
}
.user-avatar-sm {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600;
}
</style>
