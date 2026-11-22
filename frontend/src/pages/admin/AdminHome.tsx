import { useFetch } from '../../hooks'
import { User } from '../../api'

export default function AdminHome() {
  const users = useFetch<User[]>('/users/')
  const classes = useFetch<{ id: number; name: string }[]>('/classes/')
  const enrollments = useFetch<{ id: number }[]>('/enrollments/')

  if (users.loading || classes.loading || enrollments.loading)
    return <p className="muted">Loading…</p>

  const userList = users.data || []
  const teachers = userList.filter((u) => u.role === 'teacher').length
  const students = userList.filter((u) => u.role === 'student').length
  const parents = userList.filter((u) => u.role === 'parent').length

  return (
    <div>
      <h1>School Overview</h1>
      <div className="grid cols-3">
        <div className="card stat">
          <div className="label">Students</div>
          <div className="value">{students}</div>
        </div>
        <div className="card stat">
          <div className="label">Teachers</div>
          <div className="value">{teachers}</div>
        </div>
        <div className="card stat">
          <div className="label">Parents</div>
          <div className="value">{parents}</div>
        </div>
        <div className="card stat">
          <div className="label">Classes</div>
          <div className="value">{(classes.data || []).length}</div>
        </div>
        <div className="card stat">
          <div className="label">Enrollments</div>
          <div className="value">{(enrollments.data || []).length}</div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h2>Quick guide</h2>
        <ul className="muted">
          <li>Structure: set up <b>classes</b>, <b>subjects</b>, <b>teacher assignments</b> and <b>enrollments</b>.</li>
          <li>Create <b>users</b> (students, teachers, parents) from the Users page.</li>
          <li>Post <b>notifications</b> and award <b>achievements</b> to keep the school engaged.</li>
        </ul>
      </div>
    </div>
  )
}
