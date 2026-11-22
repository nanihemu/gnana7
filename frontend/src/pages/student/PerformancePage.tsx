import { useAuth } from '../../auth'
import { useFetch } from '../../hooks'

interface Perf {
  student_id: number
  subjects: { subject: string; percentage: number; status: string }[]
}
interface SummaryResp {
  student_id: number
  summary: string
}

function StatusBadge({ status }: { status: string }) {
  const cls = status === 'strong' ? 'green' : status === 'weak' ? 'red' : 'amber'
  return <span className={`badge ${cls}`}>{status}</span>
}

export default function PerformancePage() {
  const { user } = useAuth()
  const perf = useFetch<Perf>(
    user ? `/performance/${user.id}/` : null,
    [user?.id],
  )
  const summary = useFetch<SummaryResp>(
    user ? `/performance/${user.id}/summary/` : null,
    [user?.id],
  )

  return (
    <div>
      <h1>My Performance</h1>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>AI Progress Summary</h2>
        {summary.loading && <p className="muted">Generating summary…</p>}
        {summary.error && <div className="alert error">{summary.error}</div>}
        {summary.data && (
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, margin: 0 }}>{summary.data.summary}</p>
        )}
      </div>

      {perf.error && <div className="alert error">{perf.error}</div>}
      {perf.loading && <p className="muted">Loading…</p>}
      {perf.data && (perf.data.subjects || []).length === 0 && (
        <div className="card empty">
          No performance data yet — once you have graded assessments, subject-wise progress appears
          here.
        </div>
      )}

      <div className="grid cols-3">
        {(perf.data?.subjects || []).map((s) => (
          <div key={s.subject} className="card">
            <div className="row">
              <b>{s.subject}</b>
              <StatusBadge status={s.status} />
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
                  background: s.percentage >= 75 ? 'var(--success)' : s.percentage >= 50 ? 'var(--warning)' : 'var(--danger)',
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
