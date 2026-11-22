import { useState } from 'react'
import { useFetch, useMutate } from '../../hooks'
import { User } from '../../api'

interface Enrollment {
  id: number
  student: number
  student_name: string
  school_class: number
  admission_number: string
  guardian: number | null
}

export default function EnrollmentsPage() {
  const enr = useFetch<Enrollment[]>('/enrollments/')
  const users = useFetch<User[]>('/users/')
  const classes = useFetch<{ id: number; name: string; section: string }[]>('/classes/')

  const [student, setStudent] = useState('')
  const [schoolClass, setSchoolClass] = useState('')
  const [admission, setAdmission] = useState('')
  const [guardian, setGuardian] = useState('')
  const create = useMutate<Enrollment>('/enrollments/')

  const students = (users.data || []).filter((u) => u.role === 'student')
  const parents = (users.data || []).filter((u) => u.role === 'parent')

  function submit(e: React.FormEvent) {
    e.preventDefault()
    const payload: Record<string, unknown> = {
      student: parseInt(student, 10),
      school_class: parseInt(schoolClass, 10),
    }
    if (admission.trim()) payload.admission_number = admission.trim()
    if (guardian) payload.guardian = parseInt(guardian, 10)
    const done = async () => {
      const ok = await create.run(payload)
      if (ok) {
        setStudent('')
        setSchoolClass('')
        setAdmission('')
        setGuardian('')
        enr.reload()
      }
    }
    void done()
  }

  if (enr.loading || users.loading || classes.loading) return <p className="muted">Loading…</p>

  return (
    <div>
      <h1>Enrollments</h1>
      <div className="grid cols-2">
        <form className="card form" onSubmit={submit}>
          <h3>Enroll a student</h3>
          <label>Student</label>
          <select value={student} onChange={(e) => setStudent(e.target.value)} required>
            <option value="">Select student…</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.full_name || s.username}
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
          <label>Admission number</label>
          <input value={admission} onChange={(e) => setAdmission(e.target.value)} placeholder="ADM-1001" />
          <label>Guardian (parent)</label>
          <select value={guardian} onChange={(e) => setGuardian(e.target.value)}>
            <option value="">None</option>
            {parents.map((p) => (
              <option key={p.id} value={p.id}>
                {p.full_name || p.username}
              </option>
            ))}
          </select>
          {create.error && <div className="alert error">{create.error}</div>}
          <div className="actions">
            <button className="btn" type="submit" disabled={create.busy}>
              Enroll
            </button>
          </div>
        </form>

        <div className="card">
          <h3>Enrollments</h3>
          {(enr.data || []).length === 0 && <p className="empty">No enrollments yet.</p>}
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Class</th>
                <th>Admission</th>
                <th>Guardian</th>
              </tr>
            </thead>
            <tbody>
              {(enr.data || []).map((e) => {
                const p = parents.find((x) => x.id === e.guardian)
                const c = (classes.data || []).find((x) => x.id === e.school_class)
                return (
                  <tr key={e.id}>
                    <td>{e.student_name}</td>
                    <td>
                      {c ? `${c.name} ${c.section}` : `#${e.school_class}`}
                    </td>
                    <td>{e.admission_number || '—'}</td>
                    <td>{p ? p.full_name || p.username : '—'}</td>
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
