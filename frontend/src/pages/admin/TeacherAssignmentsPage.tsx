import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'
import { User } from '../../api'

interface Assignment {
  id: number
  teacher: number
  teacher_name: string
  subject: number
  school_class: number
}

export default function TeacherAssignmentsPage() {
  const asg = useFetch<Assignment[]>('/teacher-assignments/')
  const users = useFetch<User[]>('/users/')
  const subjects = useFetch<{ id: number; name: string }[]>('/subjects/')
  const classes = useFetch<{ id: number; name: string; section: string }[]>('/classes/')

  const [teacher, setTeacher] = useState('')
  const [subject, setSubject] = useState('')
  const [schoolClass, setSchoolClass] = useState('')
  const create = useMutate<Assignment>('/teacher-assignments/')

  const teachers = (users.data || []).filter((u) => u.role === 'teacher')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({
        teacher: parseInt(teacher, 10),
        subject: parseInt(subject, 10),
        school_class: parseInt(schoolClass, 10),
      })
      if (ok) {
        setTeacher('')
        setSubject('')
        setSchoolClass('')
        asg.reload()
      }
    }
    void done()
  }

  if (asg.loading || users.loading || subjects.loading || classes.loading)
    return <p className="muted">Loading…</p>

  return (
    <div>
      <h1>Teacher Assignment</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Assign teacher</h3>
          <label>Teacher</label>
          <select value={teacher} onChange={(e) => setTeacher(e.target.value)} required>
            <option value="">Select teacher…</option>
            {teachers.map((t) => (
              <option key={t.id} value={t.id}>
                {t.full_name || t.username}
              </option>
            ))}
          </select>
          <label>Subject</label>
          <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
            <option value="">Select subject…</option>
            {(subjects.data || []).map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <label>Class</label>
          <select value={schoolClass} onChange={(e) => setSchoolClass(e.target.value)} required>
            <option value="">Select class…</option>
            {(classes.data || []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} {c.section}
              </option>
            ))}
          </select>
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Assign
            </button>
          </div>
        </form>

        <div className="card">
          <h3>Assignments</h3>
          {(asg.data || []).length === 0 && <p className="empty">No assignments yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Teacher</th>
                <th>Subject</th>
                <th>Class</th>
              </tr>
            </thead>
            <tbody>
              {(asg.data || []).map((a) => {
                const s = (subjects.data || []).find((x) => x.id === a.subject)
                const c = (classes.data || []).find((x) => x.id === a.school_class)
                return (
                  <tr key={a.id}>
                    <td>{a.teacher_name}</td>
                    <td>{s ? s.name : `#${a.subject}`}</td>
                    <td>{c ? `${c.name} ${c.section}` : `#${a.school_class}`}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
