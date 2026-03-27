<template>
  <div>
    <TopBar title="检测报告" subtitle="查看所有睡眠呼吸检测报告" />

    <div class="card">
      <!-- Toolbar -->
      <div class="reports-toolbar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" placeholder="搜索患者姓名 / 报告编号" v-model="search" />
        </div>
        <div class="filter-group">
          <span class="filter-label">严重程度：</span>
          <button
            v-for="s in severities" :key="s"
            :class="['filter-btn', filterSeverity === s ? 'filter-btn--active' : '']"
            @click="filterSeverity = s"
          >{{ s }}</button>
        </div>
      </div>

      <div class="reports-count">共 {{ filtered.length }} 份报告</div>

      <table class="data-table">
        <thead>
          <tr>
            <th>报告编号</th><th>患者</th><th>检测日期</th>
            <th>AHI 指数</th><th>阻塞事件</th><th>监测时长</th>
            <th>严重程度</th><th>状态</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filtered" :key="r.id">
            <td><code style="font-size:11px">{{ r.id }}</code></td>
            <td>
              <strong>{{ r.patient }}</strong>
              <span style="color:var(--text-secondary);font-size:12px"> {{ r.age }}岁</span>
            </td>
            <td>{{ r.date }}</td>
            <td><strong>{{ r.ahi }}</strong></td>
            <td>{{ r.events }}</td>
            <td>{{ r.duration }}</td>
            <td><span :class="`badge ${levelBadge[r.severity]}`">{{ r.severity }}</span></td>
            <td><span :class="`badge ${statusBadge[r.status]}`">{{ r.status }}</span></td>
            <td>
              <button class="btn btn-primary" style="padding:4px 12px;font-size:12px"
                @click="selected = r">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal -->
    <div v-if="selected" class="report-modal-overlay" @click="selected = null">
      <div class="report-modal" @click.stop>
        <div class="modal-header">
          <div>
            <div class="modal-title">检测报告详情</div>
            <div class="modal-id">{{ selected.id }}</div>
          </div>
          <button class="modal-close" @click="selected = null">✕</button>
        </div>

        <!-- Patient Info -->
        <div class="modal-section">
          <div class="section-title">患者基本信息</div>
          <div class="info-grid">
            <div><span class="info-key">姓名</span><span class="info-val">{{ selected.patient }}</span></div>
            <div><span class="info-key">年龄</span><span class="info-val">{{ selected.age }}岁</span></div>
            <div><span class="info-key">检测日期</span><span class="info-val">{{ selected.date }}</span></div>
            <div><span class="info-key">主治医师</span><span class="info-val">{{ selected.doctor }}</span></div>
            <div><span class="info-key">监测时长</span><span class="info-val">{{ selected.duration }}</span></div>
            <div>
              <span class="info-key">严重程度</span>
              <span :class="`badge ${levelBadge[selected.severity]}`" class="info-val">{{ selected.severity }}</span>
            </div>
          </div>
        </div>

        <!-- Key Metrics -->
        <div class="modal-section">
          <div class="section-title">核心指标</div>
          <div class="metrics-row">
            <div class="metric-box metric-box--primary">
              <div class="metric-val">{{ selected.ahi }}</div>
              <div class="metric-name">AHI 指数</div>
              <div class="metric-unit">次/小时</div>
            </div>
            <div class="metric-box">
              <div class="metric-val">{{ selected.events }}</div>
              <div class="metric-name">阻塞事件</div>
              <div class="metric-unit">次</div>
            </div>
            <div class="metric-box">
              <div class="metric-val">{{ selected.spo2Avg }}%</div>
              <div class="metric-name">平均血氧</div>
              <div class="metric-unit">SpO₂</div>
            </div>
            <div class="metric-box metric-box--danger">
              <div class="metric-val">{{ selected.spo2Min }}%</div>
              <div class="metric-name">最低血氧</div>
              <div class="metric-unit">SpO₂</div>
            </div>
          </div>
        </div>

        <!-- Mini Spectrogram -->
        <div class="modal-section">
          <div class="section-title">睡眠呼吸频谱（缩略图）</div>
          <div class="mini-spectrogram-wrap">
            <svg viewBox="0 0 200 40" preserveAspectRatio="none" class="mini-spec-svg">
              <rect
                v-for="cell in miniSpectrogramCells"
                :key="`${cell.fi}-${cell.ti}`"
                :x="cell.ti" :y="cell.fi * 7"
                width="1" height="7"
                :fill="cell.isApnea
                  ? `rgba(229,62,62,${(0.4+cell.v*0.6).toFixed(2)})`
                  : `rgba(43,108,176,${(0.1+cell.v*0.9).toFixed(2)})`"
              />
            </svg>
            <div class="mini-marker" style="left:15%;width:10%"><span class="mini-marker-label">事件1</span></div>
            <div class="mini-marker" style="left:40%;width:10%"><span class="mini-marker-label">事件2</span></div>
            <div class="mini-marker" style="left:70%;width:12.5%"><span class="mini-marker-label">事件3</span></div>
            <div class="mini-x-labels">
              <span>0</span><span>2h</span><span>4h</span><span>6h</span><span>7h32m</span>
            </div>
          </div>
        </div>

        <!-- Conclusion -->
        <div class="modal-section">
          <div class="section-title">诊断结论与建议</div>
          <div class="conclusion-box">
            <p>患者监测期间共检测到 <strong>{{ selected.events }}</strong> 次呼吸阻塞事件，AHI 指数为 <strong>{{ selected.ahi }}</strong> 次/小时，
            诊断为<strong>{{ selected.severity }}睡眠呼吸暂停低通气综合征（OSAHS）</strong>。
            最低血氧饱和度为 <strong>{{ selected.spo2Min }}%</strong>，存在间歇性低氧血症。</p>
            <p style="margin-top:8px" v-if="selected.severity === '重度' || selected.severity === '中度'">
              建议：立即就诊，考虑使用持续气道正压通气（CPAP）治疗，同时评估是否需要手术干预。
            </p>
            <p style="margin-top:8px" v-else>建议：加强随访，注意体重控制，改善睡眠体位，定期复查。</p>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-primary">📤 导出 PDF</button>
          <button class="btn btn-accent">🖨️ 打印报告</button>
          <button class="btn btn-outline" @click="selected = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TopBar from '../components/TopBar.vue'

