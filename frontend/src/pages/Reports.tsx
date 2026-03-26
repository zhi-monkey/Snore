import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import './Reports.css';

const reports = [
  {
    id: 'RPT-20260325-001', patient: '张三',  age: 45, date: '2026-03-25',
    ahi: 22.5, events: 18, duration: '7h 32min', spo2Avg: 93.4, spo2Min: 87,
    severity: '中度', status: '待复查', doctor: '王医生'
  },
  {
    id: 'RPT-20260324-002', patient: '李四',  age: 52, date: '2026-03-24',
    ahi: 5.2,  events: 3,  duration: '6h 45min', spo2Avg: 96.8, spo2Min: 93,
    severity: '正常', status: '已完成', doctor: '王医生'
  },
  {
    id: 'RPT-20260324-003', patient: '王五',  age: 38, date: '2026-03-24',
    ahi: 38.1, events: 34, duration: '8h 10min', spo2Avg: 90.1, spo2Min: 82,
    severity: '重度', status: '治疗中', doctor: '李医生'
  },
  {
    id: 'RPT-20260323-004', patient: '赵六',  age: 61, date: '2026-03-23',
    ahi: 12.7, events: 9,  duration: '7h 05min', spo2Avg: 94.5, spo2Min: 89,
    severity: '轻度', status: '已完成', doctor: '王医生'
  },
  {
    id: 'RPT-20260322-005', patient: '陈七',  age: 29, date: '2026-03-22',
    ahi: 3.1,  events: 1,  duration: '7h 55min', spo2Avg: 97.2, spo2Min: 94,
    severity: '正常', status: '已完成', doctor: '李医生'
  },
  {
    id: 'RPT-20260320-006', patient: '吴八',  age: 55, date: '2026-03-20',
    ahi: 31.4, events: 28, duration: '6h 30min', spo2Avg: 91.3, spo2Min: 84,
    severity: '重度', status: '治疗中', doctor: '张医生'
  },
];

const levelBadge: Record<string, string> = {
  '正常': 'badge-success', '轻度': 'badge-info',
  '中度': 'badge-warning', '重度': 'badge-danger',
};
const statusBadge: Record<string, string> = {
  '待复查': 'badge-warning', '已完成': 'badge-success', '治疗中': 'badge-info',
};

const APNEA_WINS = [
  { left: '15%', width: '10%', label: '事件1' },
  { left: '40%', width: '10%', label: '事件2' },
  { left: '70%', width: '12.5%', label: '事件3' },
];

type Report = typeof reports[0];

