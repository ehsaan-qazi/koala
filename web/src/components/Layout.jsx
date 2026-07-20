import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Derive breadcrumb label from location
  const getBreadcrumb = () => {
    const path = window.location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/courses/')) return 'Course Detail';
    if (path.startsWith('/notes')) return 'Notes';
    if (path.startsWith('/goals')) return 'Goals';
    if (path.startsWith('/gpa')) return 'GPA Calculator';
    if (path.startsWith('/profile')) return 'Insights & Profile';
    if (path.startsWith('/retrospective')) return 'Retrospective';
    if (path.startsWith('/settings')) return 'Settings';
    if (path.startsWith('/graph')) return 'Note Graph';
    return 'Koala';
  };

  const streakCount = user?.streak_count ?? null;

  return (
    <>
      <Sidebar />
      <div className="main">
        <header className="topbar">
          <div className="breadcrumb">
            <span className="current" id="breadcrumb-text">{getBreadcrumb()}</span>
          </div>
          <div className="topbar-actions">
            {streakCount !== null && (
              <div
                className="streak-pill"
                onClick={() => navigate('/')}
                title="Activity Streak"
                style={{ cursor: 'pointer' }}
              >
                🔥 {streakCount} days
              </div>
            )}
            <div
              className="topbar-btn"
              title="Settings"
              onClick={() => navigate('/settings')}
              style={{ cursor: 'pointer' }}
            >
              ⚙️
            </div>
          </div>
        </header>
        <div className="content">
          <Outlet />
        </div>
      </div>
    </>
  );
}
