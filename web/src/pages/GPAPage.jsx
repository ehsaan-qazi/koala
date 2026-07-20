import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function GPAPage() {
  const navigate = useNavigate();
  return (
    <div className="page active">
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: '60vh', textAlign: 'center', gap: '1.25rem',
      }}>
        <div style={{
          width: '80px', height: '80px', background: 'var(--green-dim)',
          borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2.5rem',
        }}>
          🎓
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>GPA Calculator</h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '380px', lineHeight: 1.6 }}>
            Calculate your semester GPA, cumulative CGPA, run what-if scenarios,
            and track GPA-linked goals. Supports 4.0 and 5.0 grading scales.
          </p>
        </div>
        <div style={{
          padding: '0.4rem 1rem', background: 'var(--green-dim)',
          border: '1px solid rgba(52,211,153,0.3)', borderRadius: '20px',
          fontSize: '12px', color: 'var(--green)', fontWeight: 600,
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
