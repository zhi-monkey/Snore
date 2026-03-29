<template>
  <div>
  <TopBar title="睡眠呼吸监测仪表盘" subtitle="睡眠呼吸检测管理后台" />

    <div class="dashboard">

      <!-- ═══ Row 1: Overview Stats ═══════════════════════════════ -->
      <div class="stats-row">
        <div
          v-for="s in overviewStats"
          :key="s.label"
          class="stat-card"
        >
          <div class="stat-icon-box" :style="{ background: s.iconBg }">
            <span class="stat-svg" v-html="s.icon" :style="{ color: s.color }"></span>
          </div>
          <div class="stat-body">
            <div class="stat-value" :style="{ color: s.valueColor }">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
            <div class="stat-tag" :class="s.tagCls">{{ s.tag }}</div>
          </div>
        </div>
      </div>

      <!-- ═══ Row 2: Sleep Stage Timeline ════════════════════════ -->
      <div class="card">
        <div class="card-hd">
          <div class="card-title">
            <span class="icon-wrap primary" v-html="iconMoon"></span>
            睡眠分期时序图
          </div>
          <div class="stage-legend">
            <span
              v-for="leg in stageLegend"
              :key="leg.label"
              class="leg-pill"
              :style="{ background: leg.color + '20', color: leg.color, borderColor: leg.color + '40' }"
            >
              <span class="leg-dot" :style="{ background: leg.color }"></span>
              {{ leg.label }}
            </span>
          </div>
        </div>

        <div class="stage-timeline">
          <div
            v-for="row in stageRows"
            :key="row.label"
            class="stage-row"
          >
            <div class="stage-row-lbl" :style="{ color: row.color }">{{ row.label }}</div>
            <div class="stage-track">
              <div
                v-for="(seg, si) in row.segments"
                :key="si"
                class="stage-seg"
                :style="{
                  left: (seg.start / 540 * 100) + '%',
                  width: ((seg.end - seg.start) / 540 * 100) + '%',
                  background: row.color,
                }"
                :title="`${row.label}: ${toTime(seg.start)} – ${toTime(seg.end)}`"
              ></div>
            </div>
          </div>
          <div class="stage-x-axis">
            <span v-for="t in stageXLabels" :key="t">{{ t }}</span>
          </div>
        </div>

        <div class="stage-summary">
          <div v-for="s in stageSummary" :key="s.label" class="stage-sum-item">
            <span class="sum-dot" :style="{ background: s.color }"></span>
            <span class="sum-label">{{ s.label }}</span>
            <span class="sum-dur">{{ s.dur }}</span>
            <span class="sum-pct" :style="{ color: s.color }">{{ s.pct }}</span>
          </div>
        </div>
      </div>

      <!-- ═══ Row 3: SpO₂ Chart + Breathing Events ═══════════════ -->
      <div class="row-2col">
        <!-- SpO₂ Trend -->
        <div class="card spo2-card">
          <div class="card-hd">
            <div class="card-title">
              <span class="icon-wrap success" v-html="iconPulse"></span>
              血氧饱和度 (SpO₂) 趋势
            </div>
            <div class="chart-legend">
              <span class="cleg success">
                <span class="cleg-dot" style="background:#10B981"></span> 正常 ≥90%
              </span>
              <span class="cleg danger">
                <span class="cleg-dot" style="background:#EF4444"></span> 低氧预警 &lt;90%
              </span>
            </div>
          </div>
          <div class="spo2-chart-wrap">
            <Line
              :data="spo2Data"
              :options="spo2Opts"
              :plugins="[warningPlugin]"
            />
          </div>
        </div>

        <!-- Breathing Events -->
        <div class="card breathing-card">
          <div class="card-hd" style="margin-bottom:14px">
            <div class="card-title">
              <span class="icon-wrap danger" v-html="iconLung"></span>
              呼吸事件
            </div>
          </div>
          <div class="ev-list">
            <div
              v-for="ev in breathingEvents"
              :key="ev.label"
              class="ev-item"
            >
              <div class="ev-icon-box" :style="{ background: ev.bg }">
                <span class="ev-svg" v-html="ev.icon" :style="{ color: ev.color }"></span>
              </div>
              <div class="ev-body">
                <div class="ev-label">{{ ev.label }}</div>
                <div class="ev-value" :style="{ color: ev.color }">{{ ev.value }}</div>
                <div class="ev-unit">{{ ev.unit }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Row 4: Snoring Heatmap + AI Advice ═════════════════ -->
      <div class="row-2col">
        <!-- Snoring Heatmap -->
        <div class="card">
          <div class="card-hd">
            <div class="card-title">
              <span class="icon-wrap warning" v-html="iconMic"></span>
              鼾声强度热力图
            </div>
            <div class="hmap-legend">
              <span class="hmap-leg-txt">弱</span>
              <div class="hmap-leg-bar"></div>
              <span class="hmap-leg-txt">强</span>
            </div>
          </div>

          <div class="hmap-wrap">
            <div class="hmap-y-axis">
              <span v-for="f in freqLabels" :key="f">{{ f }}</span>
            </div>
            <div class="hmap-grid">
              <div v-for="(row, ri) in heatmapData" :key="ri" class="hmap-row">
                <div
                  v-for="(cell, ci) in row"
                  :key="ci"
                  class="hmap-cell"
                  :style="{ background: heatColor(cell) }"
                  :title="`${heatTimeLbl[ci]} | ${freqLabels[ri]} | 强度 ${Math.round(cell * 100)}%`"
                ></div>
              </div>
            </div>
          </div>
          <div class="hmap-x-axis">
            <span v-for="t in heatXLabels" :key="t">{{ t }}</span>
          </div>
        </div>

        <!-- AI Advice -->
        <div class="card advice-card">
          <div class="card-hd">
            <div class="card-title">
              <span class="icon-wrap primary" v-html="iconAi"></span>
              AI 诊断与建议
            </div>
            <span class="badge badge-warning">中度 OSAHS</span>
          </div>

          <div class="ai-block">
            <!-- Summary highlight -->
            <div class="ai-highlight">
              <span v-html="iconInfo" style="color:var(--primary);flex-shrink:0"></span>
              <p>
                本次检测 AHI 指数为 <strong>22.5 次/小时</strong>，达到
                <strong>中度睡眠呼吸暂停低通气综合征（OSAHS）</strong>诊断标准。
                最低血氧饱和度 <strong style="color:var(--danger)">87%</strong>，存在间歇性低氧血症。
              </p>
            </div>

            <!-- Advice list -->
            <div class="advice-list">
              <div v-for="(a, i) in adviceList" :key="i" class="advice-item">
                <span class="advice-num" :style="{ background: a.color }">{{ i + 1 }}</span>
                <span>{{ a.text }}</span>
              </div>
            </div>

            <!-- Score row -->
            <div class="score-row">
              <div v-for="sc in scores" :key="sc.label" class="score-item">
                <div class="score-val" :style="{ color: sc.color }">{{ sc.val }}</div>
                <div class="score-label">{{ sc.label }}</div>
              </div>
            </div>

            <!-- Actions -->
            <div class="advice-actions">
              <button class="btn btn-primary" @click="$router.push('/upload')">
                <span v-html="iconCheck" style="width:14px;height:14px"></span>
                生成检测报告
              </button>
              <button class="btn btn-outline" @click="$router.push('/reports')">查看历史报告</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Tooltip, Filler, type ChartOptions, type Chart,
} from 'chart.js'
import TopBar from '../components/TopBar.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

