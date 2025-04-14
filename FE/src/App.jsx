import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import './index.css'

// Contexts
import { AuthProvider, useAuth } from './contexts/AuthContext'

// Components
import Layout from './components/Layout'

// Pages
import Login from './pages/Login'
import ChangePassword from './pages/ChangePassword'
import NotFound from './pages/NotFound'

// Student Pages
import StudentDashboard from './pages/student/Dashboard'
import CourseEvaluation from './pages/student/CourseEvaluation'

// Instructor Pages
import InstructorDashboard from './pages/instructor/Dashboard'
import CourseDetails from './pages/instructor/CourseDetails'

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard'
import CourseManagement from './pages/admin/CourseManagement'
import UserManagement from './pages/admin/UserManagement'
import Reports from './pages/admin/Reports'
import ImportStudents from './pages/admin/ImportStudents'

// Routes
import { ROUTES } from './config/constants'

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }
  
  return children
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          {/* Default redirect based on role */}
          <Route index element={<RoleBasedRedirect />} />
          
          {/* Common Routes */}
          <Route path={ROUTES.CHANGE_PASSWORD} element={<ChangePassword />} />
          
          {/* Student Routes */}
          <Route path={ROUTES.STUDENT.DASHBOARD} element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          } />
          <Route path={`${ROUTES.STUDENT.COURSE_EVALUATION}/:courseId`} element={
            <ProtectedRoute allowedRoles={['student']}>
              <CourseEvaluation />
            </ProtectedRoute>
          } />
          
          {/* Instructor Routes */}
          <Route path={ROUTES.INSTRUCTOR.DASHBOARD} element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <InstructorDashboard />
            </ProtectedRoute>
          } />
          <Route path={`${ROUTES.INSTRUCTOR.COURSE_DETAILS}/:courseId`} element={
            <ProtectedRoute allowedRoles={['instructor']}>
              <CourseDetails />
            </ProtectedRoute>
          } />
          
          {/* Admin Routes */}
          <Route path={ROUTES.ADMIN.DASHBOARD} element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path={ROUTES.ADMIN.COURSE_MANAGEMENT} element={
            <ProtectedRoute allowedRoles={['admin']}>
              <CourseManagement />
            </ProtectedRoute>
          } />
          <Route path={ROUTES.ADMIN.USER_MANAGEMENT} element={
            <ProtectedRoute allowedRoles={['admin']}>
              <UserManagement />
            </ProtectedRoute>
          } />
          <Route path={ROUTES.ADMIN.REPORTS} element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Reports />
            </ProtectedRoute>
          } />
          <Route path={ROUTES.ADMIN.IMPORT_STUDENTS} element={
            <ProtectedRoute allowedRoles={['admin']}>
              <ImportStudents />
            </ProtectedRoute>
          } />
          
          {/* 404 Route */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </Router>
  )
}

// Component to redirect based on user role
const RoleBasedRedirect = () => {
  const { user } = useAuth()
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  switch (user.role) {
    case 'admin':
      return <Navigate to={ROUTES.ADMIN.DASHBOARD} replace />
    case 'instructor':
      return <Navigate to={ROUTES.INSTRUCTOR.DASHBOARD} replace />
    case 'student':
      return <Navigate to={ROUTES.STUDENT.DASHBOARD} replace />
    default:
      return <Navigate to="/login" replace />
  }
}

export default App
