import React, { useState, useEffect } from 'react'
import {
  Send,
  RotateCcw,
  ArrowRight,
  StopCircle,
  Clock,
  Sparkles,
  Award,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Cpu,
  Layers
} from 'lucide-react'
import { api } from '../services/api'
import QuestionProvenanceCard from '../components/QuestionProvenanceCard'

export default function InterviewPage({
  sessionId,
  candidate,
  role,
  onComplete,
  onUpdateResults
}) {
  const [question, setQuestion] = useState(null)
  const [answerText, setAnswerText] = useState('')
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)
  const [advancing, setAdvancing] = useState(false)
  const [error, setError] = useState(null)
  const [attemptCount, setAttemptCount] = useState(1)
  const [showEndModal, setShowEndModal] = useState(false)
  const [endingEarly, setEndingEarly] = useState(false)

  useEffect(() => {
    loadCurrentQuestion()
  }, [sessionId])

  const loadCurrentQuestion = async () => {
    setLoading(true)
    setError(null)
    try {
      const q = await api.getCurrentQuestion(sessionId)
      setQuestion(q)
      setAnswerText('')
      setEvaluation(null)
      setAttemptCount(1)
    } catch (err) {
      setError(err.message || 'Failed to fetch current question')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!answerText.trim() || evaluating) return
    setEvaluating(true)
    setError(null)

    try {
      const res = await api.submitAnswer(sessionId, answerText, attemptCount > 1)
      setEvaluation(res)
      try {
        const fullResults = await api.getResults(sessionId)
        if (onUpdateResults) onUpdateResults(fullResults)
      } catch (_) {}
    } catch (err) {
      setError(err.message || 'Failed to submit answer for evaluation.')
    } finally {
      setEvaluating(false)
    }
  }

  const handleRetry = async () => {
    try {
      const q = await api.retryQuestion(sessionId)
      setQuestion(q)
      setEvaluation(null)
      setAttemptCount(prev => prev + 1)
    } catch (err) {
      setError(err.message || 'Failed to retry question.')
    }
  }

  const handleNextQuestion = async () => {
    setAdvancing(true)
    setError(null)
    try {
      if (!evaluation?.has_next_question) {
        const finalResults = await api.getResults(sessionId)
        if (onUpdateResults) onUpdateResults(finalResults)
        onComplete()
        return
      }
      const nextQ = await api.nextQuestion(sessionId)
      setQuestion(nextQ)
      setAnswerText('')
      setEvaluation(null)
      setAttemptCount(1)
    } catch (err) {
      setError(err.message || 'Failed to advance to next question.')
    } finally {
      setAdvancing(false)
    }
  }

  const handleConfirmEndEarly = async () => {
    setEndingEarly(true)
    try {
      const finalReport = await api.finishInterview(sessionId)
      if (onUpdateResults) onUpdateResults(finalReport)
      setShowEndModal(false)
      onComplete()
    } catch (err) {
      setError(err.message || 'Failed to conclude interview early.')
      setShowEndModal(false)
    } finally {
      setEndingEarly(false)
    }
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
          Grounding Adaptive Question from Vector Store...
        </h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px', fontSize: '0.88rem' }}>
          Querying ChromaDB embedding collections and synthesizing candidate-anchored question.
        </p>
      </div>
    )
  }

  const progressPercent = question
    ? Math.round(((question.question_index + 1) / question.total_questions) * 100)
    : 0

  const wordCount = answerText.trim().split(/\s+/).filter(Boolean).length

  return (
    <div className="page-container">
      {/* Top Session Progress Bar */}
      <div className="glass-card" style={{ padding: '18px 24px', marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-heading)' }}>
              Question {question?.question_index + 1} of {question?.total_questions}
            </span>
            {attemptCount > 1 && (
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '2px 10px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(245, 158, 11, 0.08)',
                color: '#d97706',
                border: '1px solid rgba(245, 158, 11, 0.25)'
              }}>
                Attempt #{attemptCount} (Refining Answer)
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Screening Progress: {progressPercent}%
            </span>
            <button
              onClick={() => setShowEndModal(true)}
              className="btn-danger"
              style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            >
              <StopCircle size={13} /> End Interview Early
            </button>
          </div>
        </div>

        <div style={{ height: '6px', background: '#e2e8f0', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${progressPercent}%`,
            background: 'var(--gradient-bar)',
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.4s ease'
          }} />
        </div>
      </div>

      {/* QUESTION PROVENANCE CARD */}
      <QuestionProvenanceCard question={question} candidate={candidate} />

      {/* Main Question Card */}
      <div className="glass-card-elevated" style={{ padding: '28px 32px', marginBottom: '24px' }}>
        <div className="question-text-main">
          {question?.question_text}
        </div>

        {question?.expected_concepts?.length > 0 && (
          <div style={{
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.82rem',
            color: 'var(--text-secondary)'
          }}>
            <strong style={{ color: 'var(--text-heading)' }}>Key Competencies Evaluated:</strong>{' '}
            {question.expected_concepts.join(' • ')}
          </div>
        )}
      </div>

      {/* Answer Editor Section */}
      <div className="editor-container">
        <textarea
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          disabled={evaluating || evaluation !== null}
          placeholder="Provide your comprehensive technical explanation. Walk through architectural design decisions, trade-offs, formulas/algorithms, and production considerations..."
          className="answer-textarea"
        />

        <div className="editor-footer">
          <div>
            <span>{wordCount} words</span> • <span>{answerText.length} characters</span>
          </div>

          {!evaluation && (
            <button
              onClick={handleSubmit}
              disabled={evaluating || !answerText.trim()}
              className="btn-primary"
            >
              {evaluating ? (
                <>Evaluating via Rubric...</>
              ) : (
                <>
                  <Send size={16} /> Submit Answer for Evaluation →
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Evaluation Results Card */}
      {evaluation && (
        <div className="eval-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Award size={20} color="#4f46e5" />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-heading)' }}>
                Multi-Factor Rubric Evaluation
              </h3>
            </div>
            <div style={{
              fontSize: '1.45rem',
              fontWeight: 800,
              color: evaluation.score >= 7.0 ? '#059669' : (evaluation.score >= 5.0 ? '#d97706' : '#dc2626')
            }}>
              {evaluation.score}/10
            </div>
          </div>

          {/* 4 Rubric Factor Bars */}
          <div className="rubric-grid">
            <div className="rubric-pill-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Technical Accuracy (40%)</span>
                <strong style={{ color: '#4f46e5' }}>{evaluation.technical_accuracy}/10</strong>
              </div>
              <div className="rubric-score-bar">
                <div className="rubric-score-fill" style={{ width: `${evaluation.technical_accuracy * 10}%`, background: '#4f46e5' }} />
              </div>
            </div>

            <div className="rubric-pill-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Completeness (35%)</span>
                <strong style={{ color: '#7c3aed' }}>{evaluation.completeness}/10</strong>
              </div>
              <div className="rubric-score-bar">
                <div className="rubric-score-fill" style={{ width: `${evaluation.completeness * 10}%`, background: '#7c3aed' }} />
              </div>
            </div>

            <div className="rubric-pill-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Reasoning Depth (15%)</span>
                <strong style={{ color: '#3b82f6' }}>{evaluation.reasoning_depth}/10</strong>
              </div>
              <div className="rubric-score-bar">
                <div className="rubric-score-fill" style={{ width: `${evaluation.reasoning_depth * 10}%`, background: '#3b82f6' }} />
              </div>
            </div>

            <div className="rubric-pill-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Communication (10%)</span>
                <strong style={{ color: '#06b6d4' }}>{evaluation.communication}/10</strong>
              </div>
              <div className="rubric-score-bar">
                <div className="rubric-score-fill" style={{ width: `${evaluation.communication * 10}%`, background: '#06b6d4' }} />
              </div>
            </div>
          </div>

          {/* Qualitative Feedback */}
          <div style={{
            padding: '14px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.88rem',
            lineHeight: 1.6,
            color: 'var(--text-primary)',
            marginBottom: '16px'
          }}>
            {evaluation.feedback}
          </div>

          {/* Strengths and Missing Concepts */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '20px' }}>
            {evaluation.strengths?.length > 0 && (
              <div style={{ padding: '12px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.15)', borderLeft: '3px solid #10b981' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#059669', marginBottom: '6px' }}>
                  ✓ Verified Strengths
                </div>
                <ul style={{ paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                  {evaluation.strengths.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>
            )}

            {evaluation.missing_concepts?.length > 0 && (
              <div style={{ padding: '12px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(239, 68, 68, 0.04)', border: '1px solid rgba(239, 68, 68, 0.15)', borderLeft: '3px solid #ef4444' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#dc2626', marginBottom: '6px' }}>
                  ⚠ Missing Concepts
                </div>
                <ul style={{ paddingLeft: '16px', fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                  {evaluation.missing_concepts.map((m, idx) => (
                    <li key={idx}>{m}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Post-Evaluation Actions: Retry vs Next */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
            <button
              onClick={handleRetry}
              className="btn-retry"
            >
              <RotateCcw size={16} /> Retry Question (Refine Response)
            </button>

            <button
              onClick={handleNextQuestion}
              disabled={advancing}
              className="btn-primary"
            >
              {evaluation.has_next_question ? (
                <>Next Question → <ArrowRight size={16} /></>
              ) : (
                <>View Final Assessment Report → <Award size={16} /></>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Confirmation Modal for Ending Early */}
      {showEndModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#d97706', marginBottom: '14px' }}>
              <AlertTriangle size={24} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-heading)' }}>
                End Interview Session Early?
              </h3>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
              You have answered <strong>{question?.question_index + (evaluation ? 1 : 0)}</strong> questions so far.
              If you conclude early, the final report and hiring recommendation will be calculated strictly based on the evidence submitted.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                onClick={() => setShowEndModal(false)}
                className="btn-secondary"
                disabled={endingEarly}
              >
                Continue Interview
              </button>
              <button
                onClick={handleConfirmEndEarly}
                className="btn-danger"
                disabled={endingEarly}
              >
                {endingEarly ? 'Synthesizing Report...' : 'Yes, Conclude & View Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
