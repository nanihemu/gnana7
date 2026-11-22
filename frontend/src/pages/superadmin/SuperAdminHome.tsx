import { useFetch } from '../../hooks'

interface Stats {
  tenants_total: number
  tenants_active: number
  users_total: number
  active_subscriptions: number
  mrr_inr: string
  arr_inr: string
}

export default function SuperAdminHome() {
  const { data, error, loading } = useFetch<Stats>('/platform/stats/')

  if (loading) return <p className="muted">Loading platform stats…</p>
  if (error) return <div className="alert error">{error}</div>
  if (!data) return null

  return (
    <div>
      <h1>Platform Overview</h1>
      <div className="grid cols-3">
        <div className="card stat">
          <div className="label">Schools</div>
          <div className="value">
            {data.tenants_active}
            <span className="muted" style={{ fontSize: 14 }}>
              {' '}
              / {data.tenants_total} active
            </span>
          </div>
        </div>
        <div className="card stat">
          <div className="label">Users</div>
          <div className="value">{data.users_total}</div>
        </div>
        <div className="card stat">
          <div className="label">Active subscriptions</div>
          <div className="value">{data.active_subscriptions}</div>
        </div>
        <div className="card stat">
          <div className="label">Monthly recurring revenue</div>
          <div className="value">₹{Number(data.mrr_inr).toLocaleString()}</div>
        </div>
        <div className="card stat">
          <div className="label">Annualized</div>
          <div className="value">₹{Number(data.arr_inr).toLocaleString()}</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2>About this build</h2>
        <p className="muted">
          A multi-tenant school management system. Manage schools, plans, billing and roles from
          this dashboard; school admins run classes, subjects, enrollments and AI-powered content
          from theirs.
        </p>
      </div>
    </div>
  )
}