/* ── SVG Icons ─────────────────────────────────────────────── */
const iconMoon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`
const iconPulse = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`
const iconLung = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2v9a6 6 0 0 0 6 6 6 6 0 0 0 6-6V2"/><path d="M6 2C6 2 4 3 4 6v8a4 4 0 0 0 4 4"/><path d="M18 2c0 0 2 1 2 4v8a4 4 0 0 1-4 4"/><line x1="12" y1="2" x2="12" y2="14"/></svg>`
const iconMic = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>`
const iconAi = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`
const iconInfo = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
const iconCheck = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`

/* ── Overview Stats ────────────────────────────────────────── */
const overviewStats = [
  {
    label: 'AHI 指数', value: '22.5', tag: '中度', tagCls: 'tag-warning',
    valueColor: '#F59E0B', iconBg: '#FFFBEB', color: '#F59E0B',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  },
  {
    label: '平均 SpO₂', value: '93.4%', tag: '偏低', tagCls: 'tag-warning',
    valueColor: '#F59E0B', iconBg: '#FFFBEB', color: '#F59E0B',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>`,
  },
  {
    label: '最低 SpO₂', value: '87%', tag: '低氧预警', tagCls: 'tag-danger',
    valueColor: '#EF4444', iconBg: '#FEF2F2', color: '#EF4444',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  },
  {
    label: '总睡眠时长', value: '7h 32m', tag: '达标', tagCls: 'tag-success',
    valueColor: '#3B82F6', iconBg: '#EFF6FF', color: '#3B82F6',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`,
  },
  {
    label: '睡眠效率', value: '82%', tag: '一般', tagCls: 'tag-warning',
    valueColor: '#8B5CF6', iconBg: '#F5F3FF', color: '#8B5CF6',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
  },
]

/* ── Sleep Stage Timeline ──────────────────────────────────── */
const stageRows = [
  {
    label: '深睡', color: '#3B82F6',
    segments: [{ start: 80, end: 200 }, { start: 310, end: 335 }, { start: 360, end: 420 }],
  },
  {
    label: '浅睡', color: '#93C5FD',
    segments: [
      { start: 20, end: 80 }, { start: 200, end: 225 }, { start: 270, end: 310 },
      { start: 335, end: 360 }, { start: 470, end: 510 },
    ],
  },
  {
    label: 'REM', color: '#8B5CF6',
    segments: [{ start: 225, end: 270 }, { start: 420, end: 460 }, { start: 510, end: 540 }],
  },
  {
    label: '清醒', color: '#F59E0B',
    segments: [{ start: 0, end: 20 }, { start: 315, end: 325 }, { start: 460, end: 470 }],
  },
]
const stageLegend = stageRows.map(r => ({ label: r.label, color: r.color }))
const stageXLabels = ['22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00']
const stageSummary = [
  { label: '深睡', color: '#3B82F6', dur: '2h 35m', pct: '34%' },
  { label: '浅睡', color: '#93C5FD', dur: '3h 00m', pct: '40%' },
  { label: 'REM',  color: '#8B5CF6', dur: '1h 55m', pct: '25%' },
  { label: '清醒', color: '#F59E0B', dur: '5m',     pct: '1%' },
]

function toTime (minutes: number): string {
  const total = 22 * 60 + minutes
  const h = Math.floor(total / 60) % 24
  const m = total % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

/* ── SpO₂ Chart ────────────────────────────────────────────── */
const spo2Labels = [
  '22:00','22:30','23:00','23:30','00:00','00:30','01:00','01:30',
  '02:00','02:30','03:00','03:30','04:00','04:30','05:00','05:30',
  '06:00','06:30','07:00',
]
const spo2Values = [98, 97, 96, 95, 93, 92, 91, 90, 87, 88, 90, 93, 95, 94, 93, 94, 95, 96, 97]

const spo2Data = {
  labels: spo2Labels,
  datasets: [{
    label: 'SpO₂',
    data: spo2Values,
    borderColor: '#10B981',
    backgroundColor: 'rgba(16,185,129,0.08)',
    fill: true,
    tension: 0.4,
    borderWidth: 2.5,
    pointRadius: spo2Values.map(v => v < 90 ? 6 : 3),
    pointBackgroundColor: spo2Values.map(v => v < 90 ? '#EF4444' : '#10B981'),
    pointBorderColor: spo2Values.map(v => v < 90 ? '#EF4444' : '#10B981'),
    pointHoverRadius: 7,
  }],
}

const spo2Opts: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: ctx => ` SpO₂: ${ctx.raw}%`,
      },
    },
  },
  scales: {
    y: {
      min: 83, max: 100,
      ticks: { callback: v => v + '%', font: { size: 11 } },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    x: {
      ticks: { maxTicksLimit: 10, font: { size: 11 } },
      grid: { display: false },
    },
  },
}

const warningPlugin = {
  id: 'warningZone',
  beforeDraw (chart: Chart) {
    const { ctx, chartArea, scales } = chart
    if (!scales?.y || !chartArea) return
    const { y } = scales
    const { left, right } = chartArea
    const y90  = y.getPixelForValue(90)
    const yMin = y.getPixelForValue(y.min as number)
    ctx.save()
    // Red fill below 90%
    ctx.fillStyle = 'rgba(239,68,68,0.07)'
    ctx.fillRect(left, y90, right - left, yMin - y90)
    // Dashed threshold line
    ctx.strokeStyle = 'rgba(239,68,68,0.5)'
    ctx.lineWidth = 1.5
    ctx.setLineDash([5, 4])
    ctx.beginPath()
    ctx.moveTo(left, y90)
    ctx.lineTo(right, y90)
    ctx.stroke()
    ctx.setLineDash([])
    ctx.restore()
  },
}

/* ── Breathing Events ──────────────────────────────────────── */
const breathingEvents = [
  {
    label: '呼吸暂停', value: '18', unit: '次',
    color: '#EF4444', bg: '#FEF2F2',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>`,
  },
  {
    label: '低通气事件', value: '12', unit: '次',
    color: '#F59E0B', bg: '#FFFBEB',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 18 12 13 7 18"/><polyline points="17 6 12 11 7 6"/></svg>`,
  },
  {
    label: '最长暂停时间', value: '68', unit: '秒',
    color: '#EF4444', bg: '#FEF2F2',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  },
  {
    label: '平均暂停时间', value: '32', unit: '秒',
    color: '#F59E0B', bg: '#FFFBEB',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
  },
]

