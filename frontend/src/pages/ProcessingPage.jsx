import React, { useState, useEffect } from 'react'
import {
  CheckCircle2,
  Cpu,
  Database,
  Layers,
  Sparkles,
  FileText,
  UserCheck,
  ArrowRight,
  AlertCircle
} from 'lucide-react'
import { api } from '../services/api'

const PREP_STEPS = [
  { id: 1, label: 'Candidate Profile & Education Extraction', icon: UserCheck, desc: 'Parsing academic degree, contact details, and candidate background' },
  { id: 2, label: 'Resume & Technical Skills Analysis', icon: Cpu, desc: 'Extracting programming languages, frameworks, and AI/ML stack' },
  { id: 3, label: 'Role Curriculum & Topic Mapping', icon: Layers, desc: 'Calibrating assessment difficulty and progression ladders' },
  { id: 4, label: 'Knowledge Base Vector Retrieval', icon: Database, desc: 'Querying ChromaDB embedding collections for domain grounding' },
  { id: 5, label: 'Grounded Question Generation', icon: Sparkles, desc: 'Synthesizing customized technical questions via Google Gemini' },
  { id: 6, label: 'Ready to Begin Technical Screening', icon: CheckCircle2, desc: 'Active session initialized and verified' }
]

export default function ProcessingPage({
  candidateId,
  role,
  onReady,
  onError
}) {
  const [currentStep, setCurrentStep] = useState(0)
  const [percent, setPercent] = useState(15)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    const runPipeline = async () => {
      try {
        await delay(500)
        if (cancelled) return
        setCurrentStep(1)
        setPercent(32)

        await delay(550)
        if (cancelled) return
        setCurrentStep(2)
        setPercent(50)

        await delay(500)
        if (cancelled) return
        setCurrentStep(3)
        setPercent(68)

        const result = await api.createInterview(candidateId, role)
        if (cancelled) return
        setCurrentStep(4)
        setPercent(85)

        await delay(500)
        if (cancelled) return
        setCurrentStep(5)
        setPercent(100)

        await delay(450)
        if (cancelled) return

        onReady(result.session_id, result.is_mock_mode)
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to initialize technical interview session.')
        }
      }
    }

    runPipeline()
    return () => { cancelled = true }
  }, [candidateId, role])

  if (error) {
    return (
      <div className="page-container" style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="glass-card" style={{ padding: '40px', maxWidth: '520px', textAlign: 'center' }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#dc2626',
            margin: '0 auto 16px'
          }}>
            <AlertCircle size={32} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: '8px' }}>
            Preparation Encountered an Issue
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '24px' }}>
            {error}
          </p>
          <button onClick={onError} className="btn-secondary">
            ← Return to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const radius = 48
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percent / 100) * circumference

  return (
    <div className="page-container" style={{ minHeight: '82vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-card-elevated" style={{ padding: '38px 42px', maxWidth: '640px', width: '100%', position: 'relative' }}>
        {/* Top header with progress ring */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
          <div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.08), rgba(124, 58, 237, 0.05))',
              color: 'var(--accent-indigo)',
              fontSize: '0.74rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              marginBottom: '10px',
              border: '1px solid rgba(79, 70, 229, 0.15)'
            }}>
              <Sparkles size={13} />
              AI Orchestrator
            </div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-heading)', letterSpacing: '-0.02em' }}>
              Preparing Technical Screening
            </h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Grounding assessment rubric with resume signals & ChromaDB vector context
            </p>
          </div>

          {/* SVG Progress Ring */}
          <div style={{ position: 'relative', width: '110px', height: '110px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="110" height="110" style={{ transform: 'rotate(-90deg)' }}>
              <circle
                cx="55"
                cy="55"
                r={radius}
                stroke="#e2e8f0"
                strokeWidth="7"
                fill="transparent"
              />
              <circle
                cx="55"
                cy="55"
                r={radius}
                stroke="url(#prepGradient)"
                strokeWidth="7"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{ transition: 'stroke-dashoffset 0.5s ease' }}
              />
              <defs>
                <linearGradient id="prepGradient" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" />
                  <stop offset="50%" stopColor="#7c3aed" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-heading)', lineHeight: 1 }}>
                {percent}%
              </div>
              <div style={{ fontSize: '0.64rem', color: 'var(--accent-indigo)', textTransform: 'uppercase', fontWeight: 700, marginTop: '2px' }}>
                Setup
              </div>
            </div>
          </div>
        </div>

        {/* Step-by-Step Progress List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {PREP_STEPS.map((s, idx) => {
            const Icon = s.icon
            const isCompleted = idx < currentStep
            const isCurrent = idx === currentStep

            return (
              <div
                key={s.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: isCurrent
                    ? 'linear-gradient(90deg, rgba(79, 70, 229, 0.06), rgba(124, 58, 237, 0.02))'
                    : (isCompleted ? '#fafbfc' : '#fafbfc'),
                  border: `1px solid ${isCurrent ? 'rgba(79, 70, 229, 0.25)' : (isCompleted ? 'var(--border-subtle)' : 'transparent')}`,
                  opacity: isCompleted || isCurrent ? 1 : 0.4,
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: isCompleted
                    ? 'rgba(16, 185, 129, 0.1)'
                    : (isCurrent ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(124, 58, 237, 0.08))' : 'var(--bg-input)'),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isCompleted ? '#059669' : (isCurrent ? '#4f46e5' : 'var(--text-muted)')
                }}>
                  {isCompleted ? <CheckCircle2 size={16} /> : <Icon size={16} />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '0.88rem',
                    fontWeight: 600,
                    color: isCurrent ? 'var(--text-heading)' : (isCompleted ? 'var(--text-secondary)' : 'var(--text-muted)')
                  }}>
                    {s.label}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    {s.desc}
                  </div>
                </div>

                {isCurrent && (
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: 'var(--accent-indigo)',
                    boxShadow: '0 0 10px rgba(79, 70, 229, 0.5)',
                    animation: 'pulseDot 1.2s infinite'
                  }} />
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms))
}
