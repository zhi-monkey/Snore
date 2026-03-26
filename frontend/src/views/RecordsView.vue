<template>
  <div>
    <TopBar title="病历管理" subtitle="患者档案与历史病历记录" />

    <div class="records-layout">
      <!-- Left: Patient list -->
      <div class="patient-list-panel">
        <div class="card">
          <div class="card-title" style="justify-content:space-between">
            <span>📁 患者列表</span>
            <button class="btn btn-primary" style="font-size:12px;padding:5px 12px" @click="showAdd = true">＋ 新建档案</button>
          </div>
          <div class="search-box" style="margin-bottom:14px">
            <span class="search-icon">🔍</span>
            <input type="text" placeholder="搜索患者" v-model="search" />
          </div>
          <div class="patient-cards">
            <div
              v-for="p in filteredPatients" :key="p.id"
              :class="['patient-card', selected?.id === p.id ? 'patient-card--active' : '']"
              @click="selected = p"
            >
              <div class="patient-card-avatar">{{ p.name[0] }}</div>
              <div class="patient-card-info">
                <div class="patient-card-name">
                  {{ p.name }}<span class="patient-card-age"> {{ p.gender }} · {{ p.age }}岁</span>
                </div>
                <div class="patient-card-diag">
                  <span :class="`badge ${diagBadge(p.diagnosis)}`">{{ p.diagnosis }}</span>
                </div>
                <div class="patient-card-date">最近就诊：{{ p.lastVisit }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Detail -->
      <div class="patient-detail-panel">
        <template v-if="selected">
          <!-- Header Card -->
          <div class="card patient-header-card">
            <div class="patient-header">
              <div class="patient-big-avatar">{{ selected.name[0] }}</div>
              <div class="patient-header-info">
                <div class="patient-big-name">{{ selected.name }}</div>
                <div class="patient-meta">
                  <span>{{ selected.gender }}</span>
                  <span>{{ selected.age }}岁</span>
                  <span>📞 {{ selected.phone }}</span>
                  <span>主治：{{ selected.doctor }}</span>
                </div>
                <div style="margin-top:8px">
                  <span :class="`badge ${diagBadge(selected.diagnosis)}`"
                    style="font-size:13px;padding:4px 12px">{{ selected.diagnosis }}</span>
                </div>
              </div>
              <div class="patient-id-chip">ID: {{ selected.id }}</div>
            </div>
          </div>

          <!-- Records Timeline -->
          <div class="card">
            <div class="card-title"><span>📋</span> 历史病历记录</div>
            <div class="timeline">
              <div v-for="(rec, i) in selected.records" :key="i" class="timeline-item">
                <div class="timeline-dot" />
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-type">{{ rec.type }}</span>
                    <span class="timeline-date">{{ rec.date }}</span>
                  </div>
                  <div class="timeline-summary">{{ rec.summary }}</div>
                  <span v-if="rec.severity" :class="`badge ${levelBadge[rec.severity]}`" style="margin-top:4px">
                    {{ rec.severity }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="card">
            <div class="card-title"><span>⚙️</span> 操作</div>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <button class="btn btn-primary">🎙️ 发起新检测</button>
              <button class="btn btn-accent">📋 查看全部报告</button>
              <button class="btn btn-outline">✏️ 编辑患者信息</button>
              <button class="btn btn-outline">📤 导出病历</button>
            </div>
          </div>
        </template>

        <div v-else class="card empty-state">
          <div class="empty-icon">👈</div>
          <div class="empty-title">请选择患者</div>
          <div class="empty-desc">从左侧列表选择患者以查看病历详情</div>
        </div>
      </div>
    </div>

    <!-- Add Patient Modal -->
    <div v-if="showAdd" class="report-modal-overlay" @click="showAdd = false">
      <div class="report-modal" style="max-width:500px" @click.stop>
        <div class="modal-header">
          <div class="modal-title">新建患者档案</div>
          <button class="modal-close" @click="showAdd = false">✕</button>
        </div>
        <div class="form-grid">
          <div class="form-group"><label>姓名</label><input type="text" placeholder="请输入姓名" /></div>
          <div class="form-group"><label>性别</label>
            <select><option>男</option><option>女</option></select>
          </div>
          <div class="form-group"><label>年龄</label><input type="number" placeholder="年龄" /></div>
          <div class="form-group"><label>联系电话</label><input type="text" placeholder="手机号" /></div>
          <div class="form-group form-group--full"><label>既往病史</label><input type="text" placeholder="如：高血压、糖尿病" /></div>
          <div class="form-group form-group--full"><label>主治医师</label>
            <select><option>王医生</option><option>李医生</option><option>张医生</option></select>
          </div>
        </div>
        <div style="display:flex;gap:10px;margin-top:20px">
          <button class="btn btn-primary" @click="showAdd = false">✅ 保存档案</button>
          <button class="btn btn-outline" @click="showAdd = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TopBar from '../components/TopBar.vue'

interface PatientRecord { date: string; type: string; summary: string; severity: string }
interface Patient {
  id: string; name: string; gender: string; age: number; phone: string
  diagnosis: string; doctor: string; lastVisit: string; records: PatientRecord[]
}

const PATIENTS: Patient[] = [
  {
    id:'P001', name:'张三', gender:'男', age:45, phone:'138****8001',
    diagnosis:'中度OSAHS', doctor:'王医生', lastVisit:'2026-03-25',
    records:[
      { date:'2026-03-25', type:'睡眠检测', summary:'AHI=22.5, 中度, 18次呼吸阻塞', severity:'中度' },
      { date:'2026-01-10', type:'门诊就诊', summary:'主诉打鼾加重, 建议行睡眠监测', severity:'' },
      { date:'2025-11-20', type:'复查', summary:'AHI=19.2, 轻度改善', severity:'中度' },
    ]
  },
  {
    id:'P002', name:'李四', gender:'男', age:52, phone:'139****2345',
    diagnosis:'正常', doctor:'王医生', lastVisit:'2026-03-24',
    records:[
      { date:'2026-03-24', type:'睡眠检测', summary:'AHI=5.2, 正常范围', severity:'正常' },
      { date:'2025-09-08', type:'门诊就诊', summary:'体检发现打鼾, 建议监测', severity:'' },
    ]
  },
  {
    id:'P003', name:'王五', gender:'男', age:38, phone:'156****6789',
    diagnosis:'重度OSAHS', doctor:'李医生', lastVisit:'2026-03-24',
    records:[
      { date:'2026-03-24', type:'睡眠检测', summary:'AHI=38.1, 重度, 34次呼吸阻塞', severity:'重度' },
      { date:'2026-02-15', type:'门诊就诊', summary:'主诉日间嗜睡严重', severity:'' },
      { date:'2025-08-01', type:'睡眠检测', summary:'AHI=35.7, 重度', severity:'重度' },
    ]
  },
  {
    id:'P004', name:'赵六', gender:'女', age:61, phone:'177****4321',
    diagnosis:'轻度OSAHS', doctor:'王医生', lastVisit:'2026-03-23',
    records:[
      { date:'2026-03-23', type:'睡眠检测', summary:'AHI=12.7, 轻度', severity:'轻度' },
    ]
  },
  {
    id:'P005', name:'陈七', gender:'女', age:29, phone:'180****5555',
    diagnosis:'正常', doctor:'李医生', lastVisit:'2026-03-22',
    records:[
      { date:'2026-03-22', type:'睡眠检测', summary:'AHI=3.1, 正常', severity:'正常' },
    ]
  },
  {
    id:'P006', name:'吴八', gender:'男', age:55, phone:'132****7777',
    diagnosis:'重度OSAHS', doctor:'张医生', lastVisit:'2026-03-20',
    records:[
      { date:'2026-03-20', type:'睡眠检测', summary:'AHI=31.4, 重度', severity:'重度' },
      { date:'2025-12-18', type:'CPAP治疗', summary:'开始CPAP治疗, 依从性良好', severity:'' },
    ]
  },
]

const levelBadge: Record<string,string> = { '正常':'badge-success','轻度':'badge-info','中度':'badge-warning','重度':'badge-danger' }

function diagBadge (diag: string) {
  if (diag === '正常') return 'badge-success'
  if (diag.includes('轻度')) return 'badge-info'
  if (diag.includes('中度')) return 'badge-warning'
  if (diag.includes('重度')) return 'badge-danger'
  return 'badge-info'
}

const search   = ref('')
const selected = ref<Patient | null>(null)
const showAdd  = ref(false)

const filteredPatients = computed(() =>
  PATIENTS.filter(p =>
    p.name.includes(search.value) ||
    p.id.includes(search.value) ||
    p.diagnosis.includes(search.value)
  )
)
</script>

<style scoped>
.records-layout { display: grid; grid-template-columns: 300px 1fr; gap: 20px; align-items: start; }

.patient-cards { display: flex; flex-direction: column; gap: 6px; }
.patient-card {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: 8px; cursor: pointer; transition: all 0.15s;
  border: 1.5px solid transparent;
}
.patient-card:hover { background: var(--bg); }
.patient-card--active { background: var(--primary-light); border-color: var(--primary); }

.patient-card-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; flex-shrink: 0;
}
.patient-card-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.patient-card-age  { font-size: 12px; color: var(--text-secondary); font-weight: 400; margin-left: 4px; }
.patient-card-diag { margin-top: 3px; }
.patient-card-date { font-size: 11px; color: var(--text-secondary); margin-top: 3px; }

.patient-header {
  display: flex; align-items: flex-start; gap: 16px;
}
.patient-big-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; flex-shrink: 0;
}
.patient-big-name { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.patient-meta {
  display: flex; align-items: center; gap: 12px;
  font-size: 13px; color: var(--text-secondary); margin-top: 6px; flex-wrap: wrap;
}
.patient-id-chip {
  margin-left: auto; background: var(--bg); border-radius: 8px;
  padding: 6px 14px; font-size: 13px; font-weight: 600; color: var(--text-secondary);
}

.timeline { display: flex; flex-direction: column; gap: 0; padding-left: 12px; }
.timeline-item { display: flex; gap: 14px; position: relative; padding-bottom: 20px; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-dot {
  width: 12px; height: 12px; border-radius: 50%; background: var(--primary);
  flex-shrink: 0; margin-top: 3px; position: relative; z-index: 1;
}
.timeline-item:not(:last-child) .timeline-dot::after {
  content: ''; position: absolute; left: 5px; top: 14px;
  width: 2px; height: calc(100% + 20px);
  background: var(--border);
}
.timeline-content { flex: 1; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.timeline-type   { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.timeline-date   { font-size: 12px; color: var(--text-secondary); }
.timeline-summary { font-size: 13px; color: var(--text-secondary); }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon  { font-size: 48px; margin-bottom: 12px; opacity: 0.4; }
.empty-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.empty-desc  { font-size: 13px; color: var(--text-secondary); margin-top: 6px; }
</style>
