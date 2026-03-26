import React from 'react';
import { useNavigate } from 'react-router-dom';
import TopBar from '../components/TopBar';
import {
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import './Home.css';

const weeklyData = [
  { day: '周一', ahi: 12, spo2: 94 },
  { day: '周二', ahi: 8,  spo2: 96 },
  { day: '周三', ahi: 15, spo2: 92 },
  { day: '周四', ahi: 6,  spo2: 97 },
  { day: '周五', ahi: 10, spo2: 95 },
  { day: '周六', ahi: 18, spo2: 91 },
  { day: '周日', ahi: 7,  spo2: 96 },
];

const severityData = [
  { name: '正常', value: 45 },
  { name: '轻度', value: 30 },
  { name: '中度', value: 15 },
  { name: '重度', value: 10 },
];

const COLORS = ['#38a169', '#38b2ac', '#dd6b20', '#e53e3e'];

const recentPatients = [
  { id: 'P001', name: '张三',   age: 45, ahi: 22.5, level: '中度', date: '2026-03-25', status: '待复查' },
  { id: 'P002', name: '李四',   age: 52, ahi: 5.2,  level: '正常', date: '2026-03-24', status: '已完成' },
  { id: 'P003', name: '王五',   age: 38, ahi: 38.1, level: '重度', date: '2026-03-24', status: '治疗中' },
  { id: 'P004', name: '赵六',   age: 61, ahi: 12.7, level: '轻度', date: '2026-03-23', status: '已完成' },
  { id: 'P005', name: '陈七',   age: 29, ahi: 3.1,  level: '正常', date: '2026-03-22', status: '已完成' },
];

const statusBadge: Record<string, string> = {
  '待复查': 'badge-warning',
  '已完成': 'badge-success',
  '治疗中': 'badge-info',
};

const levelBadge: Record<string, string> = {
  '正常': 'badge-success',
  '轻度': 'badge-info',
  '中度': 'badge-warning',
  '重度': 'badge-danger',
};

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <TopBar title="系统主页" subtitle="欢迎使用 SnoringCare 睡眠健康管理平台" />

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card stat-card--blue">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <div className="stat-value">1,248</div>
            <div className="stat-label">总患者数</div>
            <div className="stat-trend trend-up">↑ 12% 本月</div>
          </div>
        </div>
        <div className="stat-card stat-card--teal">
          <div className="stat-icon">🎙️</div>
          <div className="stat-info">
            <div className="stat-value">86</div>
            <div className="stat-label">本月检测</div>
            <div className="stat-trend trend-up">↑ 8% 上月</div>
          </div>
        </div>
        <div className="stat-card stat-card--orange">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <div className="stat-value">23</div>
            <div className="stat-label">待处理报告</div>
            <div className="stat-trend trend-down">↓ 3 较昨日</div>
          </div>
        </div>
        <div className="stat-card stat-card--green">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">94.2%</div>
            <div className="stat-label">检测准确率</div>
            <div className="stat-trend trend-up">↑ 0.3%</div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        <div className="card chart-card-wide">
          <div className="card-title">
            <span>📈</span> 近7日 AHI 指数 & 血氧饱和度趋势
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={weeklyData}>
              <defs>
                <linearGradient id="colorAhi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2b6cb0" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2b6cb0" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorSpo2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38b2ac" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#38b2ac" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="ahi"  stroke="#2b6cb0" fill="url(#colorAhi)"  name="AHI指数"    strokeWidth={2} />
              <Area type="monotone" dataKey="spo2" stroke="#38b2ac" fill="url(#colorSpo2)" name="血氧饱和度%" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card-narrow">
          <div className="card-title">
            <span>🍕</span> 患者病情分布
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
                dataKey="value"
              >
                {severityData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => `${v}人`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Patients */}
      <div className="card">
        <div className="card-title" style={{ justifyContent: 'space-between' }}>
          <span><span>📋</span> 最近检测患者</span>
          <button className="btn btn-outline" onClick={() => navigate('/records')}>查看全部</button>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>患者ID</th>
              <th>姓名</th>
              <th>年龄</th>
              <th>AHI指数</th>
              <th>严重程度</th>
              <th>检测日期</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {recentPatients.map(p => (
              <tr key={p.id}>
                <td><code>{p.id}</code></td>
                <td><strong>{p.name}</strong></td>
                <td>{p.age}</td>
                <td>{p.ahi}</td>
                <td><span className={`badge ${levelBadge[p.level]}`}>{p.level}</span></td>
                <td>{p.date}</td>
                <td><span className={`badge ${statusBadge[p.status]}`}>{p.status}</span></td>
                <td>
                  <button className="btn btn-primary" style={{ padding: '4px 12px', fontSize: '12px' }}
                    onClick={() => navigate('/reports')}>
                    查看报告
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <div className="card quick-action-card" onClick={() => navigate('/upload')}>
          <div className="qa-icon qa-icon--blue">🎙️</div>
          <div className="qa-text">
            <div className="qa-title">新建检测</div>
            <div className="qa-desc">上传睡眠音频，开始分析</div>
          </div>
          <span className="qa-arrow">→</span>
        </div>
        <div className="card quick-action-card" onClick={() => navigate('/records')}>
          <div className="qa-icon qa-icon--teal">📁</div>
          <div className="qa-text">
            <div className="qa-title">病历管理</div>
            <div className="qa-desc">查看和管理患者病历</div>
          </div>
          <span className="qa-arrow">→</span>
        </div>
        <div className="card quick-action-card" onClick={() => navigate('/search')}>
          <div className="qa-icon qa-icon--green">🔍</div>
          <div className="qa-text">
            <div className="qa-title">健康搜索</div>
            <div className="qa-desc">查询健康知识与病情</div>
          </div>
          <span className="qa-arrow">→</span>
        </div>
      </div>
    </div>
  );
};

export default Home;
