import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import './HealthSearch.css';

const KNOWLEDGE_BASE = [
  {
    id: 1,
    title: '阻塞性睡眠呼吸暂停低通气综合征（OSAHS）',
    category: '疾病百科',
    icon: '🫁',
    summary: '一种以睡眠中反复发生的上气道塌陷为特征的睡眠呼吸疾病，可导致间歇性低氧血症。',
    content: `阻塞性睡眠呼吸暂停（OSA）是最常见的睡眠呼吸障碍，以睡眠期间上气道部分或完全塌陷为特征。主要症状包括：大声打鼾、夜间窒息/喘气、日间嗜睡、晨起头痛、注意力难以集中等。`,
    tags: ['OSAHS', '打鼾', '睡眠障碍', '低氧血症']
  },
  {
    id: 2,
    title: 'AHI 指数解读',
    category: '检测指标',
    icon: '📊',
    summary: '呼吸暂停低通气指数（AHI）是评估睡眠呼吸暂停严重程度的核心指标，以每小时发生次数计算。',
    content: `AHI（Apnea-Hypopnea Index）分级标准：
• 正常：AHI < 5 次/小时
• 轻度：5 ≤ AHI < 15 次/小时
• 中度：15 ≤ AHI < 30 次/小时  
• 重度：AHI ≥ 30 次/小时

AHI 越高，表明睡眠呼吸障碍越严重，需要及时干预治疗。`,
    tags: ['AHI', '诊断标准', '睡眠监测']
  },
  {
    id: 3,
    title: 'CPAP 治疗（持续气道正压通气）',
    category: '治疗方法',
    icon: '⚕️',
    summary: 'CPAP 是中重度睡眠呼吸暂停的一线治疗方案，通过持续正压防止气道塌陷。',
    content: `CPAP（Continuous Positive Airway Pressure）治疗是通过面罩向气道输送持续正压气流，维持上气道开放，防止睡眠中气道塌陷。适应证为：中重度 OSAHS（AHI≥15）或轻度但有显著日间嗜睡者。正确使用 CPAP 可显著改善睡眠质量和日间功能。`,
    tags: ['CPAP', '治疗', '气道正压']
  },
  {
    id: 4,
    title: '血氧饱和度（SpO₂）监测',
    category: '检测指标',
    icon: '💉',
    summary: '血氧饱和度是反映血液携氧能力的重要指标，睡眠期间 SpO₂ 下降提示存在缺氧事件。',
    content: `正常人血氧饱和度应维持在 95%-100%。睡眠呼吸暂停患者在阻塞事件发生时，SpO₂ 会出现间歇性下降（即氧减事件）。
• SpO₂ ≥ 95%：正常
• SpO₂ 90%-95%：轻度低氧
• SpO₂ < 90%：需要引起重视`,
    tags: ['SpO₂', '血氧', '低氧血症']
  },
  {
    id: 5,
    title: '打鼾与睡眠呼吸暂停的关系',
    category: '健康科普',
    icon: '😴',
    summary: '打鼾是睡眠呼吸暂停最常见的症状，但并非所有打鼾者都患有 OSAHS。',
    content: `打鼾是气流通过狭窄气道时产生的振动声音，是 OSAHS 的重要预警信号。流行病学数据显示：约 40% 的男性和 20% 的女性有习惯性打鼾，其中约一半存在 OSAHS。高危人群：肥胖、颈围大、下颌后缩、饮酒、服用镇静药物者。`,
    tags: ['打鼾', '睡眠健康', '预防']
  },
  {
    id: 6,
    title: '睡眠呼吸暂停的危险因素',
    category: '健康科普',
    icon: '⚠️',
    summary: '了解危险因素有助于早期识别高风险人群，进行预防性干预。',
    content: `主要危险因素包括：
1. 肥胖：BMI > 28 显著增加 OSAHS 风险
2. 年龄与性别：中年男性发病率最高
3. 解剖因素：扁桃体肥大、小下颌、鼻中隔偏曲
4. 生活方式：吸烟、饮酒、镇静药物
5. 遗传因素：有家族史者风险增加
6. 合并疾病：高血压、糖尿病、甲减等`,
    tags: ['危险因素', '预防', '肥胖', '高血压']
  },
];

const CATEGORIES = ['全部', '疾病百科', '检测指标', '治疗方法', '健康科普'];

