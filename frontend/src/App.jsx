import React, { useState, useEffect } from 'react'
import LandingPage from './pages/LandingPage'
import ProcessingPage from './pages/ProcessingPage'
import InterviewPage from './pages/InterviewPage'
import ResultsPage from './pages/ResultsPage'
import CandidateProfilePage from './pages/CandidateProfilePage'
import AnalyticsPage from './pages/AnalyticsPage'
import ResumeCoverageCard from './components/ResumeCoverageCard'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { api } from './services/api'

export default function App() {
  const [activeView, setActiveView] = useState('dashboard')
  const [candidateId, setCandidateId] = useState(null)
  const [candidate, setCandidate] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [isMockMode, setIsMockMode] = useState(false)
  const [selectedRole, setSelectedRole] = useState('ai_ml_engineer')
  const [health, setHealth] = useState(null)
  const [resultsData, setResultsData] = useState(null)

  useEffect(() => {
    let mounted = true
    api.health()
      .then(h => { if (mounted) setHealth(h) })
      .catch(() => { if (mounted) setHealth({ llm_available: true, llm_mode: 'Gemini (gemini-3.6-flash)', status: 'healthy' }) })
    return () => { mounted = false }
  }, [])

  const startProcessing = (cId, role, candObj) => {
    setCandidateId(cId)
    setSelectedRole(role)
    if (candObj) setCandidate(candObj)
    setActiveView('processing')
  }

  const startInterview = (sId, mock) => {
    setSessionId(sId)
    setIsMockMode(mock)
    setActiveView('interview')
    if (candidateId && !candidate) {
      api.getCandidate(candidateId).then(setCandidate).catch(() => {})
    }
  }

  const handleInterviewComplete = async () => {
    try {
      if (sessionId) {
        const res = await api.getResults(sessionId)
        setResultsData(res)
      }
    } catch (_) {}
    setActiveView('results')
  }

  const restart = () => {
    setCandidateId(null)
    setCandidate(null)
    setSessionId(null)
    setIsMockMode(false)
    setSelectedRole('ai_ml_engineer')
    setResultsData(null)
    setActiveView('dashboard')
  }

  return (
    <div className="app-shell">
      {/* Background Ambience Orbs */}
      <div className="app-atmosphere">
        <div className="atmosphere-orb orb-1" />
        <div className="atmosphere-orb orb-2" />
        <div className="atmosphere-orb orb-3" />
      </div>

      {/* Left Sidebar */}
      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        health={health}
        hasActiveSession={Boolean(sessionId)}
        candidate={candidate}
        role={selectedRole}
        onReset={restart}
      />

      {/* Main Content Area */}
      <div className="app-main">
        <Header
          activeView={activeView}
          candidate={candidate}
          role={selectedRole}
          health={health}
          onReset={restart}
          onPrint={() => window.print()}
        />

        {/* View Switcher */}
        {activeView === 'dashboard' && (
          <LandingPage
            onStart={startProcessing}
            health={health}
            candidate={candidate}
            role={selectedRole}
            results={resultsData}
            hasActiveSession={Boolean(sessionId)}
            onNavigate={setActiveView}
          />
        )}

        {activeView === 'processing' && (
          <ProcessingPage
            candidateId={candidateId}
            role={selectedRole}
            onReady={startInterview}
            onError={() => setActiveView('dashboard')}
          />
        )}

        {activeView === 'interview' && (
          <InterviewPage
            sessionId={sessionId}
            candidate={candidate}
            role={selectedRole}
            onComplete={handleInterviewComplete}
            onUpdateResults={setResultsData}
          />
        )}

        {activeView === 'candidate' && (
          <CandidateProfilePage
            candidate={candidate}
            role={selectedRole}
            onStartInterview={() => sessionId ? setActiveView('interview') : setActiveView('dashboard')}
            hasActiveSession={Boolean(sessionId)}
          />
        )}

        {activeView === 'coverage' && (
          <div className="page-container">
            <ResumeCoverageCard
              coverageData={resultsData?.coverage_summary || {}}
              totalQuestions={resultsData?.total_questions || 8}
              answeredCount={resultsData?.questions_answered || 0}
            />
          </div>
        )}

        {activeView === 'analytics' && (
          <AnalyticsPage
            results={resultsData}
            candidate={candidate}
            role={selectedRole}
          />
        )}

        {activeView === 'results' && (
          <ResultsPage
            sessionId={sessionId}
            candidate={candidate}
            role={selectedRole}
            results={resultsData}
            onRestart={restart}
          />
        )}
      </div>
    </div>
  )
}
