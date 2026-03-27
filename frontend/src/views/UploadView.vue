<template>
  <div>
    <TopBar title="睡眠呼吸检测" subtitle="上传睡眠音频，AI 智能分析呼吸阻塞事件" />

    <div class="upload-layout">
      <!-- Left: Upload + Patient form -->
      <div class="upload-panel">
        <!-- File Upload Card -->
        <div class="card">
          <div class="card-title"><span>🎙️</span> 上传音频文件</div>

          <!-- Idle state: drop zone -->
          <div
            v-if="stage === 'idle'"
            class="drop-zone"
            :class="{ 'drop-zone--active': dragOver }"
            @dragover.prevent="dragOver = true"
            @dragleave="dragOver = false"
            @drop.prevent="onDrop"
            @click="fileInput?.click()"
          >
            <div class="drop-icon">🎵</div>
            <div class="drop-title">拖拽文件到此处，或点击选择</div>
            <div class="drop-hint">支持格式：WAV · MP3 · FLAC · OGG · M4A<br />建议文件大小不超过 500MB</div>
            <button class="btn btn-primary" @click.stop="fileInput?.click()">选择文件</button>
            <input
              ref="fileInput"
              type="file"
              accept=".wav,.mp3,.flac,.ogg,.m4a"
              style="display:none"
              @change="onFileChange"
            />
          </div>

          <!-- Uploading / Analyzing state -->
          <div v-else-if="stage === 'uploading' || stage === 'analyzing'" class="progress-panel">
            <div class="file-info">
              <span class="file-icon">🎵</span>
              <div>
                <div class="file-name">{{ fileName }}</div>
                <div class="file-size">{{ fileSize }}</div>
              </div>
            </div>
            <div class="progress-label">
              {{ stage === 'uploading' ? '📤 正在上传...' : '🤖 AI 模型分析中...' }}
            </div>
            <div class="progress-bar-wrap">
              <div class="progress-bar" :style="{ width: progress.toFixed(0) + '%' }" />
            </div>
            <div class="progress-pct">{{ progress.toFixed(0) }}%</div>
            <div v-if="stage === 'analyzing'" class="analyzing-steps">
              <div class="step step--done">✅ 音频预处理</div>
              <div :class="['step', progress > 30 ? 'step--done' : 'step--active']">
                {{ progress > 30 ? '✅' : '⏳' }} 频谱特征提取
              </div>
              <div :class="['step', progress > 60 ? 'step--done' : progress > 30 ? 'step--active' : '']">
                {{ progress > 60 ? '✅' : '⏳' }} 呼吸阻塞事件检测
              </div>
              <div :class="['step', progress > 90 ? 'step--done' : progress > 60 ? 'step--active' : '']">
                {{ progress > 90 ? '✅' : '⏳' }} 生成检测报告
              </div>
            </div>
          </div>

          <!-- Done state -->
          <div v-else-if="stage === 'done'" class="done-panel">
            <div class="done-icon">✅</div>
            <div class="done-title">分析完成</div>
            <div class="done-file">{{ fileName }} · {{ fileSize }}</div>
            <button class="btn btn-outline" @click="resetUpload">重新上传</button>
          </div>
        </div>

        <!-- Patient Info Form -->
        <div class="card">
          <div class="card-title"><span>👤</span> 患者信息</div>
          <div class="form-grid">
            <div class="form-group">
              <label>姓名</label>
              <input type="text" placeholder="请输入患者姓名" v-model="form.name" />
            </div>
            <div class="form-group">
              <label>性别</label>
              <select v-model="form.gender">
                <option value="male">男</option>
                <option value="female">女</option>
              </select>
            </div>
            <div class="form-group">
              <label>年龄</label>
              <input type="number" placeholder="请输入年龄" v-model="form.age" />
            </div>
            <div class="form-group">
              <label>BMI</label>
              <input type="number" placeholder="如：26.5" v-model="form.bmi" />
            </div>
            <div class="form-group form-group--full">
              <label>既往病史</label>
              <input type="text" placeholder="如：高血压、糖尿病等" v-model="form.history" />
            </div>
            <div class="form-group">
              <label>录制日期</label>
              <input type="date" v-model="form.recordDate" />
            </div>
            <div class="form-group">
              <label>录制时长</label>
              <input type="text" placeholder="如：7h 30min" v-model="form.duration" />
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Results Panel -->
      <div class="results-panel">
        <!-- Spectrogram -->
        <div class="card">
          <div class="card-title">
            <span>📊</span> 睡眠呼吸频谱图
            <span v-if="stage === 'done'" class="spectrogram-legend">
              <span class="legend-dot legend-dot--normal" /> 正常呼吸&nbsp;&nbsp;
              <span class="legend-dot legend-dot--apnea"  /> 呼吸阻塞事件
            </span>
          </div>

          <div v-if="stage !== 'done'" class="spectrogram-placeholder">
            <div class="placeholder-icon">📊</div>
            <div class="placeholder-text">
              {{ stage === 'idle' ? '上传音频后将在此处显示频谱图' : '正在生成频谱图...' }}
            </div>
          </div>

          <div v-else class="spectrogram-container">
            <div class="spectrogram-y-labels">
              <div v-for="l in freqLabelsReversed" :key="l" class="y-label">{{ l }}</div>
            </div>
            <div class="spectrogram-canvas-wrap">
              <svg class="spectrogram-svg" viewBox="0 0 200 60" preserveAspectRatio="none">
                <rect
                  v-for="cell in spectrogramCells"
                  :key="`${cell.fi}-${cell.ti}`"
                  :x="cell.ti" :y="cell.fi * 10"
                  width="1" height="10"
                  :fill="cell.isApnea
                    ? `rgba(229,62,62,${(0.4 + cell.value * 0.6).toFixed(2)})`
                    : `rgba(43,108,176,${(0.1 + cell.value * 0.9).toFixed(2)})`"
                />
              </svg>
              <div class="apnea-markers">
                <div class="apnea-marker" style="left:15%;width:10%">
                  <div class="apnea-marker-label">阻塞事件1</div>
                </div>
                <div class="apnea-marker" style="left:40%;width:10%">
                  <div class="apnea-marker-label">阻塞事件2</div>
                </div>
                <div class="apnea-marker" style="left:70%;width:12.5%">
                  <div class="apnea-marker-label">阻塞事件3</div>
                </div>
              </div>
              <div class="spectrogram-x-labels">
                <span>0</span><span>1h</span><span>2h</span><span>3h</span>
                <span>4h</span><span>5h</span><span>6h</span><span>7h</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Analysis Result -->
        <template v-if="stage === 'done'">
          <div class="card">
            <div class="card-title"><span>📈</span> 分析结果摘要</div>
            <div class="result-grid">
              <div class="result-item result-item--highlight">
                <div class="result-value result-value--big">{{ result.ahi }}</div>
                <div class="result-key">AHI 指数（次/小时）</div>
                <span class="badge badge-warning">{{ result.severity }}睡眠呼吸暂停</span>
              </div>
              <div class="result-item">
                <div class="result-value">{{ result.apneaEvents }}</div>
                <div class="result-key">呼吸阻塞事件次数</div>
              </div>
              <div class="result-item">
                <div class="result-value">{{ result.longestApnea }}</div>
                <div class="result-key">最长阻塞时间</div>
              </div>
              <div class="result-item">
                <div class="result-value">{{ result.avgSpo2 }}%</div>
                <div class="result-key">平均血氧饱和度</div>
              </div>
              <div class="result-item">
                <div class="result-value result-value--danger">{{ result.minSpo2 }}%</div>
                <div class="result-key">最低血氧饱和度</div>
              </div>
              <div class="result-item">
                <div class="result-value">{{ result.duration }}</div>
                <div class="result-key">总监测时长</div>
              </div>
            </div>
          </div>

          <div class="card recommendation-card">
            <div class="card-title"><span>💊</span> 医生建议</div>
            <div class="recommendation">
              <span class="rec-icon">⚕️</span>
              <p>{{ result.recommendation }}</p>
            </div>
            <div class="action-btns">
              <button class="btn btn-primary">📄 生成检测报告</button>
              <button class="btn btn-accent">📤 导出 PDF</button>
              <button class="btn btn-outline">📁 保存至病历</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import TopBar from '../components/TopBar.vue'