const ReportDetail: React.FC<{ report: Report; onClose: () => void }> = ({ report, onClose }) => (
  <div className="report-modal-overlay" onClick={onClose}>
    <div className="report-modal" onClick={e => e.stopPropagation()}>
      <div className="modal-header">
        <div>
          <div className="modal-title">检测报告详情</div>
          <div className="modal-id">{report.id}</div>
        </div>
        <button className="modal-close" onClick={onClose}>✕</button>
      </div>

      {/* Patient Info */}
      <div className="modal-section">
        <div className="section-title">患者基本信息</div>
        <div className="info-grid">
          <div><span className="info-key">姓名</span><span className="info-val">{report.patient}</span></div>
          <div><span className="info-key">年龄</span><span className="info-val">{report.age}岁</span></div>
          <div><span className="info-key">检测日期</span><span className="info-val">{report.date}</span></div>
          <div><span className="info-key">主治医师</span><span className="info-val">{report.doctor}</span></div>
          <div><span className="info-key">监测时长</span><span className="info-val">{report.duration}</span></div>
          <div><span className="info-key">严重程度</span><span className="info-val">
            <span className={`badge ${levelBadge[report.severity]}`}>{report.severity}</span>
          </span></div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="modal-section">
        <div className="section-title">核心指标</div>
        <div className="metrics-row">
          <div className="metric-box metric-box--primary">
            <div className="metric-val">{report.ahi}</div>
            <div className="metric-name">AHI 指数</div>
            <div className="metric-unit">次/小时</div>
          </div>
          <div className="metric-box">
            <div className="metric-val">{report.events}</div>
            <div className="metric-name">阻塞事件</div>
            <div className="metric-unit">次</div>
          </div>
          <div className="metric-box">
            <div className="metric-val">{report.spo2Avg}%</div>
            <div className="metric-name">平均血氧</div>
            <div className="metric-unit">SpO₂</div>
          </div>
          <div className="metric-box metric-box--danger">
            <div className="metric-val">{report.spo2Min}%</div>
            <div className="metric-name">最低血氧</div>
            <div className="metric-unit">SpO₂</div>
          </div>
        </div>
      </div>

      {/* Mini Spectrogram */}
      <div className="modal-section">
        <div className="section-title">睡眠呼吸频谱（缩略图）</div>
        <div className="mini-spectrogram-wrap">
          <svg viewBox="0 0 200 40" preserveAspectRatio="none" className="mini-spec-svg">
            {Array.from({ length: 6 }, (_, fi) =>
              Array.from({ length: 200 }, (_, ti) => {
                const apnea = (ti >= 30 && ti <= 50) || (ti >= 80 && ti <= 100) || (ti >= 140 && ti <= 165);
                const v = apnea ? 0.1 + Math.random() * 0.15 : 0.4 + Math.random() * 0.5;
                return (
                  <rect key={`${fi}-${ti}`} x={ti} y={fi * 7} width={1} height={7}
                    fill={apnea ? `rgba(229,62,62,${0.4 + v * 0.6})` : `rgba(43,108,176,${0.1 + v * 0.9})`} />
                );
              })
            )}
          </svg>
          {APNEA_WINS.map((w, i) => (
            <div key={i} className="mini-marker" style={{ left: w.left, width: w.width }}>
              <span className="mini-marker-label">{w.label}</span>
            </div>
          ))}
          <div className="mini-x-labels">
            <span>0</span><span>2h</span><span>4h</span><span>6h</span><span>7h32m</span>
          </div>
        </div>
      </div>

      {/* Conclusion */}
      <div className="modal-section">
        <div className="section-title">诊断结论与建议</div>
        <div className="conclusion-box">
          <p>患者监测期间共检测到 <strong>{report.events}</strong> 次呼吸阻塞事件，AHI 指数为 <strong>{report.ahi}</strong> 次/小时，
          诊断为<strong>{report.severity}睡眠呼吸暂停低通气综合征（OSAHS）</strong>。
          最低血氧饱和度为 <strong>{report.spo2Min}%</strong>，存在间歇性低氧血症。</p>
          {report.severity === '重度' || report.severity === '中度' ? (
            <p style={{ marginTop: 8 }}>建议：立即就诊，考虑使用持续气道正压通气（CPAP）治疗，同时评估是否需要手术干预。</p>
          ) : (
            <p style={{ marginTop: 8 }}>建议：加强随访，注意体重控制，改善睡眠体位，定期复查。</p>
          )}
        </div>
      </div>

      <div className="modal-actions">
        <button className="btn btn-primary">📤 导出 PDF</button>
        <button className="btn btn-accent">🖨️ 打印报告</button>
        <button className="btn btn-outline" onClick={onClose}>关闭</button>
      </div>
    </div>
  </div>
);

const Reports: React.FC = () => {
  const [selected, setSelected] = useState<Report | null>(null);
  const [search, setSearch] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('全部');

  const filtered = reports.filter(r => {
    const matchSearch = r.patient.includes(search) || r.id.includes(search);
    const matchSev = filterSeverity === '全部' || r.severity === filterSeverity;
    return matchSearch && matchSev;
  });

  return (
    <div>
      <TopBar title="检测报告" subtitle="查看所有睡眠呼吸检测报告" />

      <div className="card">
        <div className="reports-toolbar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="搜索患者姓名 / 报告编号"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <span className="filter-label">严重程度：</span>
            {['全部', '正常', '轻度', '中度', '重度'].map(s => (
              <button
                key={s}
                className={`filter-btn ${filterSeverity === s ? 'filter-btn--active' : ''}`}
                onClick={() => setFilterSeverity(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="reports-count">共 {filtered.length} 份报告</div>

        <table className="data-table">
          <thead>
            <tr>
              <th>报告编号</th>
              <th>患者</th>
              <th>检测日期</th>
              <th>AHI 指数</th>
              <th>阻塞事件</th>
              <th>监测时长</th>
              <th>严重程度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(r => (
              <tr key={r.id}>
                <td><code style={{ fontSize: '11px' }}>{r.id}</code></td>
                <td><strong>{r.patient}</strong> <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{r.age}岁</span></td>
                <td>{r.date}</td>
                <td><strong>{r.ahi}</strong></td>
                <td>{r.events}</td>
                <td>{r.duration}</td>
                <td><span className={`badge ${levelBadge[r.severity]}`}>{r.severity}</span></td>
                <td><span className={`badge ${statusBadge[r.status]}`}>{r.status}</span></td>
                <td>
                  <button className="btn btn-primary" style={{ padding: '4px 12px', fontSize: '12px' }}
                    onClick={() => setSelected(r)}>查看详情</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && <ReportDetail report={selected} onClose={() => setSelected(null)} />}
    </div>
  );
};

export default Reports;
