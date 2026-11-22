import { Link, useParams } from 'react-router-dom'
import { useFetch } from '../../hooks'

interface Perf {
  student_id: number
  subjects: { subject: string; percentage: number; status: string }[]
}
interface SummaryResp {
  student_id: number
  summary: string
}
interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  created_at: string
}

export default function ChildPage() {
  const { id } = useParams()
  const perf = useFetch<Perf>(`/performance/${id}/`)
  const summary = useFetch<SummaryResp>(`/performance/${id}/summary/`)
  const achievements = useFetch<Achievement[]>(`/achievements/student/${id}/`)

  return (
    <div>
      <div className="row" style={{ marginBottom: 12 }}>
        <Link to="/" className="muted">
          ← My children
        </Link>
      </div>
      <h1>Child Progress</h1>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>AI Summary</h2>
        {summary.loading && <p className="muted">Generating…</p>}
        {summary.error && <div className="alert error">{summary.error}</div>}
        {summary.data && <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, margin: 0 }}>{summary.data.summary}</p>}
      </div>

      {perf.error && <div className="alert error">{perf.error}</div>}
      {perf.loading && <p className="muted">Loading…</p>}
      {perf.data && (perf.data.subjects || []).length === 0 && (
        <div className="card empty">No graded assessments for this child yet.</div>
      )}

      <div className="grid cols-3">
        {(perf.data?.subjects || []).map((s) => {
          const cls = s.status === 'strong' ? 'green' : s.status === 'weak' ? 'red' : 'amber'
          return (
            <div key={s.subject} className="card">
              <div className="row">
                <b>{s.subject}</b>
                <span className={`badge ${cls}`}>{s.status}</span>
              </div>
              <div className="stat" style={{ textAlign: 'left' }}>
                <div className="value">{s.percentage}%</div>
              </div>
              <div
                style={{
                  height: 8,
                  borderRadius: 999,
                  background: 'var(--border)',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, s.percentage)}%`,
                    background:
                      s.percentage >= 75 ? 'var(--success)' : s.percentage >= 50 ? 'var(--warning)' : 'var(--danger)',
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h2>Achievements</h2>
        {achievements.loading && <p className="muted">Loading…</p>}
        {achievements.error && <div className="alert error">{achievements.error}</div>}
        {(achievements.data || []).length === 0 && !achievements.loading && (
          <p className="muted">No achievements yet.</p>
        )}
        <div className="grid cols-3">
          {(achievements.data || []).map((a) => (
            <div key={a.id} className="card">
              <div style={{ fontSize: 32 }}>{a.icon || '🏆'}</div>
              <b>{a.title}</b>
              <p className="muted" style={{ margin: '4px 0 0', fontSize: 13 }}>
                {a.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
