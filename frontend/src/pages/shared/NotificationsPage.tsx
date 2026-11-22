import { useState } from 'react'
import { useAuth } from '../../auth'
import { api, errMsg, useFetch, useMutate } from '../../hooks'

interface Notification {
  id: number
  title: string
  body: string
  audience: string
  is_read: boolean
  created_at: string
}

const AUDIENCE_LABELS: Record<string, string> = {
  all: 'Everyone',
  admin: 'Admins',
  teachers: 'Teachers',
  students: 'Students',
  parents: 'Parents',
}

export default function NotificationsPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const list = useFetch<Notification[]>('/me/notifications/')
  const mark = useMutate<Notification>('/me/notifications/mark-read/', 'post')
  const create = useMutate<Notification>('/notifications/')

  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [audience, setAudience] = useState('all')

  function post(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({ title, body, audience })
      if (ok) {
        setTitle('')
        setBody('')
        setAudience('all')
        list.reload()
      }
    }
    void done()
  }

  async function markRead(n: Notification) {
    if (n.is_read) return
    try {
      await api.post(`/me/notifications/mark-read/${n.id}/`)
      list.reload()
    } catch (e) {
      mark.setError(errMsg(e))
    }
  }

  return (
    <div>
      <h1>Notifications</h1>

      {isAdmin && (
        <form className="card form" style={{ maxWidth: 560 }} onSubmit={post}>
          <h3>Post a notification</h3>
          <label>Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Parents' meeting on Friday" required />
          <label>Body</label>
          <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={3} required />
          <label>Audience</label>
          <select value={audience} onChange={(e) => setAudience(e.target.value)}>
            {Object.entries(AUDIENCE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Post
            </button>
          </div>
        </form>
      )}

      {list.error && <div className="alert error">{list.error}</div>}

      <div className="stack" style={{ marginTop: 20 }}>
        {list.loading && <p className="muted">Loading…</p>}
        {(list.data || []).length === 0 && !list.loading && (
          <div className="card empty">No notifications yet.</div>
        )}
        {(list.data || []).map((n) => (
          <div
            key={n.id}
            className="card"
            onClick={() => void markRead(n)}
            style={{ cursor: n.is_read ? 'default' : 'pointer', opacity: n.is_read ? 0.75 : 1 }}
          >
            <div className="row" style={{ marginBottom: 4 }}>
              <b>{n.title}</b>
              <span className="badge gray" style={{ marginLeft: 'auto' }}>
                {AUDIENCE_LABELS[n.audience] || n.audience}
              </span>
              {!n.is_read && <span className="badge">New</span>}
            </div>
            <p className="muted" style={{ margin: '0 0 6px' }}>
              {n.body}
            </p>
            <small className="muted">{new Date(n.created_at).toLocaleString()}</small>
          </div>
        ))}
        {mark.error && <div className="alert error">{mark.error}</div>}
      </div>
    </div>
  )
}
