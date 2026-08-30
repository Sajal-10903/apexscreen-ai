const API_BASE = '/api';

async function request(path, options = {}) {
  let url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  // Don't set Content-Type for FormData (browser automatically sets boundary)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  let response;
  try {
    response = await fetch(url, config);
  } catch (err) {
    // If relative proxy fetch failed, fallback to explicit backend URL
    if (url.startsWith('/api')) {
      url = `http://localhost:8000${url}`;
      response = await fetch(url, config);
    } else {
      throw err;
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health
  health: () => request('/health'),

  // Roles
  getRoles: () => request('/roles'),

  // Resume & Candidate
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/resume/upload', { method: 'POST', body: formData });
  },

  getCandidate: (candidateId) =>
    request(`/resume/${candidateId}`),

  // Interview
  createInterview: (candidateId, role) =>
    request('/interviews', {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, role }),
    }),

  getInterviewStatus: (sessionId) =>
    request(`/interviews/${sessionId}`),

  getCurrentQuestion: (sessionId) =>
    request(`/interviews/${sessionId}/current-question`),

  submitAnswer: (sessionId, answerText, isRetry = false) =>
    request(`/interviews/${sessionId}/answers`, {
      method: 'POST',
      body: JSON.stringify({ answer_text: answerText, is_retry: isRetry }),
    }),

  retryQuestion: (sessionId) =>
    request(`/interviews/${sessionId}/retry`, { method: 'POST' }),

  nextQuestion: (sessionId) =>
    request(`/interviews/${sessionId}/next-question`, { method: 'POST' }),

  finishInterview: (sessionId) =>
    request(`/interviews/${sessionId}/finish`, { method: 'POST' }),

  getResults: (sessionId) =>
    request(`/interviews/${sessionId}/results`),
};
