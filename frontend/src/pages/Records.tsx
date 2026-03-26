import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import './Records.css';

const PATIENTS = [
  {
    id: 'P001', name: '张三',  gender: '男', age: 45, phone: '138****8001',
    diagnosis: '中度OSAHS', doctor: '王医生', lastVisit: '2026-03-25',
    records: [
      { date: '2026-03-25', type: '睡眠检测', summary: 'AHI=22.5, 中度, 18次呼吸阻塞', severity: '中度' },
      { date: '2026-01-10', type: '门诊就诊', summary: '主诉打鼾加重, 建议行睡眠监测', severity: '' },
      { date: '2025-11-20', type: '复查',     summary: 'AHI=19.2, 轻度改善', severity: '中度' },
    ]
  },
  {
    id: 'P002', name: '李四',  gender: '男', age: 52, phone: '139****2345',
    diagnosis: '正常', doctor: '王医生', lastVisit: '2026-03-24',
    records: [
      { date: '2026-03-24', type: '睡眠检测', summary: 'AHI=5.2, 正常范围', severity: '正常' },
      { date: '2025-09-08', type: '门诊就诊', summary: '体检发现打鼾, 建议监测', severity: '' },
    ]
  },
  {
    id: 'P003', name: '王五',  gender: '男', age: 38, phone: '156****6789',
    diagnosis: '重度OSAHS', doctor: '李医生', lastVisit: '2026-03-24',
    records: [
      { date: '2026-03-24', type: '睡眠检测', summary: 'AHI=38.1, 重度, 34次呼吸阻塞', severity: '重度' },
      { date: '2026-02-15', type: '门诊就诊', summary: '主诉日间嗜睡严重', severity: '' },
      { date: '2025-08-01', type: '睡眠检测', summary: 'AHI=35.7, 重度', severity: '重度' },
    ]
  },
  {
    id: 'P004', name: '赵六',  gender: '女', age: 61, phone: '177****4321',
    diagnosis: '轻度OSAHS', doctor: '王医生', lastVisit: '2026-03-23',
    records: [
      { date: '2026-03-23', type: '睡眠检测', summary: 'AHI=12.7, 轻度', severity: '轻度' },
    ]
  },
  {
    id: 'P005', name: '陈七',  gender: '女', age: 29, phone: '180****5555',
    diagnosis: '正常', doctor: '李医生', lastVisit: '2026-03-22',
    records: [
      { date: '2026-03-22', type: '睡眠检测', summary: 'AHI=3.1, 正常', severity: '正常' },
    ]
  },
  {
    id: 'P006', name: '吴八',  gender: '男', age: 55, phone: '132****7777',
    diagnosis: '重度OSAHS', doctor: '张医生', lastVisit: '2026-03-20',
    records: [
      { date: '2026-03-20', type: '睡眠检测', summary: 'AHI=31.4, 重度', severity: '重度' },
      { date: '2025-12-18', type: 'CPAP治疗', summary: '开始CPAP治疗, 依从性良好', severity: '' },
    ]
  },
];

const levelBadge: Record<string, string> = {
  '正常': 'badge-success', '轻度': 'badge-info',
  '中度': 'badge-warning', '重度': 'badge-danger',
};

type Patient = typeof PATIENTS[0];

