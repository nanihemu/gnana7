import { useFetch } from '../../hooks'

interface Assessment {
  id: number
  title: string
}
interface Result {
  id: number
  assessment_title: string
  score: number | null
}
interface Topic {
  id: number
  title: string
  quiz_generated: boolean
}

export default function StudentHome() {
  const assessments = useFetch<Assessment[]>('/me/assessments/')
  const results = useFetch<Result[]>('/me/results/')
  const topics = useFetch<Topic[]>('/me/topics/')

  if (assessments.loading || results.loading || topics.loading)
    return <p className="muted">Loading…</p>

  const published = (assessments.data || []).length

  return (
    <div>
      <h1>Student Overview</h1>
      <div className="grid cols-3">
        <div className="card stat">
          <div className="label">Published assessments</div>
          <div className="value">{published}</div>
        </div>
        <div className="card stat">
          <div className="label">Graded results</div>
          <div className="value">{(results.data || []).length}</div>
        </div>
        <div className="card stat">
          <div className="label">Self-study topics</div>
          <div className="value">{(topics.data || []).length}</div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h2>How to get the most out of Gnana</h2>
        <ul className="muted">
          <li>Take <b>assessments</b> for instant MCQ auto-grading feedback.</li>
          <li>Review <b>results</b> and your <b>performance</b> trends per subject.</li>
          <li>Study at your own pace in <b>self-study</b> — and ask the <b>AI tutor</b> (bottom-right) anything about your school's material.</li>
        </ul>
      </div>
    </div>
  )
}
