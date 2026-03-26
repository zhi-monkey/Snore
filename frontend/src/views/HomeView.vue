<template>
  <div>
    <TopBar title="系统主页" subtitle="欢迎使用 SnoringCare 睡眠健康管理平台" />

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-card--blue">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">1,248</div>
          <div class="stat-label">总患者数</div>
          <div class="stat-trend trend-up">↑ 12% 本月</div>
        </div>
      </div>
      <div class="stat-card stat-card--teal">
        <div class="stat-icon">🎙️</div>
        <div class="stat-info">
          <div class="stat-value">86</div>
          <div class="stat-label">本月检测</div>
          <div class="stat-trend trend-up">↑ 8% 上月</div>
        </div>
      </div>
      <div class="stat-card stat-card--orange">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">23</div>
          <div class="stat-label">待处理报告</div>
          <div class="stat-trend trend-down">↓ 3 较昨日</div>
        </div>
      </div>
      <div class="stat-card stat-card--green">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">94.2%</div>
          <div class="stat-label">检测准确率</div>
          <div class="stat-trend trend-up">↑ 0.3%</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="card chart-card-wide">
        <div class="card-title">
          <span>📈</span> 近7日 AHI 指数 &amp; 血氧饱和度趋势
        </div>
        <div class="chart-wrap">
          <Line :data="lineData" :options="lineOptions" />
        </div>
      </div>
      <div class="card chart-card-narrow">
        <div class="card-title"><span>🍕</span> 患者病情分布</div>
        <div class="chart-wrap">
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <!-- Recent Patients -->
    <div class="card">
      <div class="card-title" style="justify-content:space-between">
        <span>📋 最近检测患者</span>
        <button class="btn btn-outline" @click="$router.push('/records')">查看全部</button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>患者ID</th><th>姓名</th><th>年龄</th>
            <th>AHI指数</th><th>严重程度</th><th>检测日期</th>
            <th>状态</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in recentPatients" :key="p.id">
            <td><code>{{ p.id }}</code></td>
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.age }}</td>
            <td>{{ p.ahi }}</td>
            <td><span :class="`badge ${levelBadge[p.level]}`">{{ p.level }}</span></td>
            <td>{{ p.date }}</td>
            <td><span :class="`badge ${statusBadge[p.status]}`">{{ p.status }}</span></td>
            <td>
              <button class="btn btn-primary" style="padding:4px 12px;font-size:12px"
                @click="$router.push('/reports')">查看报告</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <div class="card quick-action-card" @click="$router.push('/upload')">
        <div class="qa-icon qa-icon--blue">🎙️</div>
        <div class="qa-text">
          <div class="qa-title">新建检测</div>
          <div class="qa-desc">上传睡眠音频，开始分析</div>
        </div>
        <span class="qa-arrow">→</span>
      </div>
      <div class="card quick-action-card" @click="$router.push('/records')">
        <div class="qa-icon qa-icon--teal">📁</div>
        <div class="qa-text">
          <div class="qa-title">病历管理</div>
          <div class="qa-desc">查看和管理患者病历</div>
        </div>
        <span class="qa-arrow">→</span>
      </div>
      <div class="card quick-action-card" @click="$router.push('/search')">
        <div class="qa-icon qa-icon--green">🔍</div>
        <div class="qa-text">
          <div class="qa-title">健康搜索</div>
          <div class="qa-desc">查询健康知识与病情</div>
        </div>
        <span class="qa-arrow">→</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  ArcElement, Tooltip, Legend, Filler,
  type ChartOptions
} from 'chart.js'
import TopBar from '../components/TopBar.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement,
  ArcElement, Tooltip, Legend, Filler)

const recentPatients = [
  { id: 'P001', name: '张三', age: 45, ahi: 22.5, level: '中度', date: '2026-03-25', status: '待复查' },
  { id: 'P002', name: '李四', age: 52, ahi: 5.2,  level: '正常', date: '2026-03-24', status: '已完成' },
  { id: 'P003', name: '王五', age: 38, ahi: 38.1, level: '重度', date: '2026-03-24', status: '治疗中' },
  { id: 'P004', name: '赵六', age: 61, ahi: 12.7, level: '轻度', date: '2026-03-23', status: '已完成' },
  { id: 'P005', name: '陈七', age: 29, ahi: 3.1,  level: '正常', date: '2026-03-22', status: '已完成' },
]

const statusBadge: Record<string, string> = {
  '待复查': 'badge-warning', '已完成': 'badge-success', '治疗中': 'badge-info',
}
const levelBadge: Record<string, string> = {
  '正常': 'badge-success', '轻度': 'badge-info', '中度': 'badge-warning', '重度': 'badge-danger',
}

const lineData = {
  labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  datasets: [
    {
      label: 'AHI指数',
      data: [12, 8, 15, 6, 10, 18, 7],
      borderColor: '#2b6cb0',
      backgroundColor: 'rgba(43,108,176,0.15)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
    },
    {
      label: '血氧饱和度%',
      data: [94, 96, 92, 97, 95, 91, 96],
      borderColor: '#38b2ac',
      backgroundColor: 'rgba(56,178,172,0.15)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
    },
  ],
}

const lineOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top' }, tooltip: { mode: 'index' } },
  scales: { y: { beginAtZero: true } },
}

const doughnutData = {
  labels: ['正常', '轻度', '中度', '重度'],
  datasets: [{
    data: [45, 30, 15, 10],
    backgroundColor: ['#38a169', '#38b2ac', '#dd6b20', '#e53e3e'],
    borderWidth: 2,
    borderColor: '#fff',
  }],
}

const doughnutOptions: ChartOptions<'doughnut'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}人` } } },
  cutout: '60%',
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow);
  border-left: 4px solid transparent;
}
.stat-card--blue   { border-left-color: var(--primary); }
.stat-card--teal   { border-left-color: var(--accent); }
.stat-card--orange { border-left-color: var(--warning); }
.stat-card--green  { border-left-color: var(--success); }
.stat-icon {
  font-size: 32px; width: 52px; height: 52px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px; background: var(--bg); flex-shrink: 0;
}
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.stat-trend { font-size: 12px; margin-top: 4px; font-weight: 500; }
.trend-up   { color: var(--success); }
.trend-down { color: var(--danger); }

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}
.chart-card-wide, .chart-card-narrow { margin-bottom: 0 !important; }
.chart-wrap { height: 220px; position: relative; }

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.quick-action-card {
  display: flex; align-items: center; gap: 14px;
  cursor: pointer; transition: all 0.2s; margin-bottom: 0 !important;
}
.quick-action-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.qa-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
}
.qa-icon--blue  { background: #ebf8ff; }
.qa-icon--teal  { background: #e6fffa; }
.qa-icon--green { background: #f0fff4; }
.qa-text  { flex: 1; }
.qa-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.qa-desc  { font-size: 12px; color: var(--text-secondary); margin-top: 3px; }
.qa-arrow { font-size: 18px; color: var(--text-secondary); }
</style>