/* ── Snoring Heatmap ───────────────────────────────────────── */
const freqLabels = ['3.2kHz', '1.6kHz', '800Hz', '400Hz', '200Hz', '100Hz']
const heatXLabels = ['22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00']
const heatTimeLbl = Array.from({ length: 18 }, (_, i) => {
  const tot = 22 * 60 + i * 30
  const h = Math.floor(tot / 60) % 24
  const m = tot % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
})

// Deterministic heatmap (peaks at certain time slots → snoring episodes)
const SNORING_PEAK_SLOTS      = [1, 2, 3, 7, 8, 9, 13, 14, 15]
const PEAK_HIGH_FREQ_BASE     = 0.65   // intensity for low-frequency rows during peaks
const PEAK_HIGH_FREQ_JITTER   = 0.025  // small deterministic variation
const PEAK_LOW_FREQ_BASE      = 0.20   // intensity for high-frequency rows during peaks
const PEAK_LOW_FREQ_JITTER    = 0.03
const QUIET_BASE_INTENSITY    = 0.04   // background noise level
const QUIET_JITTER            = 0.008

const heatmapData = (() => {
  return Array.from({ length: 6 }, (_, row) =>
    Array.from({ length: 18 }, (_, col) => {
      const isPeak = SNORING_PEAK_SLOTS.includes(col)
      // Rows 3–5 (200 Hz – 100 Hz) carry most snoring energy
      const intensity = isPeak
        ? (row >= 3
          ? PEAK_HIGH_FREQ_BASE + ((row * 7 + col * 3) % 10) * PEAK_HIGH_FREQ_JITTER
          : PEAK_LOW_FREQ_BASE  + ((row * 5 + col * 4) % 10) * PEAK_LOW_FREQ_JITTER)
        : QUIET_BASE_INTENSITY  + ((row * 3 + col * 2) % 10) * QUIET_JITTER
      return Math.min(1, intensity)
    })
  )
})()

