import { useState } from 'react'
import { api, errMsg, useFetch } from '../../hooks'

interface Topic {
  id: number
  title: string
  description: string
  subject_name: string
  quiz_generated: boolean
  video_generated: boolean
  material_file: string | null
}

interface QuizQ {
  id: number
  text: string
  q_type: string
  options: string[]
  marks: number
}

interface Paper {
  topic_id: number
  questions: QuizQ[]
}

export default function SelfStudyPage() {
  const list = useFetch<Topic[]>('/me/topics/')
  const [quizFor, setQuizFor] = useState<number | null>(null)
  const [quiz, setQuiz] = useState<QuizQ[] | null>(null)
  const [quizErr, setQuizErr] = useState('')
  const [loadingQuiz, setLoadingQuiz] = useState(false)

  async function loadQuiz(t: Topic) {
    if (quizFor === t.id) {
      setQuizFor(null)
      setQuiz(null)
      return
    }
    setQuizFor(t.id)
    setQuiz(null)
    setQuizErr('')
    setLoadingQuiz(true)
    try {
      const { data } = await api.get<Paper>(`/topics/${t.id}/questions/`)
      setQuiz(data.questions || [])
    } catch (e: unknown) {
      const err = e as { response?: { status?: number } }
      setQuizErr(
        err?.response?.status === 404 && typeof (e as { response?: { data?: { detail?: string } } }).response?.data?.detail === 'string'
          ? (e as { response: { data: { detail: string } } }).response.data.detail
          : errMsg(e),
      )
    } finally {
      setLoadingQuiz(false)
    }
  }

  return (
    <div>
      <h1>Self-Study</h1>
      <p className="muted">Study material posted by your teachers — plus AI quizzes and the AI tutor.</p>

      {list.error && <div className="alert error">{list.error}</div>}
      {list.loading && <p className="muted">Loading…</p>}
      {(list.data || []).length === 0 && !list.loading && (
        <div className="card empty">No study topics for your class yet.</div>
      )}

      <div className="grid cols-2">
        {(list.data || []).map((t) => (
          <div key={t.id} className="card">
            <div className="row" style={{ marginBottom: 6 }}>
              <h3 style={{ margin: 0 }}>{t.title}</h3>
              <span className="badge gray" style={{ marginLeft: 'auto' }}>
                {t.subject_name}
              </span>
            </div>
            <p className="muted" style={{ margin: '0 0 10px' }}>
              {t.description}
            </p>
            <div className="row" style={{ marginBottom: 10 }}>
              {t.quiz_generated ? (
                <span className="badge green">AI quiz ready</span>
              ) : (
                <span className="badge gray">No quiz</span>
              )}
              {t.video_generated && <span className="badge">Video lesson</span>}
            </div>
            <div className="row">
              <button className="btn sm" disabled={loadingQuiz || !t.quiz_generated} onClick={() => void loadQuiz(t)}>
                {quizFor === t.id ? 'Hide quiz' : 'Practice quiz'}
              </button>
              {t.material_file && (
                <a className="btn sm secondary" href={t.material_file} target="_blank" rel="noreferrer">
                  Material
                </a>
              )}
            </div>

            {quizErr && <div className="alert error" style={{ marginTop: 10 }}>{quizErr}</div>}
            {quizFor === t.id && quiz && (
              <div style={{ marginTop: 14 }}>
                {quiz.length === 0 && <p className="muted">No questions generated yet.</p>}
                {quiz.map((q, i) => (
                  <div key={q.id} className="card" style={{ background: 'var(--bg)', marginTop: 8 }}>
                    <b>
                      Q{i + 1}. {q.text}
                    </b>
                    {q.q_type === 'mcq' && q.options && q.options.length > 0 && (
                      <ol className="muted" style={{ margin: '6px 0 0', paddingLeft: 20 }}>
                        {q.options.map((o, oi) => (
                          <li key={oi}>{o}</li>
                        ))}
                      </ol>
                    )}
                  </div>
                ))}
              </div>
            )}
            {quizFor === t.id && !quiz && !loadingQuiz && !quizErr && <p className="muted">Loading…</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
