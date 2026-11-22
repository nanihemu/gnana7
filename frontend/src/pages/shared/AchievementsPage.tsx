import { useEffect, useState } from 'react'
import { useAuth } from '../../auth'
import { api, errMsg, useFetch, useMutate } from '../../hooks'

interface Achievement {
  id: number
  title: string
  description: string
  icon: string
  awarded_to: number
  student_name: string
  created_at: string
}

export default function AchievementsPage() {
  const { user } = useAuth()
  const role = user?.role
  const canAward = role === 'admin' || role === 'teacher'

  // Parents need to pick a child; the rest just load their own list.
  const children = useFetch<{ id: number; full_name: string; username: string }[]>('/me/children/')
  const [childId, setChildId] = useState<string>('')

  const listUrl = canAward
    ? '/achievements/'
    : role === 'parent'
      ? childId
        ? `/achievements/student/${childId}/`
        : null
      : '/me/achievements/'

  const parentNoChild = role === 'parent' && !childId
  const list = useFetch<Achievement[]>(parentNoChild ? null : (listUrl || '/me/achievements/'), [
    childId,
  ])
  useEffect(() => {
    const kids = children.data
    if (role === 'parent' && kids && kids.length > 0) {
      setChildId((cur) => cur || String(kids[0].id))
    }
  }, [children.data, role])

  const award = useMutate<Achievement>('/achievements/award/')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [icon, setIcon] = useState('🏆')
  const [to, setTo] = useState('')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await award.run({
        title,
        description,
        icon,
        awarded_to: parseInt(to, 10),
      })
      if (ok) {
        setTitle('')
        setDescription('')
        setIcon('🏆')
        setTo('')
        list.reload()
      }
    }
    void done()
  }

  return (
    <div>
      <h1>Achievements</h1>

      {role === 'parent' && (
        <div className="card" style={{ maxWidth: 420, marginBottom: 16 }}>
          <label>Child</label>
          {children.loading && <p className="muted">Loading children…</p>}
          <select
            value={childId}
            onChange={(e) => setChildId(e.target.value)}
            disabled={!children.data || children.data.length === 0}
          >
            {(children.data || []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.full_name || c.username}
              </option>
            ))}
          </select>
        </div>
      )}

      {canAward && (
        <form className="card form" style={{ maxWidth: 560 }} onSubmit={submit}>
          <h3>Award an achievement</h3>
          <label>Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Science Star" required />
          <label>Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} required />
          <label>Icon</label>
          <input value={icon} onChange={(e) => setIcon(e.target.value)} maxLength={4} />
          <label>Student ID</label>
          <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="3" required />
          {award.error && <div className="alert error">{award.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={award.busy}>
              Award
            </button>
          </div>
        </form>
      )}

      {list.error && <div className="alert error">{list.error}</div>}

      <div className="grid cols-3" style={{ marginTop: 20 }}>
        {list.loading && <p className="muted">Loading…</p>}
        {(list.data || []).length === 0 && !list.loading && (
          <div className="card empty">No achievements yet.</div>
        )}
        {(list.data || []).map((a) => (
          <div key={a.id} className="card">
            <div style={{ fontSize: 32 }}>{a.icon || '🏆'}</div>
            <h3 style={{ margin: '8px 0 4px' }}>{a.title}</h3>
            <p className="muted" style={{ margin: 0 }}>
              {a.description}
            </p>
            <small className="muted">
              {a.student_name || `Student #${a.awarded_to}`} · {new Date(a.created_at).toLocaleDateString()}
            </small>
          </div>
        ))}
      </div>
    </div>
  )
}
