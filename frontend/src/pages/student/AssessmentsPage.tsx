import { useState } from 'react'
import { api, errMsg, useFetch } from '../../hooks'

interface Assessment {
  id: number
  title: string
  kind: string
  total_marks: number
  subject_name: string
  due_at: string | null
}

interface Q {
  id: number
  text: string
  q_type: string
  options: string[]
  marks: number
}

interface Paper {
  assessment: number
  title: string
  total_marks: number
  questions: Q[]
}

interface SubmitResult {
  id: number
  score: number | null
  is_graded: boolean
}

export default function AssessmentsPage() {
  const list = useFetch<Assessment[]>('/me/assessments/')
  const [active, setActive] = useState<Paper | null>(null)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [loadingPaper, setLoadingPaper] = useState(false)
  const [paperErr, setPaperErr] = useState('')
  const [result, setResult] = useState<SubmitResult | null>(null)
  const [submitBusy, setSubmitBusy] = useState(false)
  const [submitErr, setSubmitErr] = useState('')

  async function open(a: Assessment) {
    setLoadingPaper(true)
    setPaperErr('')
    setResult(null)
    setAnswers({})
    try {
      const { data } = await api.get<Paper>(`/me/assessments/${a.id}/questions/`)
      setActive(data)
    } catch (e) {
      setPaperErr(errMsg(e))
      setActive(null)
    } finally {
      setLoadingPaper(false)
    }
  }

  async function submit() {
    if (!active) return
    setSubmitBusy(true)
    setSubmitErr('')
    try {
      const { data } = await api.post<SubmitResult>('/submissions/', {
        assessment: active.assessment,
        answers,
      })
      setResult(data)
      list.reload()
    } catch (e) {
      setSubmitErr(errMsg(e))
    } finally {
      setSubmitBusy(false)
    }
  }

  return (
    <div>
      <h1>Assessments</h1>
      {list.error && <div className="alert error">{list.error}</div>}
      {list.loading && <p className="muted">Loading…</p>}
      {(list.data || []).length === 0 && !list.loading && (
        <div className="card empty">No published assessments for your class yet.</div>
      )}

      <div className="grid cols-2">
        {(list.data || []).map((a) => (
          <div key={a.id} className="card">
            <div className="row" style={{ marginBottom: 6 }}>
              <h3 style={{ margin: 0 }}>{a.title}</h3>
              <span className="badge gray">{a.kind}</span>
              <span className="badge" style={{ marginLeft: 'auto' }}>
                {a.total_marks} marks
              </span>
            </div>
            <p className="muted" style={{ margin: '0 0 10px' }}>
              {a.subject_name}
              {a.due_at ? ` · due ${new Date(a.due_at).toLocaleDateString()}` : ''}
            </p>
            <button className="btn sm" disabled={loadingPaper} onClick={() => void open(a)}>
              {loadingPaper ? 'Loading…' : 'Take it'}
            </button>
          </div>
        ))}
      </div>

      {paperErr && <div className="alert error">{paperErr}</div>}

      {active && (
        <div className="card" style={{ marginTop: 20 }} data-testid="paper">
          <div className="row">
            <h2 style={{ margin: 0 }}>{active.title}</h2>
            <button className="btn sm secondary" style={{ marginLeft: 'auto' }} onClick={() => setActive(null)}>
              Close
            </button>
          </div>

          {result && (
            <div className={`alert ${result.is_graded ? 'success' : 'info'}`}>
              {result.is_graded
                ? `Submitted! You scored ${result.score}/${active.total_marks}.`
                : `Submitted! Auto-graded part: ${result.score} points. Written answers will be graded by your teacher.`}
            </div>
          )}

          {active.questions.map((q, qi) => (
            <div key={q.id} className="card" style={{ marginTop: 12, background: 'var(--bg)' }}>
              <b>
                Q{qi + 1}. {q.text}
              </b>
              <span className="badge gray" style={{ marginLeft: 8 }}>
                {q.marks} pt
              </span>
              {q.q_type === 'mcq' && q.options && q.options.length > 0 && (
                <div className="stack" style={{ marginTop: 8 }}>
                  {q.options.map((opt, oi) => (
                    <label key={oi} style={{ display: 'flex', alignItems: 'center', gap: 8, margin: 0, fontWeight: 400 }}>
                      <input
                        type="radio"
                        name={`q-${q.id}`}
                        style={{ width: 'auto' }}
                        checked={answers[q.id] === oi}
                        onChange={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                      />
                      {opt}
                    </label>
                  ))}
                </div>
              )}
              {q.q_type !== 'mcq' && (
                <textarea
                  rows={2}
                  value={answers[q.id] != null ? String(answers[q.id]) : ''}
                  onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value as unknown as number }))}
                  placeholder="Your answer…"
                  style={{ marginTop: 8 }}
                />
              )}
            </div>
          ))}

          {submitErr && <div className="alert error">{submitErr}</div>}
          {active.questions.length === 0 && <p className="muted">This assessment has no questions yet.</p>}
          <div className="actions">
            <button className="btn" disabled={submitBusy || active.questions.length === 0} onClick={() => void submit()}>
              {submitBusy ? 'Submitting…' : 'Submit answers'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
