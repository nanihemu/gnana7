import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'

interface Remark {
  id: number
  teacher: number
  teacher_name: string
  student: number
  subject: number
  subject_name: string
  content: string
  created_at: string
}

export default function RemarksPage() {
  const list = useFetch<Remark[]>('/remarks/')
  const users = useFetch<{ id: number; full_name: string; role: string }[]>('/users/')
  const subjects = useFetch<{ id: number; name: string }[]>('/subjects/')
  const create = useMutate<Remark>('/remarks/')

  const [student, setStudent] = useState('')
  const [subject, setSubject] = useState('')
  const [content, setContent] = useState('')

  const students = (users.data || []).filter((u) => u.role === 'student')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({
        student: parseInt(student, 10),
        subject: parseInt(subject, 10),
        content,
      })
      if (ok) {
        setStudent('')
        setSubject('')
        setContent('')
        list.reload()
      }
    }
    void done()
  }

  if (list.loading || users.loading || subjects.loading) return <p className="muted">Loading…</p>

  return (
    <div>
      <h1>Remarks</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Add remark</h3>
          <label>Student</label>
          <select value={student} onChange={(e) => setStudent(e.target.value)} required>
            <option value="">Select…</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.full_name}
              </option>
            ))}
          </select>
          <label>Subject</label>
          <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
            <option value="">Select…</option>
            {(subjects.data || []).map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <label>Content</label>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={3} required />
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Add remark
            </button>
          </div>
        </form>

        <div className="card">
          <h3>Remarks</h3>
          {(list.data || []).length === 0 && <p className="empty">No remarks yet.</p>}
          {(list.data || []).map((r) => (
            <div key={r.id} style={{ marginBottom: 14 }}>
              <div className="row">
                <b>{r.teacher_name}</b>
                <span className="badge gray">{r.subject_name}</span>
                <span className="muted" style={{ marginLeft: 'auto' }}>
                  <small>{new Date(r.created_at).toLocaleDateString()}</small>
                </span>
              </div>
              <p className="muted" style={{ margin: '4px 0 0' }}>
                {r.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
