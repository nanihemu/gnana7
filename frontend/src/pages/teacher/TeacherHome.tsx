import { useFetch } from '../../hooks'

interface Topic {
  id: number
  title: string
  quiz_generated: boolean
  video_generated: boolean
}
interface Assessment {
  id: number
  title: string
}
interface Submission {
  id: number
  is_graded: boolean
}

export default function TeacherHome() {
  const topics = useFetch<Topic[]>('/topics/')
  const assessments = useFetch<Assessment[]>('/assessments/')
  const submissions = useFetch<Submission[]>('/submissions/all/')

  if (topics.loading || assessments.loading || submissions.loading)
    return <p className="muted">Loading…</p>

  const subs = submissions.data || []
  const pending = subs.filter((s) => !s.is_graded).length

  return (
    <div>
      <h1>Teacher Overview</h1>
      <div className="grid cols-3">
        <div className="card stat">
          <div className="label">Topics</div>
          <div className="value">{(topics.data || []).length}</div>
          <small className="muted">
            {(topics.data || []).filter((t) => t.quiz_generated).length} with AI quizzes
          </small>
        </div>
        <div className="card stat">
          <div className="label">Assessments</div>
          <div className="value">{(assessments.data || []).length}</div>
        </div>
        <div className="card stat">
          <div className="label">Submissions pending</div>
          <div className="value">{pending}</div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h2>AI toolkit</h2>
        <ul className="muted">
          <li>
            <b>Topics &amp; AI</b> — post study material, then generate quizzes, avatar videos and
            keep the RAG index fresh.
          </li>
          <li>
            <b>Grading</b> — see student submissions, auto-graded MCQs and draft AI feedback.
          </li>
        </ul>
      </div>
    </div>
  )
}
