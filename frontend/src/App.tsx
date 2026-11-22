import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import Layout from './pages/Layout'
import Login from './pages/Login'

// Super Admin
import SuperAdminHome from './pages/superadmin/SuperAdminHome'
import TenantsPage from './pages/superadmin/TenantsPage'
import PlansPage from './pages/superadmin/PlansPage'
import BillingPage from './pages/superadmin/BillingPage'
import RolesPage from './pages/superadmin/RolesPage'

// School Admin
import AdminHome from './pages/admin/AdminHome'
import ClassesPage from './pages/admin/ClassesPage'
import SubjectsPage from './pages/admin/SubjectsPage'
import EnrollmentsPage from './pages/admin/EnrollmentsPage'
import TeacherAssignmentsPage from './pages/admin/TeacherAssignmentsPage'
import UsersPage from './pages/admin/UsersPage'

// Teacher
import TeacherHome from './pages/teacher/TeacherHome'
import TopicsPage from './pages/teacher/TopicsPage'
import AssessmentsPage from './pages/teacher/AssessmentsPage'
import GradingPage from './pages/teacher/GradingPage'
import RemarksPage from './pages/teacher/RemarksPage'

// Student
import StudentHome from './pages/student/StudentHome'
import AssessmentsPageStudent from './pages/student/AssessmentsPage'
import ResultsPage from './pages/student/ResultsPage'
import PerformancePage from './pages/student/PerformancePage'
import SelfStudyPage from './pages/student/SelfStudyPage'

// Parent
import ParentHome from './pages/parent/ParentHome'
import ChildPage from './pages/parent/ChildPage'

// Shared
import NotificationsPage from './pages/shared/NotificationsPage'
import AchievementsPage from './pages/shared/AchievementsPage'

function roleHome(role: string): string {
  switch (role) {
    case 'student':
      return '/attempt'
    case 'parent':
      return '/'
    default:
      return '/'
  }
}

function RoleHome() {
  const { user } = useAuth()
  switch (user?.role) {
    case 'super_admin':
      return <SuperAdminHome />
    case 'admin':
      return <AdminHome />
    case 'teacher':
      return <TeacherHome />
    case 'student':
      return <StudentHome />
    case 'parent':
      return <ParentHome />
    default:
      return <Navigate to="/login" replace />
  }
}

/** Render a child only if the current user has one of the allowed roles. */
function RoleGate({ roles, children }: { roles: string[]; children: ReactNode }) {
  const { user } = useAuth()
  if (!user || !roles.includes(user.role)) return <Navigate to={roleHome(user?.role || '')} replace />
  return <>{children}</>
}

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
        <p className="muted">Loading…</p>
      </div>
    )
  }
  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    )
  }

  // Authenticated: route the right pages into the shared layout.
  return (
    <Routes>
      <Route path="/login" element={<Navigate to={roleHome(user.role)} replace />} />
      <Route element={<Layout />}>
        {/* ---- Super Admin ---- */}
        <Route
          path="/"
          element={
            <RoleGate roles={['super_admin', 'admin', 'teacher', 'student', 'parent']}>
              <RoleHome />
            </RoleGate>
          }
        />
        <Route
          path="/tenants"
          element={
            <RoleGate roles={['super_admin']}>
              <TenantsPage />
            </RoleGate>
          }
        />
        <Route
          path="/plans"
          element={
            <RoleGate roles={['super_admin']}>
              <PlansPage />
            </RoleGate>
          }
        />
        <Route
          path="/billing"
          element={
            <RoleGate roles={['super_admin']}>
              <BillingPage />
            </RoleGate>
          }
        />
        <Route
          path="/roles"
          element={
            <RoleGate roles={['super_admin']}>
              <RolesPage />
            </RoleGate>
          }
        />

        {/* ---- School Admin ---- */}
        <Route
          path="/classes"
          element={
            <RoleGate roles={['admin']}>
              <ClassesPage />
            </RoleGate>
          }
        />
        <Route
          path="/subjects"
          element={
            <RoleGate roles={['admin']}>
              <SubjectsPage />
            </RoleGate>
          }
        />
        <Route
          path="/enrollments"
          element={
            <RoleGate roles={['admin']}>
              <EnrollmentsPage />
            </RoleGate>
          }
        />
        <Route
          path="/teacher-assignments"
          element={
            <RoleGate roles={['admin']}>
              <TeacherAssignmentsPage />
            </RoleGate>
          }
        />
        <Route
          path="/users"
          element={
            <RoleGate roles={['admin']}>
              <UsersPage />
            </RoleGate>
          }
        />
        <Route
          path="/notifications"
          element={
            <RoleGate roles={['admin', 'teacher', 'student', 'parent']}>
              <NotificationsPage />
            </RoleGate>
          }
        />
        <Route
          path="/achievements"
          element={
            <RoleGate roles={['admin', 'teacher', 'student', 'parent']}>
              <AchievementsPage />
            </RoleGate>
          }
        />

        {/* ---- Teacher ---- */}
        <Route
          path="/topics"
          element={
            <RoleGate roles={['admin', 'teacher']}>
              <TopicsPage />
            </RoleGate>
          }
        />
        <Route
          path="/assessments"
          element={
            <RoleGate roles={['admin', 'teacher']}>
              <AssessmentsPage />
            </RoleGate>
          }
        />
        <Route
          path="/grading"
          element={
            <RoleGate roles={['admin', 'teacher']}>
              <GradingPage />
            </RoleGate>
          }
        />
        <Route
          path="/remarks"
          element={
            <RoleGate roles={['admin', 'teacher']}>
              <RemarksPage />
            </RoleGate>
          }
        />

        {/* ---- Student ---- */}
        <Route
          path="/attempt"
          element={
            <RoleGate roles={['student']}>
              <AssessmentsPageStudent />
            </RoleGate>
          }
        />
        <Route
          path="/results"
          element={
            <RoleGate roles={['student']}>
              <ResultsPage />
            </RoleGate>
          }
        />
        <Route
          path="/performance"
          element={
            <RoleGate roles={['student']}>
              <PerformancePage />
            </RoleGate>
          }
        />
        <Route
          path="/self-study"
          element={
            <RoleGate roles={['student']}>
              <SelfStudyPage />
            </RoleGate>
          }
        />

        {/* ---- Parent ---- */}
        <Route
          path="/child/:id"
          element={
            <RoleGate roles={['parent']}>
              <ChildPage />
            </RoleGate>
          }
        />

        <Route path="*" element={<Navigate to={roleHome(user.role)} replace />} />
      </Route>
    </Routes>
  )
}
