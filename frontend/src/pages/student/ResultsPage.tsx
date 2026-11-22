import { useFetch } from '../../hooks'

interface Result {
  id: number
  assessment: number
  assessment_title: string
  score: number | null
  is_graded: boolean
  submitted_at: string
}

export default function ResultsPage() {
  const { data, loading, error } = useFetch<Result[]>('/me/results/')

  return (
    <div>
      <h1>My Results</h1>
      {error && <div className="alert error">{error}</div>}
      {loading && <p className="muted">Loading…</p>}
      {(data || []).length === 0 && !loading && (
        <div className="card empty">No graded results yet — take an assessment first.</div>
      )}
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Assessment</th>
              <th>Score</th>
              <th>Status</th>
              <th>Submitted</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((r) => (
              <tr key={r.id}>
                <td>{r.assessment_title}</td>
                <td>
                  <b>{r.score != null ? r.score : '—'}</b>
                </td>
                <td>
                  {r.is_graded ? (
                    <span className="badge green">Graded</span>
                  ) : (
                    <span className="badge amber">Pending</span>
                  )}
                </td>
                <td className="muted">
                  <small>{new Date(r.submitted_at).toLocaleString()}</small>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
