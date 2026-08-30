import React from 'react'
import {
  ChevronRight,
  User,
  Sparkles,
} from 'lucide-react'

export function formatRoleName(roleId) {
  if (!roleId) return 'AI/ML Engineer'
  if (roleId === 'ai_ml_engineer') return 'AI/ML Engineer'
  if (roleId === 'backend_engineer') return 'Backend Engineer'
  if (roleId === 'data_scientist') return 'Data Scientist'
  return roleId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

export default function Header({
  activeView,
  candidate,
  role,
  health,
}) {
  const getViewName = (viewId) => {
    switch (viewId) {
      case 'dashboard': return 'Dashboard & Command Center'
      case 'interview': return 'Live Technical Interview'
      case 'candidate': return 'Candidate Resume Profile'
      case 'coverage': return 'Resume Coverage Matrix'
      case 'analytics': return 'Performance & Analytics'
      case 'results': return 'Comprehensive Assessment Report'
      case 'processing': return 'Preparing Screening'
      default: return 'Portal'
    }
  }

  return (
    <header className="top-header">
      {/* Breadcrumbs */}
      <div className="header-breadcrumbs">
        <span>ApexScreen</span>
        <ChevronRight size={14} />
        <span>Technical Screening</span>
        <ChevronRight size={14} />
        <span className="breadcrumb-active">{getViewName(activeView)}</span>
      </div>

      {/* Header Info & Actions */}
      <div className="header-actions">
        {candidate && (
          <div className="candidate-pill">
            <User size={14} color="#4f46e5" />
            <span>{candidate.name || 'Candidate'}</span>
            <span className="role-pill-badge">
              {formatRoleName(role)}
            </span>
          </div>
        )}

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          borderRadius: 'var(--radius-full)',
          background: 'var(--bg-input)',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.76rem',
          color: 'var(--text-muted)'
        }}>
          <Sparkles size={13} color="#4f46e5" />
          <span>{health?.llm_mode || 'Gemini 3.6 Flash'}</span>
        </div>
      </div>
    </header>
  )
}
