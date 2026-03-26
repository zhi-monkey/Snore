import React from 'react';
import './TopBar.css';

interface TopBarProps {
  title: string;
  subtitle?: string;
}

const TopBar: React.FC<TopBarProps> = ({ title, subtitle }) => {
  const now = new Date();
  const dateStr = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });

  return (
    <div className="topbar">
      <div className="topbar-left">
        <h1 className="topbar-title">{title}</h1>
        {subtitle && <p className="topbar-subtitle">{subtitle}</p>}
      </div>
      <div className="topbar-right">
        <div className="topbar-date">{dateStr}</div>
        <div className="topbar-notifications">
          <button className="notif-btn" title="通知">
            🔔
            <span className="notif-badge">3</span>
          </button>
        </div>
        <div className="topbar-user">
          <div className="user-avatar-sm">王</div>
          <span>王医生</span>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
