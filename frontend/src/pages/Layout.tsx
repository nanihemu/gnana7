import { NavLink, Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth'
import { ROLE_LABELS } from '../api'
import Chatbot from '../components/Chatbot'

interface NavEntry {
  to: string
  label: string
}

const NAV: Record<string, NavEntry[]> = {
  super_admin: [
    { to: '/', label: 'Overview' },
    { to: '/tenants', label: 'Schools' },
    { to: '/plans', label: 'Plans' },
    { to: '/billing', label: 'Billing' },
    { to: '/roles', label: 'Roles' },
  ],
  admin: [
    { to: '/', label: 'Overview' },
    { to: '/classes', label: 'Classes' },
    { to: '/subjects', label: 'Subjects' },
    { to: '/enrollments', label: 'Enrollments' },
    { to: '/teacher-assignments', label: 'Teachers' },
    { to: '/users', label: 'Users' },
    { to: '/topics', label: 'Topics' },
    { to: '/assessments', label: 'Assessments' },
    { to: '/grading', label: 'Grading' },
    { to: '/notifications', label: 'Notifications' },
    { to: '/achievements', label: 'Achievements' },
  ],
  teacher: [
    { to: '/', label: 'Overview' },
    { to: '/topics', label: 'Topics & AI' },
    { to: '/assessments', label: 'Assessments' },
    { to: '/grading', label: 'Grading' },
    { to: '/remarks', label: 'Remarks' },
    { to: '/notifications', label: 'Notifications' },
    { to: '/achievements', label: 'Achievements' },
  ],
  student: [
    { to: '/', label: 'Overview' },
    { to: '/attempt', label: 'Assessments' },
    { to: '/results', label: 'Results' },
    { to: '/performance', label: 'Performance' },
    { to: '/self-study', label: 'Self-Study' },
    { to: '/notifications', label: 'Notifications' },
    { to: '/achievements', label: 'Achievements' },
  ],
  parent: [
    { to: '/', label: 'My Children' },
    { to: '/notifications', label: 'Notifications' },
    { to: '/achievements', label: 'Achievements' },
  ],
}

export default function Layout() {
  const { user, logout } = useAuth()
  if (!user) return <Navigate to="/login" replace />

  const nav = NAV[user.role] || []

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          Gnana<span> SMS</span>
        </div>
        {nav.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.to === '/'}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            {n.label}
          </NavLink>
        ))}
        <div className="spacer" />
        <div className="user-chip">
          <b>{user.full_name || user.username}</b>
          <small>{ROLE_LABELS[user.role] || user.role}</small>
          <div style={{ marginTop: 8 }}>
            <button className="btn sm danger" onClick={logout}>
              Sign out
            </button>
          </div>
        </div>
      </aside>

      <main className="main">
        <Outlet />
      </main>

      {user.role !== 'super_admin' && <Chatbot />}
    </div>
  )
}
