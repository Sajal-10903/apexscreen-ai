import React, { useState } from 'react'
import {
  FolderGit2,
  Cpu,
  GraduationCap,
  Briefcase,
  Award,
  ChevronDown,
  ChevronUp,
  Database,
  Layers,
  Sparkles
} from 'lucide-react'

export default function QuestionProvenanceCard({ question, candidate }) {
  const [showRAGDetails, setShowRAGDetails] = useState(false)

  if (!question) return null

  const sourceType = question.source_type || 'general_rag'
  const resumeSection = question.resume_section || question.section || 'General Technical'
  const sourceItem = question.source_item || question.topic || 'Curriculum Domain'
  const signals = question.source_signals || []
  const trace = question.traceability || {}
  const retrievedChunks = trace.retrieved_chunks || []

  const getCategoryConfig = (st) => {
    switch (st) {
      case 'resume_project':
        return { label: 'PROJECT BASED', icon: FolderGit2, color: '#7c3aed' }
      case 'resume_skill':
        return { label: 'SKILLS & ARCHITECTURE', icon: Cpu, color: '#4f46e5' }
      case 'resume_education':
        return { label: 'BACKGROUND & FOUNDATION', icon: GraduationCap, color: '#3b82f6' }
      case 'resume_experience':
        return { label: 'WORK EXPERIENCE', icon: Briefcase, color: '#06b6d4' }
      case 'resume_certification':
        return { label: 'CERTIFICATIONS', icon: Award, color: '#f59e0b' }
      case 'performance_followup':
        return { label: 'FOLLOW-UP PROBE', icon: Sparkles, color: '#a855f7' }
      default:
        return { label: 'GENERAL TECHNICAL', icon: Database, color: '#06b6d4' }
    }
  }

  const { label, icon: Icon, color } = getCategoryConfig(sourceType)

  return (
    <div className="meta-strip-card" style={{ borderLeftColor: color }}>
      {/* Row 1: Category Tag & Difficulty Calibration */}
      <div className="meta-strip-top">
        <div className="meta-category-badge" style={{
          background: `${color}12`,
          color: color,
          borderColor: `${color}30`
        }}>
          <Icon size={13} />
          <span>{label}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.78rem' }}>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Difficulty: </span>
            <strong style={{
              textTransform: 'uppercase',
              color: question.difficulty === 'advanced' ? '#dc2626' : (question.difficulty === 'intermediate' ? '#d97706' : '#059669')
            }}>
              {question.difficulty || 'Intermediate'}
            </strong>
          </div>
          <span style={{ color: 'var(--border-medium)' }}>•</span>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Topic: </span>
            <strong style={{ color: 'var(--text-heading)' }}>{question.topic}</strong>
          </div>
        </div>
      </div>

      {/* Row 2: Resume Breadcrumb Path */}
      <div className="meta-breadcrumb-line">
        <span style={{ color: 'var(--text-muted)' }}>Source Path:</span>
        <span>Resume</span>
        <span style={{ color: 'var(--text-dim)' }}>→</span>
        <span>{resumeSection}</span>
        <span style={{ color: 'var(--text-dim)' }}>→</span>
        <strong>{sourceItem}</strong>
      </div>

      {/* Row 3: Resume Signals */}
      {signals.length > 0 && (
        <div className="meta-signals-line">
          <span style={{ color: 'var(--text-muted)' }}>Signals:</span>
          {signals.map((sig, idx) => (
            <span key={idx} className="signal-token">
              {sig}
            </span>
          ))}
        </div>
      )}

      {/* Row 4: RAG Vector Grounding Drawer */}
      {retrievedChunks.length > 0 && (
        <div style={{ paddingTop: '6px', borderTop: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setShowRAGDetails(!showRAGDetails)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--accent-indigo)',
              fontSize: '0.74rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              cursor: 'pointer',
              padding: 0
            }}
          >
            <Database size={12} />
            <span>RAG Context ({retrievedChunks.length} ChromaDB Knowledge Chunks)</span>
            {showRAGDetails ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>

          {showRAGDetails && (
            <div style={{
              marginTop: '8px',
              padding: '10px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.76rem',
              color: 'var(--text-secondary)'
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {retrievedChunks.map((chunk, idx) => (
                  <div key={idx} style={{ padding: '6px 8px', background: '#ffffff', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-indigo)', fontSize: '0.7rem', fontWeight: 700 }}>
                      <span>{chunk.document} § {chunk.section}</span>
                      <span>Cosine: {chunk.score?.toFixed(3) || '0.750'}</span>
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.72rem', marginTop: '2px' }}>
                      "{chunk.text_preview}"
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
