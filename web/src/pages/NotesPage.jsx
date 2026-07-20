import React from 'react';
import { useNavigate } from 'react-router-dom';

function ComingSoonPage({ icon, title, description, eta }) {
  const navigate = useNavigate();
  return (
    <div className="page active">
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
        gap: '1.25rem',
      }}>
        <div style={{
          width: '80px', height: '80px',
          background: 'var(--purple-dim)',
          borderRadius: '20px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '2.5rem',
          boxShadow: '0 0 30px var(--purple-glow)',
        }}>
          {icon}
        </div>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{title}</h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '380px', lineHeight: 1.6 }}>{description}</p>
        </div>
        {eta && (
          <div style={{
            padding: '0.4rem 1rem',
            background: 'var(--purple-dim)',
            border: '1px solid var(--purple-glow)',
            borderRadius: '20px',
            fontSize: '12px',
            color: 'var(--purple-light)',
            fontWeight: 600,
          }}>
            🚧 Coming in Phase 2
          </div>
        )}
        <button className="secondary-btn" style={{ width: 'auto' }} onClick={() => navigate('/')}>
          ← Back to Dashboard
        </button>
      </div>
    </div>
  );
}

export default function NotesPage() {
  return (
    <ComingSoonPage
      icon="📝"
      title="Obsidian-Style Notes"
      description="Write notes linked to your roadmap nodes and topics. Create wikilinks between notes and visualize your knowledge as an interactive graph."
      eta
    />
  );
}
