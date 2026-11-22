import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Plan {
  id: number
  name: string
  code: string
  monthly_price: string
  annual_price: string
  max_students: number
  max_teachers: number
  max_storage_gb: number
  ai_features: boolean
  is_active: boolean
}

const BLANK: Omit<Plan, 'id'> = {
  name: '',
  code: '',
  monthly_price: '0',
  annual_price: '0',
  max_students: 0,
  max_teachers: 0,
  max_storage_gb: 0,
  ai_features: true,
  is_active: true,
}

export default function PlansPage() {
  const { data, loading, error, reload } = useFetch<Plan[]>('/plans/')
  const [editing, setEditing] = useState<Partial<Plan>>({ ...BLANK })
  const create = useMutate<Plan>('/plans/')
  const patch = useMutate<Plan>('/plans/', 'patch')

  function num(v: string, fallback = 0): number {
    const n = parseFloat(v)
    return Number.isFinite(n) ? n : fallback
  }

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const payload = {
      ...editing,
      monthly_price: String(editing.monthly_price || 0),
      annual_price: String(editing.annual_price || 0),
      max_students: num(String(editing.max_students)),
      max_teachers: num(String(editing.max_teachers)),
      max_storage_gb: num(String(editing.max_storage_gb)),
      ai_features: Boolean(editing.ai_features),
      is_active: editing.is_active ?? true,
    }
    const done = async () => {
      const ok = editing.id ? await patch.run(payload, {}) : await create.run(payload)
      if (ok) {
        setEditing({ ...BLANK })
        reload()
      }
    }
    void done()
  }

  if (loading) return <p className="muted">Loading plans…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Subscription Plans</h1>
      <div className="grid cols-2">
        <div>
          <form className="card form" onSubmit={submit}>
            <h3>{editing.id ? 'Update plan' : 'Create plan'}</h3>
            <label>Name</label>
            <input value={editing.name || ''} onChange={(e) => setEditing({ ...editing, name: e.target.value })} required />
            <label>Code</label>
            <input value={editing.code || ''} onChange={(e) => setEditing({ ...editing, code: e.target.value })} required />
            <label>Monthly price (₹)</label>
            <input value={editing.monthly_price || ''} onChange={(e) => setEditing({ ...editing, monthly_price: e.target.value })} />
            <label>Annual price (₹)</label>
            <input value={editing.annual_price || ''} onChange={(e) => setEditing({ ...editing, annual_price: e.target.value })} />
            <div className="row">
              <div style={{ flex: 1 }}>
                <label>Max students</label>
                <input value={editing.max_students ?? ''} onChange={(e) => setEditing({ ...editing, max_students: num(e.target.value) })} />
              </div>
              <div style={{ flex: 1 }}>
                <label>Max teachers</label>
                <input value={editing.max_teachers ?? ''} onChange={(e) => setEditing({ ...editing, max_teachers: num(e.target.value) })} />
              </div>
            </div>
            <label>Storage (GB)</label>
            <input value={editing.max_storage_gb ?? ''} onChange={(e) => setEditing({ ...editing, max_storage_gb: num(e.target.value) })} />
            <div className="row" style={{ marginTop: 12 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0 }}>
                <input
                  type="checkbox"
                  style={{ width: 'auto' }}
                  checked={Boolean(editing.ai_features)}
                  onChange={(e) => setEditing({ ...editing, ai_features: e.target.checked })}
                />
                AI features
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, margin: 0 }}>
                <input
                  type="checkbox"
                  style={{ width: 'auto' }}
                  checked={editing.is_active ?? true}
                  onChange={(e) => setEditing({ ...editing, is_active: e.target.checked })}
                />
                Active
              </label>
            </div>
            {(create.error || patch.error) && <div className="alert error">{create.error || patch.error}</div>}
            <div className="actions">
              <button className="btn" type="submit" disabled={create.busy || patch.busy}>
                {editing.id ? 'Save' : 'Create'}
              </button>
              {editing.id && (
                <button className="btn secondary" type="button" onClick={() => setEditing({ ...BLANK })}>
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="card">
          <h3>Plans</h3>
          {(data || []).length === 0 && <p className="empty">No plans yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Plan</th>
                <th>₹/mo</th>
                <th>₹/yr</th>
                <th>Limits</th>
                <th>AI</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((p) => (
                <tr key={p.id}>
                  <td>
                    <b>{p.name}</b>
                    <div className="muted">
                      <small>{p.code}</small>
                    </div>
                  </td>
                  <td>{p.monthly_price}</td>
                  <td>{p.annual_price}</td>
                  <td>
                    <small>
                      {p.max_students} students · {p.max_teachers} teachers · {p.max_storage_gb} GB
                    </small>
                  </td>
                  <td>{p.ai_features ? <span className="badge">AI</span> : '—'}</td>
                  <td>
                    <button className="btn sm secondary" onClick={() => setEditing({ ...p })}>
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
