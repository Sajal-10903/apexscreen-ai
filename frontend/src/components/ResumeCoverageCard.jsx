import React from 'react'
import {
  CheckCircle2,
  Circle,
  FolderGit2,
  Cpu,
  GraduationCap,
  Briefcase,
  Award,
  Layers,
  Sparkles,
  PieChart,
  Target
} from 'lucide-react'

export default function ResumeCoverageCard({ coverageData = {}, totalQuestions = 8, answeredCount = 0 }) {
  const ALL_SECTIONS = [
    { key: 'Introduction / Background', label: 'Introduction & Foundation', icon: GraduationCap, desc: 'Academic background & core CS fundamentals' },
    { key: 'Projects', label: 'Portfolio Projects', icon: FolderGit2, desc: 'Architecture, trade-offs & production decisions' },
    { key: 'Skills', label: 'Core Skills & Stack', icon: Cpu, desc: 'Languages, frameworks, databases & libraries' },
    { key: 'Work Experience', label: 'Work Experience & Systems', icon: Briefcase, desc: 'Production systems, telemetry & concurrency' },
    { key: 'Certifications', label: 'Certifications & Standards', icon: Award, desc: 'Cloud architectures & best practices' },
    { key: 'Technical Concepts', label: 'Technical Concepts (RAG)', icon: Layers, desc: 'Algorithmic depth & ChromaDB knowledge base' },
    { key: 'General Technical', label: 'System Design & APIs', icon: Target, desc: 'Distributed caching, indexing & schemas' },
    { key: 'Follow-up / Performance Based', label: 'Follow-up Calibration', icon: Sparkles, desc: 'Adaptive probes on edge cases & scaling' },
  ]

  let coveredCount = 0
  ALL_SECTIONS.forEach(sec => {
    const item = coverageData[sec.key] || coverageData[sec.label]
    if (item && item.status === 'covered') {
      coveredCount++
    }
  })

  const coveragePercent = Math.round((coveredCount / ALL_SECTIONS.length) * 100)

  return (
    <div className="glass-card-elevated" style={{ padding: '28px 32px' }}>
      {/* Top Header Row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PieChart size={20} color="#4f46e5" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-heading)' }}>
              Curriculum & Resume Coverage Matrix
            </h3>
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Comprehensive audit tracking question distribution across all 8 assessment domains.
          </p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-indigo)', lineHeight: 1 }}>
            {coveragePercent}%
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            {coveredCount} of {ALL_SECTIONS.length} Covered
          </div>
        </div>
      </div>

      {/* Global Progress Bar */}
      <div style={{ height: '7px', background: '#e2e8f0', borderRadius: 'var(--radius-full)', overflow: 'hidden', marginBottom: '24px' }}>
        <div style={{
          height: '100%',
          width: `${coveragePercent}%`,
          background: 'var(--gradient-bar)',
          borderRadius: 'var(--radius-full)',
          transition: 'width 0.5s ease'
        }} />
      </div>

      {/* 8-Section Grid */}
      <div className="coverage-grid">
        {ALL_SECTIONS.map((sec) => {
          const Icon = sec.icon
          const data = coverageData[sec.key] || coverageData[sec.label] || { status: 'uncovered', count: 0, average_score: null }
          const isCovered = data.status === 'covered' || data.count > 0

          return (
            <div
              key={sec.key}
              className={`coverage-item-card ${isCovered ? 'covered' : ''}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  background: isCovered ? 'rgba(16, 185, 129, 0.1)' : 'var(--bg-input)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isCovered ? '#059669' : 'var(--text-muted)'
                }}>
                  <Icon size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: isCovered ? 'var(--text-heading)' : 'var(--text-muted)' }}>
                    {sec.label}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {sec.desc}
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span className={`coverage-status-tag ${isCovered ? 'tag-covered' : 'tag-uncovered'}`}>
                  {isCovered ? <CheckCircle2 size={13} /> : <Circle size={13} />}
                  {isCovered ? (data.average_score ? `${data.average_score}/10` : 'Covered') : 'Pending'}
                </span>
                {isCovered && data.count > 0 && (
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {data.count} {data.count === 1 ? 'Question' : 'Questions'}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