function heatColor (v: number): string {
  if (v < 0.15) return `rgba(59,130,246,${0.12 + v * 1.2})`
  if (v < 0.40) return `rgba(245,158,11,${0.45 + v * 0.8})`
  return `rgba(239,68,68,${0.55 + v * 0.42})`
}

/* ── AI Advice ─────────────────────────────────────────────── */
const adviceList = [
  { text: '建议进行持续气道正压通气（CPAP）治疗，可有效降低 AHI 至正常范围。', color: '#3B82F6' },
  { text: '控制体重，BMI 超标者减重 5–10% 可显著改善 OSAHS 症状。', color: '#10B981' },
  { text: '建议 2 周内复诊，评估 CPAP 依从性及睡眠结构改善情况。', color: '#F59E0B' },
]
const scores = [
  { label: '睡眠质量', val: '62分', color: '#F59E0B' },
  { label: '呼吸稳定性', val: '45分', color: '#EF4444' },
  { label: '氧合指数', val: '71分', color: '#F59E0B' },
]
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Card header ────────────────────────────────────────── */
.card-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  gap: 12px;
  flex-wrap: wrap;
}
.icon-wrap {
  width: 28px; height: 28px;
  border-radius: 6px;
  display: inline-flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.icon-wrap svg { width: 15px; height: 15px; }
.icon-wrap.primary { background: var(--primary-light); color: var(--primary); }
.icon-wrap.success { background: var(--success-light); color: var(--success); }
.icon-wrap.danger  { background: var(--danger-light);  color: var(--danger); }
.icon-wrap.warning { background: var(--warning-light); color: var(--warning); }

/* ── Row 1: Stats ──────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}
.stat-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: box-shadow 0.2s, transform 0.15s;
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.stat-icon-box {
  width: 46px; height: 46px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-svg { width: 22px; height: 22px; display: flex; }
.stat-svg svg { width: 22px; height: 22px; }
.stat-body { flex: 1; min-width: 0; }
.stat-value { font-size: 22px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; font-weight: 500; }
.stat-tag   { display: inline-block; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 4px; }
.tag-success { background: var(--success-light); color: #065F46; }
.tag-warning { background: var(--warning-light);  color: #92400E; }
.tag-danger  { background: var(--danger-light);   color: #991B1B; }

/* ── Row 2: Sleep Stage ───────────────────────────────── */
.stage-timeline { display: flex; flex-direction: column; gap: 6px; }
.stage-row { display: flex; align-items: center; gap: 10px; }
.stage-row-lbl {
  width: 36px; font-size: 11px; font-weight: 600;
  text-align: right; flex-shrink: 0;
}
.stage-track {
  flex: 1; height: 22px;
  background: var(--bg);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}
.stage-seg {
  position: absolute; top: 0; height: 100%;
  border-radius: 2px; opacity: 0.88;
  transition: opacity 0.15s;
}
.stage-seg:hover { opacity: 1; }

.stage-x-axis {
  display: flex; justify-content: space-between;
  padding-left: 46px;
  font-size: 10px; color: var(--text-muted);
  margin-top: 4px;
}
.stage-legend { display: flex; gap: 6px; flex-wrap: wrap; }
.leg-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 500;
  border: 1px solid transparent;
}
.leg-dot { width: 7px; height: 7px; border-radius: 50%; }

