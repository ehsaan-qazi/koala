import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/login.css';

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState('login');
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const handleGoogle = async () => {
    try {
      await loginWithGoogle();
    } catch (err) {
      setError(err.message || 'Google login failed');
    }
  };

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const { loginWithEmail, registerWithEmail } = useAuth();

  const handleEmailLogin = async () => {
    try {
      setError('');
      await loginWithEmail(email, password);
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  };

  const handleEmailRegister = async () => {
    try {
      setError('');
      await registerWithEmail(email, password, fullName);
    } catch (err) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="login-page-wrapper" style={{ display: 'flex', minHeight: '100vh', width: '100%', alignItems: 'stretch' }}>
      <div className="left-panel">
<div className="orb orb-1"></div>
<div className="orb orb-2"></div>
<div className="brand">
<div className="brand-icon">📚</div>
<span className="brand-name">Koala</span>
</div>
<div className="hero-content">
<div className="hero-tag">✨ v2.0 — AI-Assisted</div>
<h1 className="hero-title">Your semester,<br/><span>fully mapped.</span></h1>
<p className="hero-desc">Upload your syllabus. AI builds your roadmap. Track every topic, note, and deadline — all in one living picture of how you actually learn.</p>
<div className="feature-list">
<div className="feature-item">
<div className="icon">🤖</div>
<span>AI extracts roadmaps from your syllabus — deadlines, weights, topics</span>
</div>
<div className="feature-item">
<div className="icon">🗺️</div>
<span>Obsidian-style notes linked to every roadmap node and topic</span>
</div>
<div className="feature-item">
<div className="icon">📊</div>
<span>Profile insights: confidence trends, planning accuracy, procrastination fingerprint</span>
</div>
<div className="feature-item">
<div className="icon">🔥</div>
<span>Streak system tied to real academic progress, not arbitrary taps</span>
</div>
</div>
<div className="stats-ticker">
<div className="stat-item">
<div className="stat-value">8 phases</div>
<div className="stat-label">Feature-complete roadmap</div>
</div>
<div className="stat-item">
<div className="stat-value">$0</div>
<div className="stat-label">Cost to launch</div>
</div>
<div className="stat-item">
<div className="stat-value">100%</div>
<div className="stat-label">Student-owned data</div>
</div>
</div>
</div>
</div>
      <div className="right-panel">
        <div className="auth-header">
          <h2>{activeTab === 'login' ? 'Welcome back 👋' : 'Create your account'}</h2>
          <p>{activeTab === 'login' ? 'Sign in to your Koala account to continue.' : 'Start tracking your academic journey today.'}</p>
        </div>

        <div className="auth-toggle">
          <button 
            className={activeTab === 'login' ? 'active' : ''} 
            onClick={() => setActiveTab('login')}>
            Sign In
          </button>
          <button 
            className={activeTab === 'register' ? 'active' : ''} 
            onClick={() => setActiveTab('register')}>
            Create Account
          </button>
        </div>

        {error && <div style={{color: '#f87171', marginBottom: '16px', fontSize: '14px'}}>{error}</div>}

        <button className="google-btn" onClick={handleGoogle}>
          <span className="google-logo"></span>
          Continue with Google
        </button>

        <div className="divider">or continue with email</div>

        {activeTab === 'login' ? (
          <div id="login-form">
            <div className="form-group">
              <label>Email Address</label>
              <input type="email" placeholder="you@university.edu" value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} />
            </div>
            <button className="submit-btn" onClick={handleEmailLogin}>Sign In →</button>
            <div className="auth-footer">
              <a href="#">Forgot your password?</a>
            </div>
          </div>
        ) : (
          <div id="register-form">
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" placeholder="Alex Johnson" value={fullName} onChange={e => setFullName(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Email Address</label>
              <input type="email" placeholder="you@university.edu" value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" placeholder="Create a strong password" value={password} onChange={e => setPassword(e.target.value)} />
            </div>
            <button className="submit-btn" onClick={handleEmailRegister}>Create Account →</button>
            <div className="auth-footer">
              By signing up, you agree to our <a href="#">Terms</a> & <a href="#">Privacy Policy</a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
