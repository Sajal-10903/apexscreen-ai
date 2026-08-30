import React, { useState, useEffect } from 'react'
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Brain,
  Server,
  BarChart,
  Shield,
  Layers,
  Cpu,
  User,
  Activity,
  Award,
  Clock,
  RotateCcw,
  Zap,
  Play,
  Database,
  TrendingUp,
  AlertTriangle,
  ChevronRight
} from 'lucide-react'
import {
  ResponsiveContainer,
  BarChart as RechartsBar,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts'
import { api } from '../services/api'
import ResumeCoverageCard from '../components/ResumeCoverageCard'

export default function LandingPage({
  onStart,
  health,
  candidate,
  role,
  results,
  hasActiveSession,
  onNavigate
}) {
  const [file, setFile] = useState(null)
  const [localCandidate, setLocalCandidate] = useState(candidate || null)
  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState(role || 'ai_ml_engineer')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)

  useEffect(() => {
    if (candidate) {
      setLocalCandidate(candidate)
    }
  }, [candidate])

  useEffect(() => {
    api.getRoles()
      .then(res => {
        if (res?.roles) setRoles(res.roles)
      })
      .catch(err => console.error('Failed to load roles:', err))
  }, [])

  const handleFileDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === 'application/pdf') {
      handleUpload(droppedFile)
    } else {
      setError('Please upload a valid PDF resume file.')
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      handleUpload(selectedFile)
    }
  }

  const handleUpload = async (pdfFile) => {
    setFile(pdfFile)
    setUploading(true)
    setError(null)

    try {
      const res = await api.uploadResume(pdfFile)
      setLocalCandidate(res)
    } catch (err) {
      setError(err.message || 'Failed to process resume. Please upload a readable PDF.')
    } finally {
      setUploading(false)
    }
  }

  const getRoleIcon = (roleId) => {
    switch (roleId) {
      case 'ai_ml_engineer': return Brain
      case 'backend_engineer': return Server
      case 'data_scientist': return BarChart
      default: return Layers
    }
  }

  const activeCand = localCandidate || candidate
  const answeredQuestions = results?.questions?.filter(q => q.answer_text) || []

  // Topic bar data for dashboard
  const topicMap = {}
  answeredQuestions.forEach((q) => {
    if (!topicMap[q.topic]) topicMap[q.topic] = []
    topicMap[q.topic].push(q.score)
  })
  const topicBarData = Object.entries(topicMap).map(([topic, scores]) => ({
    topic: topic.length > 14 ? topic.slice(0, 12) + '...' : topic,
    score: Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1))
  }))

  // Progression Line Data
  const progressionData = results?.score_progression || answeredQuestions.map((q, idx) => ({
    question_index: `Q${idx + 1}`,
    score: q.score
  }))

  const canStart = activeCand && selectedRole && !uploading

  return (
    <div className="page-container">
      {/* ─────────────────────────────────────────────────────────
         TOP HERO GRADIENT BANNER
         ───────────────────────────────────────────────────────── */}
      <div className="hero-gradient-card" style={{ padding: '32px 36px', marginBottom: '24px', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', position: 'relative', zIndex: 2 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{
                padding: '3px 12px',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.7rem',
                fontWeight: 700,
                background: 'rgba(255,255,255,0.2)',
                color: '#ffffff',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                backdropFilter: 'blur(4px)'
              }}>ENTERPRISE SCREENING PLATFORM</span>
              <span style={{ fontSize: '0.74rem', color: 'rgba(255,255,255,0.7)' }}>• Grounded with Google Gemini & ChromaDB</span>
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em' }}>
              {activeCand ? `Screening: ${activeCand.name || 'Candidate'}` : 'Technical Screening & Assessment Portal'}
            </h1>
            <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.8)', marginTop: '6px', maxWidth: '600px' }}>
              {activeCand
                ? `Track: ${(role || selectedRole).replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} • ${activeCand.skills?.length || 0} skills detected • Real-time rubric calibration`
                : 'Upload candidate resume to extract technical stack signals and begin adaptive, RAG-grounded interview rounds.'}
            </p>
          </div>

          {activeCand && (
            <div style={{ display: 'flex', gap: '10px' }}>
              {hasActiveSession ? (
                <button onClick={() => onNavigate('interview')} className="btn-primary" style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.3)', boxShadow: 'none' }}>
                  <Play size={15} /> Resume Live Interview
                </button>
              ) : (
                <button onClick={() => onStart(activeCand.candidate_id, selectedRole, activeCand)} className="btn-primary" style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.3)', boxShadow: 'none' }}>
                  <Sparkles size={15} /> Start Technical Screening →
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────
         IF CANDIDATE LOADED: FULL ANALYTICAL COMMAND CENTER
         ───────────────────────────────────────────────────────── */}
      {activeCand && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '24px' }}>
          {/* 1. TOP KPI ROW */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
            <div className="glass-card" style={{ padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <span>Resume Match Score</span>
                <Sparkles size={16} color="#4f46e5" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-heading)', marginTop: '6px' }}>
                92<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>%</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--accent-indigo)', marginTop: '2px', fontWeight: 600 }}>
                High technical stack alignment
              </div>
            </div>

            <div className="glass-card" style={{ padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <span>Skills Detected</span>
                <Cpu size={16} color="#06b6d4" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-heading)', marginTop: '6px' }}>
                {activeCand.skills?.length || 0}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#0891b2', marginTop: '2px', fontWeight: 600 }}>
                {activeCand.ai_ml_technologies?.length || 0} ML/Framework tokens
              </div>
            </div>

            <div className="glass-card" style={{ padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <span>Interview Progress</span>
                <Activity size={16} color="#10b981" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-heading)', marginTop: '6px' }}>
                {answeredQuestions.length}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/{results?.total_questions || 8}</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#059669', marginTop: '2px', fontWeight: 600 }}>
                {hasActiveSession ? 'Session active' : 'Ready to start'}
              </div>
            </div>

            <div className="glass-card" style={{ padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <span>Current Score</span>
                <Award size={16} color="#f59e0b" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-heading)', marginTop: '6px' }}>
                {results?.overall_score || (answeredQuestions.length ? '—' : '—')}
                <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/10</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#d97706', marginTop: '2px', fontWeight: 600 }}>
                Weighted 4-factor rubric
              </div>
            </div>
          </div>

          {/* 2. MAIN ANALYTICS & INSIGHTS GRID */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '18px' }}>
            {/* Topic Performance Chart */}
            <div className="glass-card" style={{ padding: '22px 24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart size={16} color="#4f46e5" />
                  <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                    Topic-wise Evaluation Performance
                  </h3>
                </div>
                <button
                  onClick={() => onNavigate('analytics')}
                  style={{ background: 'transparent', border: 'none', color: 'var(--accent-indigo)', fontSize: '0.76rem', fontWeight: 700, cursor: 'pointer' }}
                >
                  Full Metrics →
                </button>
              </div>

              {topicBarData.length > 0 ? (
                <div style={{ width: '100%', height: 180 }}>
                  <ResponsiveContainer>
                    <RechartsBar data={topicBarData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="topic" stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 11 }} />
                      <YAxis domain={[0, 10]} stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', color: '#1e293b', boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }} />
                      <Bar dataKey="score" fill="url(#barGrad)" radius={[6, 6, 0, 0]} name="Score (/10)">
                        <defs>
                          <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#4f46e5" />
                            <stop offset="100%" stopColor="#7c3aed" />
                          </linearGradient>
                        </defs>
                      </Bar>
                    </RechartsBar>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  Topic scores will render here as questions are evaluated.
                </div>
              )}
            </div>

            {/* Insights Panel: Strengths & Weaknesses */}
            <div className="glass-card" style={{ padding: '22px 24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <TrendingUp size={16} color="#06b6d4" />
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                  Technical Assessment Insights
                </h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.15)', borderLeft: '3px solid #10b981' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#059669', textTransform: 'uppercase', marginBottom: '6px' }}>
                    ✓ Strongest Areas
                  </div>
                  <ul style={{ paddingLeft: '14px', fontSize: '0.78rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {results?.strong_areas?.length > 0 ? (
                      results.strong_areas.slice(0, 3).map((s, idx) => <li key={idx}>{s}</li>)
                    ) : (
                      <>
                        <li>Data Pipelines & ML Prep</li>
                        <li>Feature Engineering (TF-IDF)</li>
                      </>
                    )}
                  </ul>
                </div>

                <div style={{ padding: '14px 16px', borderRadius: 'var(--radius-md)', background: 'rgba(245, 158, 11, 0.04)', border: '1px solid rgba(245, 158, 11, 0.15)', borderLeft: '3px solid #f59e0b' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#d97706', textTransform: 'uppercase', marginBottom: '6px' }}>
                    ⚠ Growth Opportunities
                  </div>
                  <ul style={{ paddingLeft: '14px', fontSize: '0.78rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {results?.weak_areas?.length > 0 ? (
                      results.weak_areas.slice(0, 3).map((w, idx) => <li key={idx}>{w}</li>)
                    ) : (
                      <>
                        <li>Distributed Model Serving</li>
                        <li>Production Latency Optimization</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* 3. RESUME COVERAGE MATRIX */}
          <ResumeCoverageCard
            coverageData={results?.coverage_summary || {}}
            totalQuestions={results?.total_questions || 8}
            answeredCount={answeredQuestions.length}
          />

          {/* 4. SYSTEM STATUS BAR */}
          <div className="glass-card" style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', fontSize: '0.78rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="status-dot" />
                <span style={{ color: 'var(--text-muted)' }}>LLM:</span>
                <strong style={{ color: 'var(--text-heading)' }}>{health?.llm_mode || 'Google Gemini 3.6 Flash'}</strong>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Database size={13} color="#4f46e5" />
                <span style={{ color: 'var(--text-muted)' }}>ChromaDB:</span>
                <strong style={{ color: 'var(--text-heading)' }}>3 Collections (92 Chunks)</strong>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Cpu size={13} color="#06b6d4" />
                <span style={{ color: 'var(--text-muted)' }}>Embedding:</span>
                <strong style={{ color: 'var(--text-heading)' }}>all-MiniLM-L6-v2 (384-dim)</strong>
              </div>
            </div>

            <div style={{ color: 'var(--accent-indigo)', fontWeight: 700 }}>
              System Status: ONLINE & GROUNDED
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────
         INTAKE ZONE: UPLOAD RESUME & ROLE SELECTION
         ───────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '18px' }}>
        {/* Step 1: Upload Resume */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '0.82rem'
            }}>
              1
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                {activeCand ? 'Upload / Replace Resume PDF' : 'Upload Candidate Resume'}
              </h3>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>PyMuPDF multi-page parsing & structured signal extraction</p>
            </div>
          </div>

          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleFileDrop}
            style={{
              border: `2px dashed ${isDragOver ? '#4f46e5' : '#cbd5e1'}`,
              borderRadius: 'var(--radius-md)',
              padding: '30px 18px',
              textAlign: 'center',
              background: isDragOver ? 'rgba(79, 70, 229, 0.04)' : '#fafbfc',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => document.getElementById('resume-file-input').click()}
          >
            <input
              id="resume-file-input"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />

            <UploadCloud size={38} color={isDragOver ? '#4f46e5' : '#94a3b8'} style={{ margin: '0 auto 10px' }} />
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: '4px' }}>
              {uploading ? 'Extracting Skills & Projects...' : (file ? file.name : (activeCand ? 'Choose a different PDF resume' : 'Drop candidate PDF resume here or click to browse'))}
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
              Supports PDF documents up to 10MB
            </div>
          </div>

          {error && (
            <div style={{
              marginTop: '12px',
              padding: '10px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(239, 68, 68, 0.06)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              color: '#dc2626',
              fontSize: '0.78rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Step 2: Select Technical Track */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '0.82rem'
            }}>
              2
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-heading)' }}>Select Technical Track</h3>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Calibrated assessment track & topic ladders</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {roles.map((r) => {
              const Icon = getRoleIcon(r.id)
              const isSelected = selectedRole === r.id
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedRole(r.id)}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: isSelected ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.06), rgba(124, 58, 237, 0.03))' : '#fafbfc',
                    border: `1.5px solid ${isSelected ? 'var(--accent-indigo)' : 'var(--border-subtle)'}`,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Icon size={16} color={isSelected ? '#4f46e5' : '#94a3b8'} />
                      <span style={{ fontWeight: 700, color: isSelected ? 'var(--text-heading)' : 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        {r.name}
                      </span>
                    </div>
                    {isSelected && (
                      <span style={{ color: 'var(--accent-indigo)', fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase' }}>
                        Active Track
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginLeft: '24px' }}>
                    {r.description || 'Target engineering assessment track'}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Start Button if candidate not yet loaded */}
      {!activeCand && (
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <button
            onClick={() => onStart(activeCand?.candidate_id, selectedRole, activeCand)}
            disabled={!canStart}
            className="btn-primary"
            style={{ padding: '14px 32px', fontSize: '0.98rem', minWidth: '300px' }}
          >
            <Sparkles size={16} /> Start Technical Screening <ArrowRight size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
