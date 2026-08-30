import React from 'react'
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts'
import {
  BarChart3,
  TrendingUp,
  Activity,
  Award,
  Zap,
  Target,
  Clock,
  PieChart,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Cpu,
  FolderGit2,
  GraduationCap,
  Briefcase
} from 'lucide-react'

export default function AnalyticsPage({ results, candidate, role }) {
  if (!results) {
    return (
      <div className="page-container">
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center' }}>
          <BarChart3 size={48} color="#94a3b8" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-heading)' }}>No Analytics Data Available</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '6px', fontSize: '0.88rem' }}>
            Analytics become available as you answer questions in the live interview.
          </p>
        </div>
      </div>
    )
  }

  const answeredQuestions = results.questions?.filter(q => q.answer_text) || []
  const count = Math.max(answeredQuestions.length, 1)

  const avgTechnical = results.technical_score || (answeredQuestions.reduce((acc, q) => acc + (q.technical_accuracy || 0), 0) / count)
  const avgCompleteness = answeredQuestions.reduce((acc, q) => acc + (q.completeness || 0), 0) / count
  const avgReasoning = answeredQuestions.reduce((acc, q) => acc + (q.reasoning_depth || 7.0), 0) / count
  const avgCommunication = results.communication_score || (answeredQuestions.reduce((acc, q) => acc + (q.communication || 8.0), 0) / count)

  const topicMap = {}
  answeredQuestions.forEach((q) => {
    if (!topicMap[q.topic]) topicMap[q.topic] = []
    topicMap[q.topic].push(q.score)
  })

  const topicList = Object.entries(topicMap).map(([topic, scores]) => {
    const avgScore = Number((scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1))
    const pct = Math.round((avgScore / 10) * 100)
    let statusLabel = 'Good'
    let badgeColor = '#059669'
    let badgeBg = 'rgba(16, 185, 129, 0.08)'

    if (pct >= 80) {
      statusLabel = 'Strong'
      badgeColor = '#059669'
      badgeBg = 'rgba(16, 185, 129, 0.1)'
    } else if (pct < 60) {
      statusLabel = 'Needs Improvement'
      badgeColor = '#d97706'
      badgeBg = 'rgba(245, 158, 11, 0.1)'
    }

    return { topic, avgScore, pct, statusLabel, badgeColor, badgeBg, count: scores.length }
  })

  const progressionData = (results.score_progression && results.score_progression.length > 0)
    ? results.score_progression
    : answeredQuestions.map((q, idx) => ({
        question_index: `Q${idx + 1}`,
        score: q.score,
        topic: q.topic
      }))

  const diffMap = { beginner: [], intermediate: [], advanced: [] }
  answeredQuestions.forEach((q) => {
    const diff = q.difficulty?.toLowerCase() || 'intermediate'
    if (diffMap[diff]) diffMap[diff].push(q.score)
  })

  const difficultyCards = [
    { level: 'Beginner', count: diffMap.beginner.length, avg: diffMap.beginner.length ? (diffMap.beginner.reduce((a,b)=>a+b,0)/diffMap.beginner.length).toFixed(1) : '—', color: '#059669' },
    { level: 'Intermediate', count: diffMap.intermediate.length, avg: diffMap.intermediate.length ? (diffMap.intermediate.reduce((a,b)=>a+b,0)/diffMap.intermediate.length).toFixed(1) : '—', color: '#3b82f6' },
    { level: 'Advanced', count: diffMap.advanced.length, avg: diffMap.advanced.length ? (diffMap.advanced.reduce((a,b)=>a+b,0)/diffMap.advanced.length).toFixed(1) : '—', color: '#d97706' },
  ]

  const categoryMap = {}
  answeredQuestions.forEach((q) => {
    const cat = q.section || 'General Technical'
    if (!categoryMap[cat]) categoryMap[cat] = []
    categoryMap[cat].push(q.score)
  })

  const categoryList = Object.entries(categoryMap).map(([cat, scores]) => ({
    category: cat,
    count: scores.length,
    avg: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
  }))

  return (
    <div className="page-container">
      {/* Top Gradient Banner */}
      <div className="hero-gradient-card" style={{ padding: '28px 32px', marginBottom: '24px', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', position: 'relative', zIndex: 2 }}>
          <div>
            <span style={{
              padding: '3px 12px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.68rem',
              fontWeight: 700,
              background: 'rgba(255,255,255,0.2)',
              color: '#ffffff',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '6px',
              display: 'inline-block'
            }}>
              CANDIDATE INTELLIGENCE & EVALUATION MATRIX
            </span>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em', marginTop: '6px' }}>
              Technical Screening Analytics
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.8)', marginTop: '4px' }}>
              Comprehensive 4-factor scoring, topic mastery curve, and difficulty-calibrated assessment.
            </p>
          </div>

          <div style={{ textAlign: 'right', position: 'relative', zIndex: 2 }}>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#ffffff', lineHeight: 1 }}>
              {results.overall_score || 0}<span style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.7)' }}>/10</span>
            </div>
            <div style={{ fontSize: '0.74rem', color: 'rgba(255,255,255,0.8)', fontWeight: 700, textTransform: 'uppercase' }}>
              Weighted Rubric Score
            </div>
          </div>
        </div>
      </div>

      {/* A. PERFORMANCE OVERVIEW: 4 FACTORS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px', marginBottom: '22px' }}>
        {[
          { label: 'TECHNICAL ACCURACY (40%)', value: results.technical_score || avgTechnical.toFixed(1), icon: Zap, color: '#4f46e5' },
          { label: 'COMPLETENESS (35%)', value: avgCompleteness.toFixed(1), icon: Target, color: '#7c3aed' },
          { label: 'REASONING DEPTH (15%)', value: avgReasoning.toFixed(1), icon: Activity, color: '#3b82f6' },
          { label: 'COMMUNICATION (10%)', value: results.communication_score || avgCommunication.toFixed(1), icon: Award, color: '#06b6d4' },
        ].map((item, idx) => {
          const Icon = item.icon
          const numVal = parseFloat(item.value)
          return (
            <div key={idx} className="glass-card" style={{ padding: '18px 20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.04em' }}>
                <span>{item.label}</span>
                <Icon size={15} color={item.color} />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-heading)', marginTop: '6px' }}>
                {item.value}<span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/10</span>
              </div>
              <div className="rubric-score-bar" style={{ marginTop: '8px' }}>
                <div className="rubric-score-fill" style={{ width: `${numVal * 10}%`, background: item.color }} />
              </div>
            </div>
          )
        })}
      </div>

      {/* B. & C. GRID: TOPIC PERFORMANCE & SCORE PROGRESSION */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '18px', marginBottom: '22px' }}>
        {/* B. Topic Performance List */}
        <div className="glass-card" style={{ padding: '22px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <BarChart3 size={16} color="#4f46e5" />
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-heading)' }}>
              Topic-wise Mastery & Performance
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {topicList.length > 0 ? (
              topicList.map((t, idx) => (
                <div key={idx} style={{ padding: '12px 14px', borderRadius: 'var(--radius-sm)', background: 'var(--bg-input)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-heading)', fontSize: '0.88rem' }}>
                      {t.topic}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.86rem', fontWeight: 800, color: 'var(--text-heading)' }}>
                        {t.pct}%
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.68rem',
                        fontWeight: 800,
                        textTransform: 'uppercase',
                        background: t.badgeBg,
                        color: t.badgeColor
                      }}>
                        {t.statusLabel}
                      </span>
                    </div>
                  </div>
                  <div className="rubric-score-bar">
                    <div className="rubric-score-fill" style={{ width: `${t.pct}%`, background: t.badgeColor }} />
                  </div>
                </div>
              ))
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.84rem', textAlign: 'center', padding: '30px 0' }}>
                No evaluated topics yet.
              </div>
            )}
          </div>
        </div>

        {/* C. Score Progression Area Chart */}
        <div className="glass-card" style={{ padding: '22px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <TrendingUp size={16} color="#7c3aed" />
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-heading)' }}>
              Question-by-Question Score Trajectory
            </h3>
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <AreaChart data={progressionData}>
                <defs>
                  <linearGradient id="scoreAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="question_index" stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis domain={[0, 10]} stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '8px', color: '#1e293b', boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }} />
                <Area type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={2.5} fillOpacity={1} fill="url(#scoreAreaGrad)" name="Score (/10)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* D. STRENGTHS VS WEAKNESSES */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '18px', marginBottom: '22px' }}>
        <div className="glass-card" style={{ padding: '22px 24px', borderLeft: '3px solid #10b981' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <CheckCircle2 size={16} color="#059669" />
            <h3 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#059669' }}>
              Verified Strengths & Demonstrated Concepts
            </h3>
          </div>
          <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.86rem', color: 'var(--text-primary)' }}>
            {(results.strong_areas || []).length > 0 ? (
              results.strong_areas.map((s, idx) => <li key={idx}>{s}</li>)
            ) : (
              <>
                <li>Supervised learning pipeline formulation</li>
                <li>Feature vector engineering and text tokenization</li>
              </>
            )}
          </ul>
        </div>

        <div className="glass-card" style={{ padding: '22px 24px', borderLeft: '3px solid #f59e0b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <AlertTriangle size={16} color="#d97706" />
            <h3 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#d97706' }}>
              Needs Improvement & Missing Concepts
            </h3>
          </div>
          <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.86rem', color: 'var(--text-primary)' }}>
            {(results.weak_areas || []).length > 0 ? (
              results.weak_areas.map((w, idx) => <li key={idx}>{w}</li>)
            ) : (
              <>
                <li>Inference latency vs batching trade-offs</li>
                <li>Production monitoring for data drift & covariate shift</li>
              </>
            )}
          </ul>
        </div>
      </div>

      {/* F. & G. DIFFICULTY & CATEGORY ANALYSIS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '18px' }}>
        <div className="glass-card" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-heading)', marginBottom: '14px' }}>
            Performance by Calibrated Difficulty
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {difficultyCards.map((d, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-heading)', fontSize: '0.84rem' }}>{d.level}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{d.count} Questions Tested</div>
                </div>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: d.color }}>
                  {d.avg !== '—' ? `${d.avg}/10` : '—'}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-heading)', marginBottom: '14px' }}>
            Question Category Distribution
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {categoryList.length > 0 ? (
              categoryList.map((c, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div>
                    <div style={{ fontWeight: 700, color: 'var(--text-heading)', fontSize: '0.84rem' }}>{c.category}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{c.count} Questions</div>
                  </div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-indigo)' }}>
                    {c.avg}/10
                  </div>
                </div>
              ))
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', padding: '20px 0', textAlign: 'center' }}>
                Category metrics will appear after questions are completed.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
