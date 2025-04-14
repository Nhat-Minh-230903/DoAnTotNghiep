// API URL
export const API_URL = 'http://localhost:5000/api'

// User roles
export const ROLES = {
  ADMIN: 'admin',
  INSTRUCTOR: 'instructor',
  STUDENT: 'student'
}

// Routes
export const ROUTES = {
  LOGIN: '/login',
  CHANGE_PASSWORD: '/change-password',
  
  STUDENT: {
    DASHBOARD: '/student',
    COURSE_EVALUATION: '/student/evaluate'
  },
  
  INSTRUCTOR: {
    DASHBOARD: '/instructor',
    COURSE_DETAILS: '/instructor/course'
  },
  
  ADMIN: {
    DASHBOARD: '/admin',
    COURSE_MANAGEMENT: '/admin/courses',
    USER_MANAGEMENT: '/admin/users',
    REPORTS: '/admin/reports',
    IMPORT_STUDENTS: '/admin/import-students'
  }
}

// Evaluation constants
export const MIN_RATING_WITHOUT_COMMENT = 3

// Rating categories for course evaluations
export const RATING_CATEGORIES = {
  content: 'Nội dung khóa học',
  materials: 'Tài liệu học tập',
  instructor: 'Giảng viên',
  facilities: 'Cơ sở vật chất',
  support: 'Hỗ trợ học tập'
}

// Rating labels for star ratings
export const RATING_LABELS = {
  content: 'Nội dung',
  materials: 'Tài liệu',
  instructor: 'Giảng viên',
  facilities: 'Cơ sở vật chất',
  support: 'Hỗ trợ'
}
