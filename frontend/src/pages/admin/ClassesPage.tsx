import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface SchoolClass {
  id: number
  name: string
  section: string
  created_at: string
}

export default function ClassesPage() {
  const { data, loading, error, reload } = useFetch<SchoolClass[]>('/classes/')
  const [name, setName] = useState('')
  const [section, setSection] = useState('')
  const create = useMutate<SchoolClass>('/classes/')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({ name, section })
      if (ok) {
        setName('')
        setSection('')
        reload()
      }
    }
    void done()
  }

  if (loading) return <p className="muted">Loading classes…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Classes</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Add class</h3>
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Grade 6" required />
          <label>Section</label>
          <input value={section} onChange={(e) => setSection(e.target.value)} placeholder="A" />
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Add class
            </button>
          </div>
        </form>
        <div className="card">
          <h3>Classes</h3>
          {(data || []).length === 0 && <p className="empty">No classes yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Section</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.section || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
