import React from 'react'
import {
  User,
  Cpu,
  FolderGit2,
  GraduationCap,
  Sparkles,
  ArrowRight,
  Brain,
  Layers,
  Code2,
  CheckCircle2
} from 'lucide-react'

export default function CandidateProfilePage({
  candidate,
  role,
  onStartInterview,
  hasActiveSession
}) {
  if (!candidate) {
    return (
      <div className="page-container">
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center' }}>
          <User size={48} color="#64748b" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>No Candidate Profile Loaded</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            Please upload a PDF resume from the Dashboard to extract candidate skills and projects.
          </p>
        </div>
      </div>
    )
  }

  const allSkills = candidate.skills || []
  const aimlTech = candidate.ai_ml_technologies || []
  const projects = candidate.projects || []

  return (
    <div className="page-container">
      {/* Top Profile Header Card */}
      <div className="glass-card-elevated" style={{ padding: '32px 36px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, #0d9488, #14b8a6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '1.8rem',
              fontWeight: 800,
              boxShadow: '0 4px 20px rgba(20, 184, 166, 0.3)'
            }}>
              {(candidate.name || 'C')[0]}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h2 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#f8fafc' }}>
                  {candidate.name || 'Extracted Candidate Profile'}
                </h2>
                <span className="role-pill-badge" style={{ textTransform: 'uppercase' }}>
                  {role ? role.replace('_', ' ') : 'AI/ML Engineer'}
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                ID: {candidate.candidate_id?.slice(0, 12)}... • Extracted with PyMuPDF & Structured LLM Parser
              </p>
            </div>
          </div>

          <button onClick={onStartInterview} className="btn-primary" style={{ padding: '12px 24px' }}>
            {hasActiveSession ? (
              <>Resume Live Interview <ArrowRight size={16} /></>
            ) : (
              <>Start Technical Screening <Sparkles size={16} /></>
            )}
          </button>
        </div>
      </div>

      {/* Grid: Skills Cloud & Projects */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '22px', marginBottom: '24px' }}>
        {/* Skills Breakdown */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Cpu size={18} color="#2dd4bf" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
              Detected Skills & Technologies ({allSkills.length})
            </h3>
          </div>

          {aimlTech.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--brand-teal-light)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                AI/ML & Deep Learning Stack
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {aimlTech.map((tech, idx) => (
                  <span key={idx} className="signal-pill" style={{ background: 'rgba(20, 184, 166, 0.15)', borderColor: 'rgba(20, 184, 166, 0.4)' }}>
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
              Core Technical Skills & Frameworks
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {allSkills.map((sk, idx) => (
                <span key={idx} className="signal-pill">{sk}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Education & Background */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <GraduationCap size={18} color="#10b981" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
              Academic & Education Foundation
            </h3>
          </div>

          {candidate.education?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {candidate.education.map((edu, idx) => (
                <div key={idx} style={{ padding: '12px 14px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.92rem' }}>
                    {edu.degree || 'Degree'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {edu.institution || edu.field || 'Institution'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Candidate education and background profile extracted from resume.
            </div>
          )}
        </div>
      </div>

      {/* Portfolio Projects Section */}
      <div className="glass-card" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
          <FolderGit2 size={18} color="#06b6d4" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
            Detected Portfolio Projects ({projects.length})
          </h3>
        </div>

        {projects.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            {projects.map((proj, idx) => (
              <div
                key={idx}
                style={{
                  padding: '18px 20px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}
              >
                <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.98rem' }}>
                  {proj.name}
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {proj.description || 'Production system implementation & architectural pipeline.'}
                </div>
                {proj.technologies?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '6px' }}>
                    {proj.technologies.map((t, tidx) => (
                      <span key={tidx} className="signal-pill" style={{ fontSize: '0.7rem' }}>{t}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
            No explicit project sections extracted. General technical and skills questions will be calibrated.
          </div>
        )}
      </div>
    </div>
  )
}