type Stage = 'idle' | 'uploading' | 'analyzing' | 'done'

const FREQ_LABELS = ['0-100Hz', '100-200Hz', '200-400Hz', '400-800Hz', '800-1.6kHz', '1.6k-3.2kHz']
const freqLabelsReversed = [...FREQ_LABELS].reverse()

function generateSpectrogramCells () {
  const cells: { fi: number; ti: number; value: number; isApnea: boolean }[] = []
  const apneaWins = [[30, 50], [80, 100], [140, 165]]
  const inApnea = (t: number) => apneaWins.some(([a, b]) => t >= a && t <= b)
  for (let f = 0; f < 6; f++) {
    for (let t = 0; t < 200; t++) {
      const ap = inApnea(t)
      cells.push({ fi: 5 - f, ti: t, value: ap ? 0.1 + Math.random() * 0.15 : 0.4 + Math.random() * 0.5, isApnea: ap })
    }
  }
  return cells
}

const stage = ref<Stage>('idle')
const dragOver = ref(false)
const fileName = ref('')
const fileSize  = ref('')
const progress  = ref(0)
const fileInput = ref<HTMLInputElement | null>(null)
const spectrogramCells = generateSpectrogramCells()

const form = reactive({
  name: '张三', gender: 'male', age: '45', bmi: '27.2',
  history: '高血压', recordDate: '2026-03-25', duration: '7h 32min',
})

