import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Subject {
  id: number
  name: string
  code: string
}

export default function SubjectsPage() {
  const { data, loading, error, reload } = useFetch<Subject[]>('/subjects/')
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const create = useMutate<Subject>('/subjects/')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({ name, code })
      if (ok) {
        setName('')
        setCode('')
        reload()
      }
    }
    void done()
  }

  if (loading) return <p className="muted">Loading subjects…</p>
  if (error) return <div className="alert error">{error}</div>

  return (
    <div>
      <h1>Subjects</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Add subject</h3>
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Science" required />
          <label>Code</label>
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="SCI" />
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Add subject
            </button>
          </div>
        </form>
        <div className="card">
          <h3>Subjects</h3>
          {(data || []).length === 0 && <p className="empty">No subjects yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Code</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>
                    <span className="badge gray">{s.code}</span>
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
