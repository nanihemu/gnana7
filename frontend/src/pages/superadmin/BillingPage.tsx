import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Subscription {
  id: number
  tenant: number
  tenant_name: string
  plan: number
  plan_name: string
  billing_cycle: string
  status: string
  starts_at: string
  ends_at: string
}

interface Transaction {
  id: number
  tenant_name: string
  kind: string
  amount: string
  currency: string
  status: string
  gateway_ref: string
  created_at: string
}

export default function BillingPage() {
  const { data, error, loading, reload } = useFetch<Subscription[]>('/subscriptions/')
  const tx = useFetch<Transaction[]>('/transactions/')
  const [form, setForm] = useState({
    tenant: '',
    plan: '',
    billing_cycle: 'monthly',
    status: 'active',
    starts_at: '',
    ends_at: '',
  })
  const create = useMutate<Subscription>('/subscriptions/')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const payload = {
      tenant: form.tenant ? num(form.tenant) : undefined,
      plan: form.plan ? num(form.plan) : undefined,
      billing_cycle: form.billing_cycle,
      status: form.status,
      starts_at: form.starts_at,
      ends_at: form.ends_at,
    }
    const done = async () => {
      const ok = await create.run(payload)
      if (ok) {
        setForm({ tenant: '', plan: '', billing_cycle: 'monthly', status: 'active', starts_at: '', ends_at: '' })
        reload()
        tx.reload()
      }
    }
    void done()
  }

  function num(v: string): number {
    const n = parseInt(v, 10)
    return Number.isFinite(n) ? n : 0
  }

  if (loading || tx.loading) return <p className="muted">Loading billing…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Billing</h1>

      <form className="card form" style={{ maxWidth: 560 }} onSubmit={submit}>
        <h3>New subscription</h3>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Tenant ID</label>
            <input value={form.tenant} onChange={(e) => setForm({ ...form, tenant: e.target.value })} placeholder="1" required />
          </div>
          <div style={{ flex: 1 }}>
            <label>Plan ID</label>
            <input value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })} placeholder="1" required />
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Cycle</label>
            <select value={form.billing_cycle} onChange={(e) => setForm({ ...form, billing_cycle: e.target.value })}>
              <option value="monthly">Monthly</option>
              <option value="annual">Annual</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Status</label>
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="active">Active</option>
              <option value="trialing">Trialing</option>
              <option value="past_due">Past due</option>
              <option value="canceled">Canceled</option>
            </select>
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Starts (ISO)</label>
            <input value={form.starts_at} onChange={(e) => setForm({ ...form, starts_at: e.target.value })} placeholder="2025-01-01" />
          </div>
          <div style={{ flex: 1 }}>
            <label>Ends (ISO)</label>
            <input value={form.ends_at} onChange={(e) => setForm({ ...form, ends_at: e.target.value })} placeholder="2025-12-31" />
          </div>
        </div>
        {create.error && <div className="alert error">{create.error}</div>}
        <div className="actions">
          <button className="btn" type="submit" disabled={create.busy}>
            Create subscription
          </button>
        </div>
      </form>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Subscriptions</h3>
        {(data || []).length === 0 && <p className="empty">No subscriptions.</p>}
        <table>
          <thead>
            <tr>
              <th>School</th>
              <th>Plan</th>
              <th>Cycle</th>
              <th>Status</th>
              <th>Period</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((s) => (
              <tr key={s.id}>
                <td>{s.tenant_name}</td>
                <td>{s.plan_name}</td>
                <td>{s.billing_cycle}</td>
                <td>
                  <span className={`badge ${s.status === 'active' || s.status === 'trialing' ? 'green' : s.status === 'past_due' ? 'amber' : 'gray'}`}>
                    {s.status}
                  </span>
                </td>
                <td className="muted">
                  <small>
                    {s.starts_at?.slice(0, 10)} → {s.ends_at?.slice(0, 10)}
                  </small>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Transactions</h3>
        {(tx.data || []).length === 0 && <p className="empty">No transactions.</p>}
        <table>
          <thead>
            <tr>
              <th>School</th>
              <th>Kind</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Ref</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {(tx.data || []).map((t) => (
              <tr key={t.id}>
                <td>{t.tenant_name}</td>
                <td>{t.kind}</td>
                <td>{t.currency} {t.amount}</td>
                <td>{t.status}</td>
                <td className="muted">
                  <small>{t.gateway_ref || '—'}</small>
                </td>
                <td className="muted">
                  <small>{t.created_at?.slice(0, 10)}</small>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