interface Report {
  id: string; patient: string; age: number; date: string
  ahi: number; events: number; duration: string
  spo2Avg: number; spo2Min: number; severity: string
  status: string; doctor: string
}

const reports: Report[] = [
  { id:'RPT-20260325-001', patient:'张三', age:45, date:'2026-03-25', ahi:22.5, events:18, duration:'7h 32min', spo2Avg:93.4, spo2Min:87, severity:'中度', status:'待复查', doctor:'王医生' },
  { id:'RPT-20260324-002', patient:'李四', age:52, date:'2026-03-24', ahi:5.2,  events:3,  duration:'6h 45min', spo2Avg:96.8, spo2Min:93, severity:'正常', status:'已完成', doctor:'王医生' },
  { id:'RPT-20260324-003', patient:'王五', age:38, date:'2026-03-24', ahi:38.1, events:34, duration:'8h 10min', spo2Avg:90.1, spo2Min:82, severity:'重度', status:'治疗中', doctor:'李医生' },
  { id:'RPT-20260323-004', patient:'赵六', age:61, date:'2026-03-23', ahi:12.7, events:9,  duration:'7h 05min', spo2Avg:94.5, spo2Min:89, severity:'轻度', status:'已完成', doctor:'王医生' },
  { id:'RPT-20260322-005', patient:'陈七', age:29, date:'2026-03-22', ahi:3.1,  events:1,  duration:'7h 55min', spo2Avg:97.2, spo2Min:94, severity:'正常', status:'已完成', doctor:'李医生' },
  { id:'RPT-20260320-006', patient:'吴八', age:55, date:'2026-03-20', ahi:31.4, events:28, duration:'6h 30min', spo2Avg:91.3, spo2Min:84, severity:'重度', status:'治疗中', doctor:'张医生' },
]

const levelBadge: Record<string,string> = { '正常':'badge-success','轻度':'badge-info','中度':'badge-warning','重度':'badge-danger' }
const statusBadge: Record<string,string> = { '待复查':'badge-warning','已完成':'badge-success','治疗中':'badge-info' }

const search         = ref('')
const filterSeverity = ref('全部')
const selected       = ref<Report | null>(null)
const severities     = ['全部','正常','轻度','中度','重度']

const filtered = computed(() => reports.filter(r => {
  const q = search.value.toLowerCase()
  return (r.patient.toLowerCase().includes(q) || r.id.toLowerCase().includes(q))
    && (filterSeverity.value === '全部' || r.severity === filterSeverity.value)
}))

// Mini spectrogram cells (generated once)
const miniSpectrogramCells = (() => {
  const cells: { fi: number; ti: number; v: number; isApnea: boolean }[] = []
  for (let f = 0; f < 6; f++) {
    for (let t = 0; t < 200; t++) {
      const ap = (t>=30&&t<=50)||(t>=80&&t<=100)||(t>=140&&t<=165)
      cells.push({ fi: f, ti: t, v: ap ? 0.1+Math.random()*0.15 : 0.4+Math.random()*0.5, isApnea: ap })
    }
  }
  return cells
})()
</script>

<style scoped>
.reports-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; margin-bottom: 16px; flex-wrap: wrap;
}
.reports-count { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; }

.info-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
.info-key  { font-size: 12px; color: var(--text-secondary); margin-right: 6px; }
.info-val  { font-size: 14px; font-weight: 500; color: var(--text-primary); }

.metrics-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; }
.metric-box {
  background: var(--bg); border-radius: 10px; padding: 14px 12px;
  text-align: center; border: 1.5px solid transparent;
}
.metric-box--primary { border-color: var(--primary); background: var(--primary-light); }
.metric-box--danger  { border-color: var(--danger);  background: #fff5f5; }
.metric-val  { font-size: 22px; font-weight: 700; color: var(--primary); }
.metric-name { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.metric-unit { font-size: 11px; color: var(--text-secondary); }

.mini-spectrogram-wrap { position: relative; }
.mini-spec-svg { width: 100%; height: 90px; background: #0a1628; border-radius: 6px; display: block; }
.mini-marker {
  position: absolute; top: 0; bottom: 20px;
  border: 1.5px solid rgba(229,62,62,0.8); border-radius: 2px;
  background: rgba(229,62,62,0.05);
}
.mini-marker-label {
  position: absolute; top: -18px; left: 50%; transform: translateX(-50%);
  font-size: 9px; color: var(--danger); background: #fff; padding: 1px 4px;
  border-radius: 3px; border: 1px solid var(--danger); white-space: nowrap;
}
.mini-x-labels {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--text-secondary); padding-top: 4px;
}

.conclusion-box {
  background: var(--bg); border-radius: 8px;
  padding: 16px; font-size: 14px; line-height: 1.7; color: var(--text-primary);
}
</style>
