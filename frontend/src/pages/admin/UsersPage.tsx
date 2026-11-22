import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'
import { User, ROLE_LABELS } from '../../api'

export default function UsersPage() {
  const { data, loading, error, reload } = useFetch<User[]>('/users/')
  const create = useMutate<User>('/users/provision/')
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'student',
    phone: '',
  })

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({ ...form })
      if (ok) {
        setForm({ username: '', email: '', password: '', full_name: '', role: 'student', phone: '' })
        reload()
      }
    }
    void done()
  }

  // Keep role list sorted with interesting roles first.
  const ROLE_ORDER = ['student', 'teacher', 'parent', 'admin']

  if (loading) return <p className="muted">Loading users…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Users</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Provision user</h3>
          <label>Full name</label>
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
          <label>Username</label>
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          <label>Email</label>
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <label>Password</label>
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} minLength={6} required />
          <label>Role</label>
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            {ROLE_ORDER.map((r) => (
              <option key={r} value={r}>
                {ROLE_LABELS[r] || r}
              </option>
            ))}
          </select>
          <label>Phone</label>
          <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+91 …" />
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Create user
            </button>
          </div>
        </form>

        <div className="card">
          <h3>Users</h3>
          {(data || []).length === 0 && <p className="empty">No users yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Role</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((u) => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td>{u.username}</td>
                  <td>
                    <span className="badge">{ROLE_LABELS[u.role] || u.role}</span>
                  </td>
                  <td className="muted">{u.email || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