const Records: React.FC = () => {
  const [selected, setSelected] = useState<Patient | null>(null);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const filtered = PATIENTS.filter(p =>
    p.name.includes(search) || p.id.includes(search) || p.diagnosis.includes(search)
  );

  return (
    <div>
      <TopBar title="病历管理" subtitle="患者档案与历史病历记录" />

      <div className="records-layout">
        {/* Patient List */}
        <div className="patient-list-panel">
          <div className="card">
            <div className="card-title" style={{ justifyContent: 'space-between' }}>
              <span><span>📁</span> 患者列表</span>
              <button className="btn btn-primary" style={{ fontSize: '12px', padding: '5px 12px' }}
                onClick={() => setShowAdd(true)}>
                ＋ 新建档案
              </button>
            </div>
            <div className="search-box" style={{ marginBottom: 14 }}>
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="搜索患者"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <div className="patient-cards">
              {filtered.map(p => (
                <div
                  key={p.id}
                  className={`patient-card ${selected?.id === p.id ? 'patient-card--active' : ''}`}
                  onClick={() => setSelected(p)}
                >
                  <div className="patient-card-avatar">{p.name[0]}</div>
                  <div className="patient-card-info">
                    <div className="patient-card-name">{p.name}
                      <span className="patient-card-age">{p.gender} · {p.age}岁</span>
                    </div>
                    <div className="patient-card-diag">
                      {p.diagnosis !== '正常'
                        ? <span className={`badge ${levelBadge[p.diagnosis.replace('OSAHS','').trim()] || 'badge-info'}`}>{p.diagnosis}</span>
                        : <span className="badge badge-success">{p.diagnosis}</span>
                      }
                    </div>
                    <div className="patient-card-date">最近就诊：{p.lastVisit}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Patient Detail */}
        <div className="patient-detail-panel">
          {selected ? (
            <div>
              <div className="card patient-header-card">
                <div className="patient-header">
                  <div className="patient-big-avatar">{selected.name[0]}</div>
                  <div className="patient-header-info">
                    <div className="patient-big-name">{selected.name}</div>
                    <div className="patient-meta">
                      <span>{selected.gender}</span>
                      <span>{selected.age}岁</span>
                      <span>📞 {selected.phone}</span>
                      <span>主治：{selected.doctor}</span>
                    </div>
                    <div style={{ marginTop: 8 }}>
                      {selected.diagnosis !== '正常'
                        ? <span className={`badge ${levelBadge[selected.diagnosis.replace('OSAHS','').trim()] || 'badge-info'}`} style={{ fontSize: '13px', padding: '4px 12px' }}>{selected.diagnosis}</span>
                        : <span className="badge badge-success" style={{ fontSize: '13px', padding: '4px 12px' }}>{selected.diagnosis}</span>
                      }
                    </div>
                  </div>
                  <div className="patient-id-chip">
                    ID: {selected.id}
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-title"><span>📋</span> 历史病历记录</div>
                <div className="timeline">
                  {selected.records.map((rec, i) => (
                    <div key={i} className="timeline-item">
                      <div className="timeline-dot" />
                      <div className="timeline-content">
                        <div className="timeline-header">
                          <span className="timeline-type">{rec.type}</span>
                          <span className="timeline-date">{rec.date}</span>
                        </div>
                        <div className="timeline-summary">{rec.summary}</div>
                        {rec.severity && (
                          <span className={`badge ${levelBadge[rec.severity]}`} style={{ marginTop: 4 }}>
                            {rec.severity}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card">
                <div className="card-title"><span>⚙️</span> 操作</div>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                  <button className="btn btn-primary">🎙️ 发起新检测</button>
                  <button className="btn btn-accent">📋 查看全部报告</button>
                  <button className="btn btn-outline">✏️ 编辑患者信息</button>
                  <button className="btn btn-outline">📤 导出病历</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card empty-state">
              <div className="empty-icon">👈</div>
              <div className="empty-title">请选择患者</div>
              <div className="empty-desc">从左侧列表选择患者以查看病历详情</div>
            </div>
          )}
        </div>
      </div>

      {showAdd && (
        <div className="report-modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="report-modal" style={{ maxWidth: 500 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">新建患者档案</div>
              <button className="modal-close" onClick={() => setShowAdd(false)}>✕</button>
            </div>
            <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="form-group"><label>姓名</label><input type="text" placeholder="请输入姓名" /></div>
              <div className="form-group"><label>性别</label><select><option>男</option><option>女</option></select></div>
              <div className="form-group"><label>年龄</label><input type="number" placeholder="年龄" /></div>
              <div className="form-group"><label>联系电话</label><input type="text" placeholder="手机号" /></div>
              <div className="form-group" style={{ gridColumn: '1/-1' }}>
                <label>既往病史</label>
                <input type="text" placeholder="如：高血压、糖尿病" />
              </div>
              <div className="form-group" style={{ gridColumn: '1/-1' }}>
                <label>主治医师</label>
                <select><option>王医生</option><option>李医生</option><option>张医生</option></select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={() => setShowAdd(false)}>✅ 保存档案</button>
              <button className="btn btn-outline" onClick={() => setShowAdd(false)}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Records;
