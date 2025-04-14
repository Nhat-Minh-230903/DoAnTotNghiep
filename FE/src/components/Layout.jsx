import React from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { FaSignOutAlt, FaUser, FaBook, FaChartBar, FaUsers, FaFileImport, FaKey } from 'react-icons/fa'
import { ROUTES } from '../config/constants'

const Layout = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-sidebar-color border-r border-border-color p-4">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-primary-color">Đánh giá môn học</h1>
        </div>
        
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-2">
            <FaUser />
            <span>{user.name}</span>
          </div>
          <div className="text-sm text-gray-600">{user.email}</div>
          <div className="mt-2">
            <span className="badge badge-primary">{
              user.role === 'student' ? 'Sinh viên' :
              user.role === 'instructor' ? 'Giảng viên' : 'Quản trị viên'
            }</span>
          </div>
        </div>
        
        <nav className="mb-6">
          <ul>
            {/* Student navigation */}
            {user.role === 'student' && (
              <li className="mb-2">
                <NavLink 
                  to={ROUTES.STUDENT.DASHBOARD} 
                  className={({ isActive }) => 
                    `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                  }
                >
                  <FaBook />
                  <span>Danh sách môn học</span>
                </NavLink>
              </li>
            )}
            
            {/* Instructor navigation */}
            {user.role === 'instructor' && (
              <li className="mb-2">
                <NavLink 
                  to={ROUTES.INSTRUCTOR.DASHBOARD} 
                  className={({ isActive }) => 
                    `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                  }
                  end
                >
                  <FaBook />
                  <span>Môn học của tôi</span>
                </NavLink>
              </li>
            )}
            
            {/* Admin navigation */}
            {user.role === 'admin' && (
              <>
                <li className="mb-2">
                  <NavLink 
                    to={ROUTES.ADMIN.DASHBOARD} 
                    className={({ isActive }) => 
                      `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                    }
                  >
                    <FaChartBar />
                    <span>Tổng quan</span>
                  </NavLink>
                </li>
                <li className="mb-2">
                  <NavLink 
                    to={ROUTES.ADMIN.COURSE_MANAGEMENT} 
                    className={({ isActive }) => 
                      `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                    }
                  >
                    <FaBook />
                    <span>Quản lý môn học</span>
                  </NavLink>
                </li>
                <li className="mb-2">
                  <NavLink 
                    to={ROUTES.ADMIN.USER_MANAGEMENT} 
                    className={({ isActive }) => 
                      `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                    }
                  >
                    <FaUsers />
                    <span>Quản lý người dùng</span>
                  </NavLink>
                </li>
                <li className="mb-2">
                  <NavLink 
                    to={ROUTES.ADMIN.REPORTS} 
                    className={({ isActive }) => 
                      `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                    }
                  >
                    <FaChartBar />
                    <span>Báo cáo thống kê</span>
                  </NavLink>
                </li>
                <li className="mb-2">
                  <NavLink 
                    to={ROUTES.ADMIN.IMPORT_STUDENTS} 
                    className={({ isActive }) => 
                      `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                    }
                  >
                    <FaFileImport />
                    <span>Nhập sinh viên</span>
                  </NavLink>
                </li>
              </>
            )}
            
            {/* Common navigation for all users */}
            <li className="mb-2">
              <NavLink 
                to={ROUTES.CHANGE_PASSWORD} 
                className={({ isActive }) => 
                  `flex items-center gap-2 p-2 rounded ${isActive ? 'bg-primary-color text-white' : 'hover:bg-gray-200'}`
                }
              >
                <FaKey />
                <span>Đổi mật khẩu</span>
              </NavLink>
            </li>
          </ul>
        </nav>
        
        <div className="mt-auto">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 p-2 w-full text-left rounded hover:bg-gray-200"
          >
            <FaSignOutAlt />
            <span>Đăng xuất</span>
          </button>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 p-6">
        <Outlet />
      </div>
    </div>
  )
}

export default Layout
