import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Role {
  id: number
  code: string
  name: string
  permissions: string[]
}

export default function RolesPage() {
  const { data, loading, error, reload } = useFetch<Role[]>('/roles/')
  const [editing, setEditing] = useState<Partial<Role>>({ code: '', name: '', permissions: [] })
  const [permText, setPermText] = useState('')
  const create = useMutate<Role>('/roles/')
  const patch = useMutate<Role>('/roles/', 'patch')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const perms = permText
      .split(',')
      .map((p) => p.trim())
      .filter(Boolean)
    const payload = { code: editing.code, name: editing.name, permissions: perms }
    const done = async () => {
      const ok = editing.id ? await patch.run(payload, {}) : await create.run(payload)
      if (ok) {
        setEditing({ code: '', name: '', permissions: [] })
        setPermText('')
        reload()
      }
    }
    void done()
  }

  function editRole(r: Role) {
    setEditing({ ...r })
    setPermText((r.permissions || []).join(', '))
  }

  if (loading) return <p className="muted">Loading roles…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Roles & Permissions</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>{editing.id ? 'Update role' : 'Create role'}</h3>
          <label>Code</label>
          <input value={editing.code || ''} onChange={(e) => setEditing({ ...editing, code: e.target.value })} required />
          <label>Display name</label>
          <input value={editing.name || ''} onChange={(e) => setEditing({ ...editing, name: e.target.value })} required />
          <label>Permissions (comma-separated)</label>
          <textarea
            value={permText}
            onChange={(e) => setPermText(e.target.value)}
            placeholder="class.write, enrollment.write, …"
            rows={4}
          />
          {(create.error || patch.error) && <div className="alert error">{create.error || patch.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy || patch.busy}>
              {editing.id ? 'Save' : 'Create'}
            </button>
            {editing.id && (
              <button
                className="btn secondary"
                type="button"
                onClick={() => {
                  setEditing({ code: '', name: '', permissions: [] })
                  setPermText('')
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        <div className="card">
          <h3>Roles</h3>
          {(data || []).length === 0 && <p className="empty">No roles.</p>}
          {(data || []).map((r) => (
            <div key={r.id} style={{ marginBottom: 16 }}>
              <div className="row">
                <b>{r.name}</b>
                <span className="badge gray">{r.code}</span>
                <button className="btn sm secondary" onClick={() => editRole(r)}>
                  Edit
                </button>
              </div>
              <div className="muted">
                <small>{(r.permissions || []).join(' · ') || '—'}</small>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