const HOT_SEARCHES = ['AHI指数', 'CPAP治疗', '睡眠监测', '血氧饱和度', '打鼾危害', '睡眠质量改善'];

const HealthSearch: React.FC = () => {
  const [query, setQuery]       = useState('');
  const [category, setCategory] = useState('全部');
  const [expanded, setExpanded] = useState<number | null>(null);
  const [searched, setSearched] = useState(false);

  const doSearch = (q?: string) => {
    if (q !== undefined) setQuery(q);
    setSearched(true);
  };

  const filtered = KNOWLEDGE_BASE.filter(item => {
    const q = query.toLowerCase();
    const matchQ = !searched || !q || item.title.includes(query) || item.summary.includes(query) ||
      item.tags.some(t => t.toLowerCase().includes(q)) || item.content.includes(query);
    const matchC = category === '全部' || item.category === category;
    return matchQ && matchC;
  });

  return (
    <div>
      <TopBar title="健康搜索" subtitle="睡眠健康知识库，快速查阅相关医学信息" />

      {/* Search Bar */}
      <div className="card search-hero">
        <div className="hero-title">🔍 搜索健康知识</div>
        <div className="hero-search-bar">
          <input
            type="text"
            className="hero-input"
            placeholder="搜索疾病、症状、治疗方法..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && doSearch()}
          />
          <button className="btn btn-primary hero-btn" onClick={() => doSearch()}>搜索</button>
        </div>
        <div className="hot-searches">
          <span className="hot-label">🔥 热门搜索：</span>
          {HOT_SEARCHES.map(h => (
            <button key={h} className="hot-tag" onClick={() => { setQuery(h); doSearch(h); }}>{h}</button>
          ))}
        </div>
      </div>

      {/* Category Filter */}
      <div className="card" style={{ padding: '14px 20px', marginBottom: 16 }}>
        <div className="filter-group" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>分类：</span>
          {CATEGORIES.map(c => (
            <button
              key={c}
              className={`filter-btn ${category === c ? 'filter-btn--active' : ''}`}
              onClick={() => setCategory(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="knowledge-list">
        {filtered.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>😕</div>
            <div style={{ fontSize: 16, fontWeight: 600 }}>未找到相关结果</div>
            <div style={{ fontSize: 13, marginTop: 6 }}>请尝试其他关键词</div>
          </div>
        ) : filtered.map(item => (
          <div key={item.id} className="card knowledge-card">
            <div className="knowledge-header" onClick={() => setExpanded(expanded === item.id ? null : item.id)}>
              <div className="knowledge-icon">{item.icon}</div>
              <div className="knowledge-main">
                <div className="knowledge-title">{item.title}</div>
                <div className="knowledge-summary">{item.summary}</div>
                <div className="knowledge-tags">
                  <span className={`badge badge-info`} style={{ marginRight: 4, fontSize: 11 }}>{item.category}</span>
                  {item.tags.map(t => (
                    <span key={t} className="knowledge-tag">{t}</span>
                  ))}
                </div>
              </div>
              <div className="knowledge-expand">
                {expanded === item.id ? '▲ 收起' : '▼ 展开'}
              </div>
            </div>
            {expanded === item.id && (
              <div className="knowledge-content">
                <pre className="knowledge-pre">{item.content}</pre>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Health Tips */}
      <div className="card">
        <div className="card-title"><span>💡</span> 睡眠健康小贴士</div>
        <div className="tips-grid">
          {[
            { icon: '🛏️', tip: '保持规律作息，每天同一时间上床和起床' },
            { icon: '🏃', tip: '规律运动有助于改善睡眠质量，但避免睡前2小时剧烈运动' },
            { icon: '🍷', tip: '睡前避免饮酒，酒精会加重气道塌陷和打鼾' },
            { icon: '⚖️', tip: '控制体重，BMI 超标是 OSAHS 的重要危险因素' },
            { icon: '🔄', tip: '尝试侧卧入睡，可减少气道阻塞风险' },
            { icon: '🏥', tip: '长期打鼾伴日间嗜睡者，建议及时就医检查' },
          ].map((t, i) => (
            <div key={i} className="tip-item">
              <span className="tip-icon">{t.icon}</span>
              <span className="tip-text">{t.tip}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HealthSearch;
