import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const navItem = (path, icon, label) => (
    <div
      className={`nav-item${isActive(path) ? ' active' : ''}`}
      onClick={() => navigate(path)}
      style={{ cursor: 'pointer' }}
    >
      <span className="nav-icon">{icon}</span> {label}
    </div>
  );

  // Build user initials from name or email
  const displayName = user?.full_name || user?.email?.split('@')[0] || 'You';
  const initials = displayName
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
        <div className="brand-logo">📚</div>
        <span className="brand-text">Koala</span>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">Main</div>
        {navItem('/', '🏠', 'Dashboard')}
        {navItem('/notes', '📝', 'Notes')}
        {navItem('/graph', '🕸️', 'Note Graph')}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">Tracking</div>
        {navItem('/goals', '🎯', 'Goals')}
        {navItem('/gpa', '🎓', 'GPA Calculator')}
        {navItem('/profile', '📊', 'Insights & Profile')}
        {navItem('/retrospective', '📋', 'Retrospective')}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-label">Account</div>
        {navItem('/settings', '⚙️', 'Settings')}
        <div
          className="nav-item"
          onClick={handleLogout}
          style={{ cursor: 'pointer', color: 'var(--red)' }}
        >
          <span className="nav-icon">🚪</span> Sign Out
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-card">
          <div className="user-avatar">{initials || '?'}</div>
          <div className="user-info">
            <div className="user-name">{displayName}</div>
            <div className="user-role">
              {user?.plan === 'pro' ? '✨ Pro Plan' : 'Free Plan'}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
