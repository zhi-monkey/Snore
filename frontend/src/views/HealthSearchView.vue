<template>
  <div>
    <TopBar title="健康搜索" subtitle="睡眠健康知识库，快速查阅相关医学信息" />

    <!-- Search Hero -->
    <div class="card search-hero">
      <div class="hero-title">🔍 搜索健康知识</div>
      <div class="hero-search-bar">
        <input
          type="text"
          class="hero-input"
          placeholder="搜索疾病、症状、治疗方法..."
          v-model="query"
          @keydown.enter="doSearch()"
        />
        <button class="btn btn-primary hero-btn" @click="doSearch()">搜索</button>
      </div>
      <div class="hot-searches">
        <span class="hot-label">🔥 热门搜索：</span>
        <button
          v-for="h in HOT_SEARCHES" :key="h"
          class="hot-tag"
          @click="query = h; doSearch()"
        >{{ h }}</button>
      </div>
    </div>

    <!-- Category Filter -->
    <div class="card" style="padding:14px 20px;margin-bottom:16px">
      <div class="filter-group">
        <span class="filter-label">分类：</span>
        <button
          v-for="c in CATEGORIES" :key="c"
          :class="['filter-btn', category === c ? 'filter-btn--active' : '']"
          @click="category = c"
        >{{ c }}</button>
      </div>
    </div>

    <!-- Knowledge List -->
    <div class="knowledge-list">
      <div v-if="filtered.length === 0" class="card" style="text-align:center;padding:40px;color:var(--text-secondary)">
        <div style="font-size:40px;margin-bottom:12px">😕</div>
        <div style="font-size:16px;font-weight:600">未找到相关结果</div>
        <div style="font-size:13px;margin-top:6px">请尝试其他关键词</div>
      </div>

      <div v-for="item in filtered" :key="item.id" class="card knowledge-card">
        <div class="knowledge-header" @click="toggleExpand(item.id)">
          <div class="knowledge-icon">{{ item.icon }}</div>
          <div class="knowledge-main">
            <div class="knowledge-title">{{ item.title }}</div>
            <div class="knowledge-summary">{{ item.summary }}</div>
            <div class="knowledge-tags">
              <span class="badge badge-info" style="margin-right:4px;font-size:11px">{{ item.category }}</span>
              <span v-for="t in item.tags" :key="t" class="knowledge-tag">{{ t }}</span>
            </div>
          </div>
          <div class="knowledge-expand">{{ expanded === item.id ? '▲ 收起' : '▼ 展开' }}</div>
        </div>
        <div v-if="expanded === item.id" class="knowledge-content">
          <pre class="knowledge-pre">{{ item.content }}</pre>
        </div>
      </div>
    </div>

    <!-- Health Tips -->
    <div class="card">
      <div class="card-title"><span>💡</span> 睡眠健康小贴士</div>
      <div class="tips-grid">
        <div v-for="(t, i) in TIPS" :key="i" class="tip-item">
          <span class="tip-icon">{{ t.icon }}</span>
          <span class="tip-text">{{ t.tip }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TopBar from '../components/TopBar.vue'

interface KnowledgeItem { id: number; title: string; category: string; icon: string; summary: string; content: string; tags: string[] }

const KNOWLEDGE_BASE: KnowledgeItem[] = [
  {
    id:1, title:'阻塞性睡眠呼吸暂停低通气综合征（OSAHS）',
    category:'疾病百科', icon:'🫁',
    summary:'一种以睡眠中反复发生的上气道塌陷为特征的睡眠呼吸疾病，可导致间歇性低氧血症。',
    content:`阻塞性睡眠呼吸暂停（OSA）是最常见的睡眠呼吸障碍，以睡眠期间上气道部分或完全塌陷为特征。主要症状包括：大声打鼾、夜间窒息/喘气、日间嗜睡、晨起头痛、注意力难以集中等。`,
    tags:['OSAHS','打鼾','睡眠障碍','低氧血症']
  },
  {
    id:2, title:'AHI 指数解读',
    category:'检测指标', icon:'📊',
    summary:'呼吸暂停低通气指数（AHI）是评估睡眠呼吸暂停严重程度的核心指标，以每小时发生次数计算。',
    content:`AHI（Apnea-Hypopnea Index）分级标准：
• 正常：AHI < 5 次/小时
• 轻度：5 ≤ AHI < 15 次/小时
• 中度：15 ≤ AHI < 30 次/小时
• 重度：AHI ≥ 30 次/小时

AHI 越高，表明睡眠呼吸障碍越严重，需要及时干预治疗。`,
    tags:['AHI','诊断标准','睡眠监测']
  },
  {
    id:3, title:'CPAP 治疗（持续气道正压通气）',
    category:'治疗方法', icon:'⚕️',
    summary:'CPAP 是中重度睡眠呼吸暂停的一线治疗方案，通过持续正压防止气道塌陷。',
    content:`CPAP（Continuous Positive Airway Pressure）治疗是通过面罩向气道输送持续正压气流，维持上气道开放，防止睡眠中气道塌陷。适应证为：中重度 OSAHS（AHI≥15）或轻度但有显著日间嗜睡者。正确使用 CPAP 可显著改善睡眠质量和日间功能。`,
    tags:['CPAP','治疗','气道正压']
  },
  {
    id:4, title:'血氧饱和度（SpO₂）监测',
    category:'检测指标', icon:'💉',
    summary:'血氧饱和度是反映血液携氧能力的重要指标，睡眠期间 SpO₂ 下降提示存在缺氧事件。',
    content:`正常人血氧饱和度应维持在 95%-100%。睡眠呼吸暂停患者在阻塞事件发生时，SpO₂ 会出现间歇性下降（即氧减事件）。
• SpO₂ ≥ 95%：正常
• SpO₂ 90%-95%：轻度低氧
• SpO₂ < 90%：需要引起重视`,
    tags:['SpO₂','血氧','低氧血症']
  },
  {
    id:5, title:'打鼾与睡眠呼吸暂停的关系',
    category:'健康科普', icon:'😴',
    summary:'打鼾是睡眠呼吸暂停最常见的症状，但并非所有打鼾者都患有 OSAHS。',
    content:`打鼾是气流通过狭窄气道时产生的振动声音，是 OSAHS 的重要预警信号。流行病学数据显示：约 40% 的男性和 20% 的女性有习惯性打鼾，其中约一半存在 OSAHS。高危人群：肥胖、颈围大、下颌后缩、饮酒、服用镇静药物者。`,
    tags:['打鼾','睡眠健康','预防']
  },
  {
    id:6, title:'睡眠呼吸暂停的危险因素',
    category:'健康科普', icon:'⚠️',
    summary:'了解危险因素有助于早期识别高风险人群，进行预防性干预。',
    content:`主要危险因素包括：
1. 肥胖：BMI > 28 显著增加 OSAHS 风险
2. 年龄与性别：中年男性发病率最高
3. 解剖因素：扁桃体肥大、小下颌、鼻中隔偏曲
4. 生活方式：吸烟、饮酒、镇静药物
5. 遗传因素：有家族史者风险增加
6. 合并疾病：高血压、糖尿病、甲减等`,
    tags:['危险因素','预防','肥胖','高血压']
  },
]

const CATEGORIES = ['全部','疾病百科','检测指标','治疗方法','健康科普']
const HOT_SEARCHES = ['AHI指数','CPAP治疗','睡眠监测','血氧饱和度','打鼾危害','睡眠质量改善']
const TIPS = [
  { icon:'🛏️', tip:'保持规律作息，每天同一时间上床和起床' },
  { icon:'🏃', tip:'规律运动有助于改善睡眠质量，但避免睡前2小时剧烈运动' },
  { icon:'🍷', tip:'睡前避免饮酒，酒精会加重气道塌陷和打鼾' },
  { icon:'⚖️', tip:'控制体重，BMI 超标是 OSAHS 的重要危险因素' },
  { icon:'🔄', tip:'尝试侧卧入睡，可减少气道阻塞风险' },
  { icon:'🏥', tip:'长期打鼾伴日间嗜睡者，建议及时就医检查' },
]

const query    = ref('')
const category = ref('全部')
const expanded = ref<number | null>(null)
const searched = ref(false)

function doSearch () { searched.value = true }
function toggleExpand (id: number) { expanded.value = expanded.value === id ? null : id }

const filtered = computed(() => KNOWLEDGE_BASE.filter(item => {
  const q = query.value.toLowerCase()
  const matchQ = !searched.value || !q
    || item.title.includes(query.value)
    || item.summary.includes(query.value)
    || item.tags.some(t => t.toLowerCase().includes(q))
    || item.content.includes(query.value)
  const matchC = category.value === '全部' || item.category === category.value
  return matchQ && matchC
}))
</script>

<style scoped>
.search-hero { text-align: center; padding: 32px 24px; }
.hero-title  { font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }
.hero-search-bar {
  display: flex; max-width: 560px; margin: 0 auto 16px; gap: 0;
  border: 2px solid var(--primary); border-radius: 10px; overflow: hidden;
}
.hero-input {
  flex: 1; padding: 12px 16px; border: none; outline: none;
  font-size: 15px; color: var(--text-primary);
}
.hero-btn { border-radius: 0; padding: 12px 24px; }
.hot-searches { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: center; }
.hot-label    { font-size: 13px; color: var(--text-secondary); }
.hot-tag {
  padding: 4px 12px; border-radius: 999px; background: var(--bg);
  border: 1.5px solid var(--border); font-size: 12px; cursor: pointer;
  color: var(--text-secondary); transition: all 0.15s;
}
.hot-tag:hover { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }

.knowledge-list { display: flex; flex-direction: column; gap: 0; }
.knowledge-card { padding: 16px 20px; }
.knowledge-header {
  display: flex; align-items: flex-start; gap: 14px;
  cursor: pointer; user-select: none;
}
.knowledge-icon  { font-size: 28px; flex-shrink: 0; margin-top: 2px; }
.knowledge-main  { flex: 1; }
.knowledge-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.knowledge-summary { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 8px; }
.knowledge-tags  { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
.knowledge-tag {
  padding: 2px 8px; border-radius: 4px; background: var(--bg);
  font-size: 11px; color: var(--text-secondary); border: 1px solid var(--border);
}
.knowledge-expand { font-size: 12px; color: var(--primary); white-space: nowrap; flex-shrink: 0; }
.knowledge-content { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.knowledge-pre {
  font-family: inherit; font-size: 13px; color: var(--text-primary);
  line-height: 1.7; white-space: pre-wrap; background: var(--bg);
  border-radius: 8px; padding: 12px 16px;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.tip-item {
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--bg); border-radius: 8px; padding: 12px 14px;
}
.tip-icon { font-size: 20px; flex-shrink: 0; }
.tip-text { font-size: 13px; color: var(--text-primary); line-height: 1.5; }
</style>
