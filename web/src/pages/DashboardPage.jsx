import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../api/client';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  
  useEffect(() => {
    apiFetch('/courses')
      .then(setCourses)
      .catch(console.error);
  }, []);

  return (
    <div className="page active" id="page-dashboard">
<div className="page-header">
<div>
<div className="page-title">Good afternoon, Alex 👋</div>
<div className="page-subtitle">Fall 2026 · Week 6 of 16 · 2 assignments due this week</div>
</div>
<button className="btn btn-primary" onClick="navigate('courses')">+ New Course</button>
</div>
{/* Stats Row */}
<div className="stats-row">
<div className="stat-card">
<div className="stat-card-top">
<div className="stat-card-label">Active Courses</div>
<div className="stat-card-icon">📖</div>
</div>
<div className="stat-card-value">4</div>
<div className="stat-card-sub">Fall 2026 semester</div>
</div>
<div className="stat-card">
<div className="stat-card-top">
<div className="stat-card-label">Topics Completed</div>
<div className="stat-card-icon">✅</div>
</div>
<div className="stat-card-value">13<span >/36</span></div>
<div className="stat-card-sub">36% coverage overall</div>
</div>
<div className="stat-card">
<div className="stat-card-top">
<div className="stat-card-label">Upcoming Deadlines</div>
<div className="stat-card-icon">⏰</div>
</div>
<div className="stat-card-value" >3</div>
<div className="stat-card-sub">Next 7 days</div>
</div>
<div className="stat-card">
<div className="stat-card-top">
<div className="stat-card-label">Unresolved Placeholders</div>
<div className="stat-card-icon">⚠️</div>
</div>
<div className="stat-card-value" >5</div>
<div className="stat-card-sub">Fill in when announced</div>
</div>
</div>
{/* Streak Display */}
<div className="streak-display">
<div className="streak-item">
<div className="streak-icon">🔥</div>
<div>
<div className="streak-count" >12</div>
<div className="streak-info-label">Day Activity Streak</div>
<div className="streak-record">Best: 28 days</div>
</div>
</div>
<div ></div>
<div className="streak-item">
<div className="streak-icon">🎯</div>
<div>
<div className="streak-count" >5</div>
<div className="streak-info-label">On-Time Submissions</div>
<div className="streak-record">Best: 8 in a row</div>
</div>
</div>
<div >
<div >
            ⚡ Log an activity today to keep your streak!<br/>
<span >Fill in ML501 placeholder →</span>
</div>
</div>
</div>
<div className="dash-grid">
{/* Upcoming Deadlines */}
<div className="card">
<div className="card-header">
<div className="card-title">📅 Due This Week</div>
<button className="btn btn-ghost btn-sm">View all</button>
</div>
<div className="deadline-row">
<div className="deadline-dot" ></div>
<div className="deadline-info">
<div className="deadline-title">Assignment 2 — ER Diagram</div>
<div className="deadline-meta"><span>📖 DB401</span> <span className="badge badge-red">Overdue</span></div>
</div>
<div className="deadline-due" >Jul 8</div>
</div>
<div className="deadline-row">
<div className="deadline-dot" ></div>
<div className="deadline-info">
<div className="deadline-title">Quiz 3 — Requirements</div>
<div className="deadline-meta"><span>📖 SE301</span> <span className="badge badge-amber">In Progress</span></div>
</div>
<div className="deadline-due" >Jul 12</div>
</div>
<div className="deadline-row">
<div className="deadline-dot" ></div>
<div className="deadline-info">
<div className="deadline-title">Lab Report 2</div>
<div className="deadline-meta"><span>📖 CN201</span> <span className="badge badge-gray">Pending</span></div>
</div>
<div className="deadline-due">Jul 15</div>
</div>
<div className="deadline-row">
<div className="deadline-dot" ></div>
<div className="deadline-info">
<div className="deadline-title">Project Proposal</div>
<div className="deadline-meta"><span>📖 ML501</span> <span className="badge badge-gray">Pending</span></div>
</div>
<div className="deadline-due">Jul 18</div>
</div>
<div className="deadline-row">
<div className="deadline-dot" ></div>
<div className="deadline-info">
<div className="deadline-title">Midterm Exam <span >📌 Date TBC</span></div>
<div className="deadline-meta"><span>📖 SE301</span> <span className="badge badge-amber" >Placeholder</span></div>
</div>
<div className="deadline-due" >— TBA</div>
</div>
</div>
{/* Topic Coverage per Course */}
<div className="card">
<div className="card-header">
<div className="card-title">📚 Topic Coverage</div>
<span className="badge badge-gray">Fall 2026</span>
</div>
<div className="course-coverage">
<div className="course-coverage-top">
<span className="course-coverage-name">Software Engineering · SE301</span>
<span className="course-coverage-count" >7/10</span>
</div>
<div className="progress-bar"><div className="progress-fill green" ></div></div>
</div>
<div className="course-coverage">
<div className="course-coverage-top">
<span className="course-coverage-name">Database Systems · DB401</span>
<span className="course-coverage-count" >4/8</span>
</div>
<div className="progress-bar"><div className="progress-fill" ></div></div>
</div>
<div className="course-coverage">
<div className="course-coverage-top">
<span className="course-coverage-name">Machine Learning · ML501</span>
<span className="course-coverage-count" >2/12</span>
</div>
<div className="progress-bar"><div className="progress-fill amber" ></div></div>
</div>
<div className="course-coverage">
<div className="course-coverage-top">
<span className="course-coverage-name">Computer Networks · CN201</span>
<span className="course-coverage-count" >0/6</span>
</div>
<div className="progress-bar"><div className="progress-fill" ></div></div>
</div>
<div >
<div className="card-title" >🎯 Goal Progress</div>
<div >
<div >
<span>Get B+ in all courses</span>
<span className="badge badge-blue">Active</span>
</div>
<div >
<span>Submit assignments 2 days early</span>
<span className="badge badge-green">✓ Complete</span>
</div>
<div >
<span>Complete all readings before class</span>
<span className="badge badge-blue">Active</span>
</div>
</div>
</div>
</div>
</div>
{/* Activity Heatmap */}
<div className="card">
<div className="card-header">
<div className="card-title">📈 Activity Heatmap — Last 12 Weeks</div>
<div >
            Less
            <div ></div>
<div ></div>
<div ></div>
<div ></div>
            More
          </div>
</div>
<div className="heatmap-grid" id="heatmap"></div>
</div>
</div>
  );
}