const result = reactive({
  ahi: 22.5, severity: '中度', apneaEvents: 18, longestApnea: '68s',
  avgSpo2: 93.4, minSpo2: 87, duration: '7h 32min',
  recommendation: '建议进行持续气道正压通气(CPAP)治疗，并尽快复诊。',
})

function handleFile (file: File) {
  if (!file.name.match(/\.(wav|mp3|flac|ogg|m4a)$/i)) {
    alert('请上传音频文件（WAV / MP3 / FLAC / OGG / M4A）')
    return
  }
  fileName.value = file.name
  fileSize.value  = (file.size / (1024 * 1024)).toFixed(2) + ' MB'
  stage.value = 'uploading'
  progress.value = 0

  let p = 0
  const uploadTimer = setInterval(() => {
    p += Math.random() * 15
    if (p >= 100) {
      p = 100; clearInterval(uploadTimer); progress.value = 100
      setTimeout(() => {
        stage.value = 'analyzing'
        let ap = 0
        const analyzeTimer = setInterval(() => {
          ap += Math.random() * 8
          if (ap >= 100) {
            ap = 100; clearInterval(analyzeTimer)
            setTimeout(() => { stage.value = 'done' }, 300)
          }
          progress.value = Math.min(ap, 100)
        }, 200)
      }, 500)
    }
    progress.value = Math.min(p, 100)
  }, 150)
}

function onDrop (e: DragEvent) {
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file) handleFile(file)
}

