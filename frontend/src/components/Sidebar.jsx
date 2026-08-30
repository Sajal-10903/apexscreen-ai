import React from 'react'
import {
  LayoutDashboard,
  Mic,
  User,
  PieChart,
  BarChart3,
  FileCheck2,
  Sparkles,
  RotateCcw
} from 'lucide-react'
import { formatRoleName } from './Header'

export default function Sidebar({
  activeView,
  onNavigate,
  health,
  hasActiveSession,
  candidate,
  role,
  onReset
}) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'interview', label: 'Live Interview', icon: Mic, badge: hasActiveSession ? 'LIVE' : null },
    { id: 'candidate', label: 'Candidate Profile', icon: User },
    { id: 'coverage', label: 'Resume Coverage', icon: PieChart },
    { id: 'analytics', label: 'Analytics & Metrics', icon: BarChart3 },
    { id: 'results', label: 'Assessment Report', icon: FileCheck2 },
  ]

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="brand-icon">
          <Sparkles size={20} />
        </div>
        <div className="brand-title">
          <span>ApexScreen AI</span>
          <span className="brand-subtitle">Technical Screener</span>
        </div>
      </div>

      {/* Navigation List */}
      <div className="sidebar-nav">
        <div className="nav-section-label">Screening Console</div>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeView === item.id

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badge && <span className="nav-badge-live">{item.badge}</span>}
            </button>
          )
        })}

        {/* Active Candidate Widget in Sidebar */}
        {candidate && (
          <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
            <div className="nav-section-label">Active Candidate</div>
            <div style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.8rem'
            }}>
              <div style={{ fontWeight: 700, color: 'var(--text-heading)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {candidate.name || 'Candidate'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--accent-indigo)', marginTop: '2px', textTransform: 'uppercase', fontWeight: 700 }}>
                {formatRoleName(role)}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.72rem' }}>
                <span>{candidate.skills?.length || 0} Skills</span> • <span>{candidate.projects?.length || 0} Projects</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Sidebar Footer & System Status */}
      <div className="sidebar-footer">
        <div className="system-status-box">
          <div className="status-row">
            <span>LLM Engine</span>
            <span className="status-indicator">
              <span className="status-dot" />
              {health?.llm_mode ? health.llm_mode.split(' ')[0] : 'Gemini 3.6'}
            </span>
          </div>
          <div className="status-row">
            <span>Vector Store</span>
            <span className="status-indicator" style={{ color: 'var(--accent-indigo)' }}>
              ChromaDB
            </span>
          </div>
        </div>

        {candidate && (
          <button
            onClick={onReset}
            className="btn-secondary"
            style={{ padding: '8px 12px', fontSize: '0.78rem', width: '100%' }}
          >
            <RotateCcw size={13} /> Reset Candidate
          </button>
        )}
      </div>
    </aside>
  )
}
