import React, { useState, useEffect } from 'react'
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Printer,
  RotateCcw,
  Sparkles,
  TrendingUp,
  Target,
  Clock,
  User,
  FolderGit2,
  Cpu,
  GraduationCap,
  Briefcase,
  Layers,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { api } from '../services/api'
import ResumeCoverageCard from '../components/ResumeCoverageCard'
import { formatRoleName } from '../components/Header'

export default function ResultsPage({
  sessionId,
  candidate,
  role,
  onRestart,
  results: initialResults
}) {
  const [results, setResults] = useState(initialResults || null)
  const [loading, setLoading] = useState(!initialResults)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('summary')
  const [expandedQuestions, setExpandedQuestions] = useState({})

  useEffect(() => {
    if (!initialResults && sessionId) {
      loadResults()
    }
  }, [sessionId, initialResults])

  const loadResults = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getResults(sessionId)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Failed to load interview results.')
    } finally {
      setLoading(false)
    }
  }

  const toggleExpandQuestion = (idx) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  const handlePrint = () => {
    window.print()
  }

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{
          width: '52px',
          height: '52px',
          borderRadius: '50%',
          border: '3px solid #e2e8f0',
          borderTopColor: '#4f46e5',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }} />
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-heading)' }}>
          Synthesizing Comprehensive Assessment Report...
        </h3>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="page-container">
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center' }}>
          <AlertTriangle size={44} color="#d97706" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-heading)' }}>No Results Available</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            Complete at least one interview question to generate an assessment scorecard.
          </p>
        </div>
      </div>
    )
  }

  const getRecommendationBadge = (rec) => {
    switch (rec?.toLowerCase()) {
      case 'strong_yes':
      case 'strong hire':
        return { label: 'Strong Hire', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.3)', color: '#059669' }
      case 'yes':
      case 'hire':
        return { label: 'Recommended for Hire', bg: 'rgba(79, 70, 229, 0.08)', border: 'rgba(79, 70, 229, 0.25)', color: '#4f46e5' }
      case 'maybe':
      case 'borderline':
        return { label: 'Borderline / Needs Follow-up', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.3)', color: '#d97706' }
      default:
        return { label: 'Screening Threshold Not Met', bg: 'rgba(239, 68, 68, 0.08)', border: 'rgba(239, 68, 68, 0.25)', color: '#dc2626' }
    }
  }

  const badge = getRecommendationBadge(results.hiring_recommendation)
  const answeredQuestions = results.questions?.filter(q => q.answer_text) || []

  return (
    <div className="page-container">
      {/* Top Gradient Banner with Scorecard */}
      <div className="hero-gradient-card" style={{ padding: '32px 36px', marginBottom: '24px', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px', position: 'relative', zIndex: 2 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
                {results.candidate_name || candidate?.name || 'Candidate'}
              </h2>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 14px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '0.82rem',
                textTransform: 'uppercase',
                backdropFilter: 'blur(4px)'
              }}>
                <CheckCircle2 size={15} />
                {badge.label}
              </span>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.8)' }}>
              Track: <strong style={{ color: '#ffffff' }}>{formatRoleName(results.role)}</strong> • Session ID: {results.session_id?.slice(0, 8)}... • Evaluated: {answeredQuestions.length} of {results.total_questions} Questions
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px', position: 'relative', zIndex: 2 }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '2.8rem', fontWeight: 800, color: '#ffffff', lineHeight: 1 }}>
                {results.overall_score}<span style={{ fontSize: '1.2rem', color: 'rgba(255,255,255,0.7)' }}>/10</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.8)', fontWeight: 600, textTransform: 'uppercase' }}>
                Overall Score
              </div>
            </div>

            <button
              onClick={handlePrint}
              className="btn-secondary"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.15)', color: '#ffffff', borderColor: 'rgba(255,255,255,0.3)', backdropFilter: 'blur(4px)' }}
            >
              <Printer size={15} /> Print / Export PDF
            </button>
          </div>
        </div>

        {/* Early Finish Notice */}
        {results.is_completed_early && (
          <div style={{
            marginTop: '20px',
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: 'rgba(255,255,255,0.9)',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            position: 'relative',
            zIndex: 2
          }}>
            <AlertTriangle size={18} />
            <span>
              <strong>Interview Concluded Early:</strong> This evaluation is synthesized strictly from the <strong>{answeredQuestions.length}</strong> questions answered.
            </span>
          </div>
        )}
      </div>

      {/* Tabs Navigation */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
        {[
          { id: 'summary', label: 'Executive Summary & Analysis' },
          { id: 'questions', label: `Question Breakdown (${answeredQuestions.length})` },
          { id: 'coverage', label: 'Curriculum Coverage Matrix' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '8px 18px',
              fontSize: '0.85rem',
              fontWeight: activeTab === tab.id ? 700 : 500,
              borderRadius: 'var(--radius-sm)',
              border: activeTab === tab.id ? 'none' : '1px solid var(--border-subtle)',
              background: activeTab === tab.id ? 'var(--gradient-primary)' : '#ffffff',
              color: activeTab === tab.id ? '#ffffff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              boxShadow: activeTab === tab.id ? 'var(--shadow-gradient)' : 'none'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: EXECUTIVE SUMMARY */}
      {activeTab === 'summary' && (
        <div>
          <div className="glass-card" style={{ padding: '26px', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: '12px' }}>
              Overall Synthesis & Technical Assessment
            </h3>
            <p style={{ fontSize: '0.92rem', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
              {results.overall_assessment || 'Candidate demonstrated competent technical knowledge across answered questions.'}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '22px', marginBottom: '24px' }}>
            <div className="glass-card" style={{ padding: '24px', borderLeft: '3px solid #10b981' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <CheckCircle2 size={18} color="#059669" />
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#059669' }}>
                  Verified Strengths ({results.strong_areas?.length || 0})
                </h3>
              </div>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                {(results.strong_areas || []).map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="glass-card" style={{ padding: '24px', borderLeft: '3px solid #f59e0b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <AlertTriangle size={18} color="#d97706" />
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#d97706' }}>
                  Target Growth Areas ({results.weak_areas?.length || 0})
                </h3>
              </div>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                {(results.weak_areas || []).map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          </div>

          {results.recommendations?.length > 0 && (
            <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <Sparkles size={18} color="#4f46e5" />
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                  Hiring Committee Recommendations
                </h3>
              </div>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                {results.recommendations.map((r, idx) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DETAILED QUESTION BREAKDOWN */}
      {activeTab === 'questions' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {results.questions?.map((q, idx) => {
            const isAnswered = Boolean(q.answer_text)
            const isExpanded = expandedQuestions[idx]
            const isResumeDerived = q.source_type?.startsWith('resume')

            return (
              <div
                key={idx}
                className="glass-card"
                style={{ padding: '22px', borderLeft: `4px solid ${isResumeDerived ? '#4f46e5' : '#06b6d4'}` }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontWeight: 800, color: 'var(--text-heading)', fontSize: '0.95rem' }}>
                      Q{q.question_index + 1}: {q.topic}
                    </span>
                    <span className={`provenance-badge ${isResumeDerived ? 'prov-badge-project' : 'prov-badge-general'}`}>
                      {q.section}
                    </span>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      Difficulty: {q.difficulty}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {isAnswered ? (
                      <span style={{
                        fontSize: '1.15rem',
                        fontWeight: 800,
                        color: q.score >= 7.0 ? '#059669' : (q.score >= 5.0 ? '#d97706' : '#dc2626')
                      }}>
                        {q.score}/10
                      </span>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        Not Attempted
                      </span>
                    )}

                    <button
                      onClick={() => toggleExpandQuestion(idx)}
                      style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                    >
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </button>
                  </div>
                </div>

                <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-heading)', marginBottom: '8px' }}>
                  {q.question_text}
                </div>

                <div style={{ fontSize: '0.78rem', color: 'var(--accent-indigo)', marginBottom: '8px' }}>
                  <strong>Question Provenance:</strong> {q.resume_section ? `Resume → ${q.resume_section}` : 'General Technical RAG'}
                  {q.source_item && ` → ${q.source_item}`}
                </div>

                {isExpanded && isAnswered && (
                  <div style={{
                    marginTop: '14px',
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.85rem'
                  }}>
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '4px' }}>
                        Candidate Answer:
                      </div>
                      <div style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                        {q.answer_text}
                      </div>
                    </div>

                    <div style={{ marginBottom: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '4px' }}>
                        Rubric Feedback:
                      </div>
                      <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                        {q.feedback}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '16px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      <span>Technical Accuracy: <strong style={{ color: '#4f46e5' }}>{q.technical_accuracy}/10</strong></span>
                      <span>Completeness: <strong style={{ color: '#7c3aed' }}>{q.completeness}/10</strong></span>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* TAB 3: RESUME COVERAGE */}
      {activeTab === 'coverage' && (
        <ResumeCoverageCard
          coverageData={results.coverage_summary || {}}
          totalQuestions={results.total_questions || 8}
          answeredCount={answeredQuestions.length}
        />
      )}

      {/* Bottom Actions */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '36px' }}>
        <button onClick={onRestart} className="btn-secondary" style={{ padding: '12px 28px' }}>
          <RotateCcw size={16} /> Start Another Candidate Screening
        </button>
      </div>
    </div>
  )
}
