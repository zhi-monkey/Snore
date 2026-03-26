import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const NAV_ITEMS = [
  { path: '/',          label: '系统主页',   icon: '🏠' },
  { path: '/upload',    label: '睡眠检测',   icon: '🎙️' },
  { path: '/reports',   label: '检测报告',   icon: '📋' },
  { path: '/records',   label: '病历管理',   icon: '📁' },
  { path: '/search',    label: '健康搜索',   icon: '🔍' },
];

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon">🫁</span>
        <div>
          <div className="brand-name">SnoringCare</div>
          <div className="brand-sub">睡眠健康管理平台</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'nav-item--active' : ''}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">王</div>
          <div>
            <div className="user-name">王医生</div>
            <div className="user-role">主治医师</div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