.stage-summary {
  display: flex; gap: 18px;
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}
.stage-sum-item { display: flex; align-items: center; gap: 5px; font-size: 12px; }
.sum-dot  { width: 10px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.sum-label { color: var(--text-secondary); }
.sum-dur   { font-weight: 600; color: var(--text-primary); margin-left: 2px; }
.sum-pct   { font-size: 11px; }

/* ── Row 3: 2-column ──────────────────────────────────── */
.row-2col {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  align-items: start;
}

.spo2-card { display: flex; flex-direction: column; }
.spo2-chart-wrap { height: 230px; position: relative; }

.chart-legend { display: flex; gap: 14px; }
.cleg { display: flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 500; }
.cleg.success { color: #065F46; }
.cleg.danger  { color: #991B1B; }
.cleg-dot { width: 8px; height: 8px; border-radius: 50%; }

/* Breathing Events */
.breathing-card { display: flex; flex-direction: column; }
.ev-list { display: flex; flex-direction: column; gap: 10px; }
.ev-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px;
  background: var(--bg);
  border-radius: 10px;
  border: 1px solid var(--border);
  transition: box-shadow 0.15s;
}
.ev-item:hover { box-shadow: var(--shadow); }
.ev-icon-box {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ev-svg { width: 18px; height: 18px; display: flex; }
.ev-svg svg { width: 18px; height: 18px; }
.ev-body { flex: 1; }
.ev-label { font-size: 11px; color: var(--text-secondary); font-weight: 500; margin-bottom: 2px; }
.ev-value { font-size: 26px; font-weight: 700; line-height: 1.1; }
.ev-unit  { font-size: 11px; color: var(--text-secondary); }

/* ── Row 4: Heatmap ───────────────────────────────────── */
.hmap-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}
.hmap-y-axis {
  display: flex; flex-direction: column; justify-content: space-between;
  flex-shrink: 0; width: 46px;
}
.hmap-y-axis span {
  font-size: 9px; color: var(--text-muted);
  text-align: right; height: 20px;
  display: flex; align-items: center; justify-content: flex-end;
}
.hmap-grid { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.hmap-row  { display: flex; gap: 2px; flex: 1; }
.hmap-cell {
  flex: 1; height: 20px;
  border-radius: 2px;
  cursor: pointer;
  transition: transform 0.1s;
}
.hmap-cell:hover { transform: scale(1.15); z-index: 1; }
.hmap-x-axis {
  display: flex; justify-content: space-between;
  padding-left: 54px;
  font-size: 10px; color: var(--text-muted);
}
.hmap-legend { display: flex; align-items: center; gap: 6px; }
.hmap-leg-txt { font-size: 11px; color: var(--text-secondary); }
.hmap-leg-bar {
  width: 64px; height: 8px; border-radius: 4px;
  background: linear-gradient(to right,
    rgba(59,130,246,0.3),
    rgba(245,158,11,0.8),
    rgba(239,68,68,0.9)
  );
}

/* ── AI Advice ────────────────────────────────────────── */
.advice-card { display: flex; flex-direction: column; }
.ai-block { display: flex; flex-direction: column; gap: 14px; }
.ai-highlight {
  display: flex; gap: 10px; align-items: flex-start;
  background: var(--primary-light);
  border-radius: 8px; padding: 14px 16px;
  font-size: 13px; line-height: 1.65; color: var(--text-primary);
}
.advice-list { display: flex; flex-direction: column; gap: 8px; }
.advice-item {
  display: flex; align-items: flex-start; gap: 10px;
  font-size: 13px; line-height: 1.6; color: var(--text-secondary);
}
.advice-num {
  min-width: 20px; height: 20px; border-radius: 50%;
  color: #fff; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 2px;
}
.score-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.score-item {
  background: var(--bg);
  border-radius: 8px; padding: 10px 12px; text-align: center;
  border: 1px solid var(--border);
}
.score-val   { font-size: 18px; font-weight: 700; }
.score-label { font-size: 10px; color: var(--text-secondary); margin-top: 3px; }
.advice-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 2px; }
</style>
