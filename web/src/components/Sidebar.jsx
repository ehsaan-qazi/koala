import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  
  return (
    <aside className="sidebar">
<div className="sidebar-brand" onClick="navigate('dashboard')">
<div className="brand-logo">📚</div>
<span className="brand-text">Koala</span>
</div>
<div className="sidebar-section">
<div className="sidebar-label">Main</div>
<div className="nav-item active" id="nav-dashboard" onClick="navigate('dashboard')">
<span className="nav-icon">🏠</span> Dashboard
    </div>
<div className="nav-item" id="nav-courses" onClick="navigate('courses')">
<span className="nav-icon">📖</span> My Courses
    </div>
<div className="nav-item" id="nav-notes" onClick="navigate('notes')">
<span className="nav-icon">📝</span> Notes
    </div>
<div className="nav-item" id="nav-graph" onClick="navigate('graph')">
<span className="nav-icon">🕸️</span> Note Graph
    </div>
</div>
<div className="sidebar-section">
<div className="sidebar-label">Tracking</div>
<div className="nav-item" id="nav-goals" onClick="navigate('goals')">
<span className="nav-icon">🎯</span> Goals
    </div>
<div className="nav-item" id="nav-gpa" onClick="navigate('gpa')">
<span className="nav-icon">🎓</span> GPA Calculator
    </div>
<div className="nav-item" id="nav-profile" onClick="navigate('profile')">
<span className="nav-icon">📊</span> Insights &amp; Profile
    </div>
<div className="nav-item" id="nav-retrospective" onClick="navigate('retrospective')">
<span className="nav-icon">📋</span> Retrospective
    </div>
</div>
<div className="sidebar-section">
<div className="sidebar-label">Preview</div>
<div className="nav-item" id="nav-mobile" onClick="navigate('mobile')">
<span className="nav-icon">📱</span> Mobile View
    </div>
<div className="nav-item" id="nav-assessment" onClick="navigate('assessment')">
<span className="nav-icon">✍️</span> Self-Assessment
    </div>
</div>
<div className="sidebar-footer">
<div className="user-card">
<div className="user-avatar">AJ</div>
<div className="user-info">
<div className="user-name">Alex Johnson</div>
<div className="user-role">Fall 2026 · 4 Courses</div>
</div>
</div>
</div>
</aside>
  );
}
