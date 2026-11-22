import { useState } from 'react'
import { api, errMsg, useFetch, useMutate } from '../../hooks'

interface Submission {
  id: number
  assessment: number
  assessment_title: string
  student: number
  student_name: string
  answers: Record<string, unknown>
  score: number | null
  is_graded: boolean
  submitted_at: string
}

interface FeedbackDraft {
  content: string
  per_question?: { question?: string; feedback?: string; correct?: boolean }[]
  is_ai_assisted: boolean
}

export default function GradingPage() {
  const [onlyPending, setOnlyPending] = useState(true)
  const list = useFetch<Submission[]>(
    onlyPending ? '/submissions/all/?graded=0' : '/submissions/all/',
    [onlyPending],
  )

  const [gradeFor, setGradeFor] = useState<number | null>(null)
  const [score, setScore] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [draft, setDraft] = useState<FeedbackDraft | null>(null)
  const [draftErr, setDraftErr] = useState('')
  const [drafting, setDrafting] = useState(false)
  const [gradeErr, setGradeErr] = useState('')
  const [busyId, setBusyId] = useState<number | null>(null)

  function openGrade(s: Submission) {
    setGradeFor(s.id)
    setScore(s.score != null ? String(s.score) : '')
    setFeedbackText('')
    setDraft(null)
    setDraftErr('')
  }

  async function loadDraft(s: Submission) {
    setDrafting(true)
    setDraftErr('')
    try {
      const { data } = await api.post<FeedbackDraft>(`/feedback/${s.id}/`)
      setDraft(Array.isArray(data) ? (data[0] as FeedbackDraft) : data)
    } catch (e) {
      setDraftErr(errMsg(e))
    } finally {
      setDrafting(false)
    }
  }

  async function submitGrade(s: Submission) {
    setBusyId(s.id)
    setGradeErr('')
    try {
      await api.post(`/submissions/${s.id}/grade/`, {
        score: parseFloat(score),
        feedback: feedbackText.trim() || undefined,
      })
      setGradeFor(null)
      list.reload()
    } catch (e) {
      setGradeErr(errMsg(e))
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div>
      <h1>Grading</h1>

      <div className="row" style={{ marginBottom: 16 }}>
        <button
          className={`btn sm ${onlyPending ? '' : 'secondary'}`}
          onClick={() => setOnlyPending(true)}
        >
          Pending
        </button>
        <button
          className={`btn sm ${onlyPending ? 'secondary' : ''}`}
          onClick={() => setOnlyPending(false)}
        >
          All submissions
        </button>
      </div>

      {list.error && <div className="alert error">{list.error}</div>}
      {list.loading && <p className="muted">Loading…</p>}
      {(list.data || []).length === 0 && !list.loading && (
        <div className="card empty">
          {onlyPending ? 'No pending submissions — nothing to grade. 🎉' : 'No submissions yet.'}
        </div>
      )}

      {(list.data || []).map((s) => (
        <div key={s.id} className="card" style={{ marginBottom: 12 }}>
          <div className="row">
            <b>{s.student_name}</b>
            <span className="badge gray">{s.assessment_title}</span>
            {s.is_graded ? (
              <span className="badge green">Graded · {s.score}pts</span>
            ) : (
              <span className="badge amber">Pending</span>
            )}
            <span className="muted" style={{ marginLeft: 'auto' }}>
              <small>{new Date(s.submitted_at).toLocaleString()}</small>
            </span>
            <button className="btn sm secondary" onClick={() => openGrade(s)}>
              {gradeFor === s.id ? 'Close' : 'Grade'}
            </button>
          </div>

          {Object.keys(s.answers || {}).length > 0 && (
            <div className="muted" style={{ marginTop: 8, fontSize: 13 }}>
              Answers: {JSON.stringify(s.answers)}
            </div>
          )}

          {gradeFor === s.id && (
            <div className="card" style={{ marginTop: 12, background: 'var(--bg)' }}>
              <div className="row">
                <div style={{ flex: 1 }}>
                  <label>Score</label>
                  <input type="number" value={score} onChange={(e) => setScore(e.target.value)} placeholder="e.g. 4" />
                </div>
                <div style={{ flex: 2 }}>
                  <label>Feedback</label>
                  <textarea
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    rows={2}
                    placeholder="Write feedback, or use the AI draft…"
                  />
                </div>
              </div>
              {draftErr && <div className="alert error">{draftErr}</div>}
              {gradeErr && <div className="alert error">{gradeErr}</div>}

              {draft && (
                <div className="card" style={{ marginTop: 12 }}>
                  <div className="row" style={{ marginBottom: 6 }}>
                    <b>AI draft</b>
                    {draft.is_ai_assisted ? <span className="badge">AI</span> : <span className="badge gray">Template</span>}
                    <button className="btn sm secondary" style={{ marginLeft: 'auto' }} onClick={() => setFeedbackText(draft.content)}>
                      Use draft
                    </button>
                  </div>
                  <p className="muted" style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {draft.content}
                  </p>
                </div>
              )}

              <div className="actions">
                <button className="btn" disabled={busyId === s.id || !score} onClick={() => void submitGrade(s)}>
                  {busyId === s.id ? 'Saving…' : 'Submit grade'}
                </button>
                <button className="btn secondary" disabled={drafting} onClick={() => void loadDraft(s)}>
                  {drafting ? 'Drafting…' : 'Generate AI feedback'}
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
