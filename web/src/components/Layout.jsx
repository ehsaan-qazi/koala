import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <>
      <Sidebar />
      <div className="main">
        <header className="topbar">
<div className="breadcrumb">
<span className="current" id="breadcrumb-text">Dashboard</span>
</div>
<div className="topbar-actions">
<div className="streak-pill" onClick="navigate('dashboard')" title="Activity Streak">🔥 12 days</div>
<div className="topbar-btn" title="Search">🔍</div>
<div className="topbar-btn" title="Notifications">🔔</div>
<div className="topbar-btn" title="Settings">⚙️</div>
</div>
</header>
        <div className="content">
          <Outlet />
        </div>
      </div>
    </>
  );
}
