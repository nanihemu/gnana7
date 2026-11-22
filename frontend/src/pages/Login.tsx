import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { errMsg } from '../api'

const DEMO = [
  { role: 'Super Admin', user: 'superadmin', pass: 'changeme123' },
  { role: 'School Admin', user: 'admin', pass: 'demo12345' },
  { role: 'Teacher', user: 'teacher', pass: 'demo12345' },
  { role: 'Student', user: 'student', pass: 'demo12345' },
  { role: 'Parent', user: 'parent', pass: 'demo12345' },
]

export default function Login() {
  const { user, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(username.trim(), password)
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setBusy(false)
    }
  }

  function fill(u: string, p: string) {
    setUsername(u)
    setPassword(p)
    setError('')
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={submit}>
        <h1>Gnana SMS</h1>
        <p className="sub">School management with AI tutoring</p>

        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          placeholder="e.g. student"
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          placeholder="••••••••"
        />

        {error && <div className="alert error">{error}</div>}

        <div className="actions">
          <button className="btn" type="submit" disabled={busy || !username || !password}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </div>

        <div className="demo">
          <strong>Demo logins</strong> (from <code>seed_demo</code>):
          {DEMO.map((d) => (
            <div key={d.user}>
              <button type="button" className="btn sm secondary" onClick={() => fill(d.user, d.pass)}>
                {d.role}
              </button>{' '}
              <span className="muted">
                {d.user} / {d.pass}
              </span>
            </div>
          ))}
        </div>
      </form>
    </div>
  )
}
