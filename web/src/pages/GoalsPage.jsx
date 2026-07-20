import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function GoalsPage() {
  const navigate = useNavigate();
  return (
    <div className="page active">
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '60vh', textAlign: 'center', gap: '1.25rem',
      }}>
        <div style={{
          width: '80px', height: '80px', background: 'var(--amber-dim)',
          borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2.5rem',
        }}>
          🎯
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Goals</h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '380px', lineHeight: 1.6 }}>
            Set semester goals like "Get a B+ in all courses" or "Submit assignments 2 days early"
            and track your progress automatically as you complete topics and assignments.
          </p>
        </div>
        <div style={{
          padding: '0.4rem 1rem', background: 'var(--amber-dim)',
          border: '1px solid rgba(251,191,36,0.3)', borderRadius: '20px',
          fontSize: '12px', color: 'var(--amber)', fontWeight: 600,
        }}>
          🚧 Coming in Phase 2
        </div>
        <button className="secondary-btn" style={{ width: 'auto' }} onClick={() => navigate('/')}>
          ← Back to Dashboard
        </button>
      </div>
    </div>
  );
}