function onFileChange (e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

function resetUpload () {
  stage.value = 'idle'; fileName.value = ''; fileSize.value = ''; progress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<style scoped>
.upload-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
  align-items: start;
}
.upload-panel, .results-panel { display: flex; flex-direction: column; gap: 0; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.drop-zone:hover, .drop-zone--active { border-color: var(--primary); background: var(--primary-light); }
.drop-icon  { font-size: 48px; margin-bottom: 4px; }
.drop-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.drop-hint  { font-size: 12px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 4px; }

.progress-panel { padding: 8px 0; }
.file-info {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px; padding: 12px;
  background: var(--bg); border-radius: 8px;
}
.file-icon { font-size: 28px; }
.file-name { font-size: 14px; font-weight: 600; color: var(--text-primary); word-break: break-all; }
.file-size { font-size: 12px; color: var(--text-secondary); }
.progress-label { font-size: 13px; font-weight: 500; color: var(--primary); margin-bottom: 8px; }
.progress-bar-wrap { height: 8px; background: var(--border); border-radius: 999px; overflow: hidden; margin-bottom: 4px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); border-radius: 999px; transition: width 0.3s; }
.progress-pct { font-size: 12px; color: var(--text-secondary); text-align: right; margin-bottom: 16px; }
.analyzing-steps { display: flex; flex-direction: column; gap: 6px; }
.step { font-size: 13px; color: var(--text-secondary); padding: 6px 10px; border-radius: 6px; }
.step--done   { color: var(--success); background: #f0fff4; }
.step--active { color: var(--primary); background: var(--primary-light); font-weight: 500; }

.done-panel { text-align: center; padding: 24px 0; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.done-icon  { font-size: 48px; }
.done-title { font-size: 18px; font-weight: 700; color: var(--success); }
.done-file  { font-size: 13px; color: var(--text-secondary); }

.spectrogram-placeholder {
  height: 180px; background: var(--bg); border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
}
.placeholder-icon { font-size: 40px; opacity: 0.4; }
.placeholder-text { font-size: 14px; color: var(--text-secondary); }

.spectrogram-container { display: flex; gap: 8px; }
.spectrogram-y-labels {
  display: flex; flex-direction: column; justify-content: space-between;
  padding: 0 4px; flex-shrink: 0;
}
.y-label { font-size: 10px; color: var(--text-secondary); height: 30px; display: flex; align-items: center; }
.spectrogram-canvas-wrap { flex: 1; position: relative; }
.spectrogram-svg { width: 100%; height: 180px; display: block; border-radius: 6px; background: #0a1628; }
.apnea-markers { position: absolute; top: 0; left: 0; right: 0; bottom: 24px; pointer-events: none; }
.apnea-marker {
  position: absolute; top: 0; bottom: 0;
  border: 2px solid rgba(229,62,62,0.8); border-radius: 2px;
  background: rgba(229,62,62,0.05);
}
.apnea-marker-label {
  position: absolute; top: -20px; left: 50%; transform: translateX(-50%);
  font-size: 9px; font-weight: 600; color: var(--danger); white-space: nowrap;
  background: #fff; padding: 1px 4px; border-radius: 3px; border: 1px solid var(--danger);
}
.spectrogram-x-labels {
  display: flex; justify-content: space-between;
  padding-top: 4px; font-size: 11px; color: var(--text-secondary);
}
.spectrogram-legend { margin-left: auto; font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; }
.legend-dot { display: inline-block; width: 12px; height: 12px; border-radius: 2px; }
.legend-dot--normal { background: rgba(43,108,176,0.7); }
.legend-dot--apnea  { background: rgba(229,62,62,0.8); }

.result-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.result-item { background: var(--bg); border-radius: 10px; padding: 14px 16px; text-align: center; }
.result-item--highlight {
  background: #fff8f0; border: 1.5px solid var(--warning);
  grid-column: 1 / -1; display: flex; align-items: center;
  justify-content: space-between; gap: 12px; text-align: left; padding: 16px 20px;
}
.result-value { font-size: 22px; font-weight: 700; color: var(--primary); }
.result-value--big { font-size: 32px; color: var(--warning); }
.result-value--danger { color: var(--danger); }
.result-key { font-size: 11px; color: var(--text-secondary); margin-top: 3px; }

.recommendation {
  display: flex; align-items: flex-start; gap: 12px;
  background: var(--primary-light); border-radius: 8px;
  padding: 14px 16px; margin-bottom: 16px;
}
.rec-icon { font-size: 22px; flex-shrink: 0; }
.recommendation p { font-size: 14px; line-height: 1.7; color: var(--primary-dark); }
.action-btns { display: flex; gap: 10px; flex-wrap: wrap; }
</style>
