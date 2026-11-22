import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Tenant {
  id: number
  name: string
  slug: string
  subdomain: string
  contact_email: string
  contact_phone: string
  address: string
  is_active: boolean
  created_at: string
}

export default function TenantsPage() {
  const { data, loading, error, reload } = useFetch<Tenant[]>('/tenants/')
  const [editing, setEditing] = useState<Partial<Tenant>>({
    name: '',
    slug: '',
    subdomain: '',
    contact_email: '',
    contact_phone: '',
    address: '',
  })
  const create = useMutate<Tenant>('/tenants/')
  const patch = useMutate<Tenant>('/tenants/', 'patch')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const payload = { ...editing }
    const done = async () => {
      const ok = editing.id ? await patch.run(payload, {}) : await create.run(payload)
      if (ok) {
        setEditing({ name: '', slug: '', subdomain: '', contact_email: '', contact_phone: '', address: '' })
        reload()
      }
    }
    void done()
  }

  if (loading) return <p className="muted">Loading schools…</p>
  if (error) return <div className="alert error">{error}</div>

  const list = data || []

  return (
    <div>
      <h1>Schools (Tenants)</h1>
      <div className="grid cols-2">
        <div>
          <form className="card form" onSubmit={submit}>
            <h3>{editing.id ? 'Update school' : 'Create school'}</h3>
            <label>Name</label>
            <input
              value={editing.name || ''}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
              required
            />
            <label>Slug</label>
            <input
              value={editing.slug || ''}
              onChange={(e) => setEditing({ ...editing, slug: e.target.value })}
              placeholder="demo"
            />
            <label>Subdomain</label>
            <input
              value={editing.subdomain || ''}
              onChange={(e) => setEditing({ ...editing, subdomain: e.target.value })}
            />
            <label>Contact email</label>
            <input
              type="email"
              value={editing.contact_email || ''}
              onChange={(e) => setEditing({ ...editing, contact_email: e.target.value })}
            />
            <label>Contact phone</label>
            <input
              value={editing.contact_phone || ''}
              onChange={(e) => setEditing({ ...editing, contact_phone: e.target.value })}
            />
            <label>Address</label>
            <textarea
              value={editing.address || ''}
              onChange={(e) => setEditing({ ...editing, address: e.target.value })}
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
                  onClick={() => setEditing({ name: '', slug: '', subdomain: '', contact_email: '', contact_phone: '', address: '' })}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="card">
          <h3>Schools</h3>
          {list.length === 0 && <p className="empty">No schools yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Status</th>
                <th>Contact</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {list.map((t) => (
                <tr key={t.id}>
                  <td>{t.name}</td>
                  <td>{t.slug}</td>
                  <td>
                    <span className={`badge ${t.is_active ? 'green' : 'gray'}`}>
                      {t.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td>{t.contact_email || '—'}</td>
                  <td>
                    <button
                      className="btn sm secondary"
                      onClick={() => setEditing({ ...t })}
                    >
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
