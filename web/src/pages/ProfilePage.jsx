import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div className="page active">
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '60vh', textAlign: 'center', gap: '1.25rem',
      }}>
        <div style={{
          width: '80px', height: '80px', background: 'var(--blue-dim)',
          borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2.5rem',
        }}>
          📊
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Insights & Profile</h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '380px', lineHeight: 1.6 }}>
            View your study patterns, confidence trends, planning accuracy, procrastination fingerprint,
            and detailed retrospective reports — all driven by your activity data.
          </p>
        </div>
        <div style={{
          padding: '0.4rem 1rem', background: 'var(--blue-dim)',
          border: '1px solid rgba(96,165,250,0.3)', borderRadius: '20px',
          fontSize: '12px', color: 'var(--blue)', fontWeight: 600,
        }}>
          🚧 Coming in Phase 2
        </div>
        {user && (
          <div style={{
            padding: '1rem 1.5rem', background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-md)', border: '1px solid var(--border)',
            fontSize: '13px', color: 'var(--text-secondary)',
          }}>
            Logged in as <strong style={{ color: 'var(--text-primary)' }}>{user.email}</strong>
            {' · '}
            <span style={{ color: user.plan === 'pro' ? 'var(--purple-light)' : 'var(--text-muted)' }}>
              {user.plan === 'pro' ? '✨ Pro Plan' : 'Free Plan'}
            </span>
          </div>
        )}
        <button className="secondary-btn" style={{ width: 'auto' }} onClick={() => navigate('/')}>
          ← Back to Dashboard
        </button>
      </div>
    </div>
  );
}
