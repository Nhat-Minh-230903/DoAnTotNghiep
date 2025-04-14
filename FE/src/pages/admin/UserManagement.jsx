import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaEdit, FaTrash, FaPlus, FaKey } from 'react-icons/fa'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'

const UserSchema = Yup.object().shape({
  name: Yup.string().required('Vui lòng nhập họ tên'),
  email: Yup.string().email('Email không hợp lệ').required('Vui lòng nhập email'),
  role: Yup.string().required('Vui lòng chọn vai trò'),
  studentId: Yup.string().when('role', {
    is: 'student',
    then: Yup.string().required('Vui lòng nhập mã sinh viên')
  })
})

const ResetPasswordSchema = Yup.object().shape({
  newPassword: Yup.string().min(6, 'Mật khẩu phải có ít nhất 6 ký tự').required('Vui lòng nhập mật khẩu mới')
})

const UserManagement = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showResetModal, setShowResetModal] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [resetUser, setResetUser] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${API_URL}/admin/users`)
        setUsers(response.data.users)
      } catch (error) {
        toast.error('Không thể tải danh sách người dùng')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  const handleAddUser = () => {
    setEditingUser(null)
    setShowModal(true)
  }

  const handleEditUser = (user) => {
    setEditingUser(user)
    setShowModal(true)
  }

  const handleResetPassword = (user) => {
    setResetUser(user)
    setShowResetModal(true)
  }

  const handleDeleteUser = async (userId) => {
    if (!confirm('Bạn có chắc chắn muốn xóa người dùng này?')) return
    
    try {
      await axios.delete(`${API_URL}/admin/users/${userId}`)
      setUsers(users.filter(user => user.id !== userId))
      toast.success('Xóa người dùng thành công')
    } catch (error) {
      toast.error('Không thể xóa người dùng')
    }
  }

  const handleSubmitUser = async (values, { setSubmitting, resetForm }) => {
    try {
      if (editingUser) {
        // Update existing user
        const response = await axios.put(`${API_URL}/admin/users/${editingUser.id}`, values)
        setUsers(users.map(user => 
          user.id === editingUser.id ? response.data.user : user
        ))
        toast.success('Cập nhật người dùng thành công')
      } else {
        // Create new user
        const response = await axios.post(`${API_URL}/admin/users`, values)
        setUsers([...users, response.data.user])
        toast.success('Thêm người dùng thành công')
      }
      
      setShowModal(false)
      resetForm()
    } catch (error) {
      toast.error(error.response?.data?.message || 'Có lỗi xảy ra')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSubmitReset = async (values, { setSubmitting }) => {
    try {
      await axios.post(`${API_URL}/admin/users/${resetUser.id}/reset-password`, {
        newPassword: values.newPassword
      })
      
      toast.success('Đặt lại mật khẩu thành công')
      setShowResetModal(false)
    } catch (error) {
      toast.error('Không thể đặt lại mật khẩu')
    } finally {
      setSubmitting(false)
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesRole = roleFilter === 'all' || user.role === roleFilter
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (user.studentId && user.studentId.toLowerCase().includes(searchTerm.toLowerCase()))
    
    return matchesRole && matchesSearch
  })

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Quản lý người dùng</h1>
        <button 
          onClick={handleAddUser}
          className="btn btn-primary flex items-center"
        >
          <FaPlus className="mr-2" />
          Thêm người dùng
        </button>
      </div>
      
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="form-group mb-0 flex-1">
          <input
            type="text"
            className="form-control"
            placeholder="Tìm kiếm theo tên, email hoặc mã sinh viên"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="form-group mb-0 md:w-64">
          <select
            className="form-control"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">Tất cả vai trò</option>
            <option value="admin">Quản trị viên</option>
            <option value="instructor">Giảng viên</option>
            <option value="student">Sinh viên</option>
          </select>
        </div>
      </div>
      
      {filteredUsers.length === 0 ? (
        <div className="card text-center p-6">
          <p>Không tìm thấy người dùng nào.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Họ tên</th>
                <th>Email</th>
                <th>Vai trò</th>
                <th>Mã sinh viên</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`badge ${
                      user.role === 'admin' ? 'badge-error' : 
                      user.role === 'instructor' ? 'badge-warning' : 
                      'badge-primary'
                    }`}>
                      {user.role === 'admin' ? 'Quản trị viên' : 
                       user.role === 'instructor' ? 'Giảng viên' : 
                       'Sinh viên'}
                    </span>
                  </td>
                  <td>{user.studentId || '-'}</td>
                  <td>
                    <span className={`badge ${user.firstLogin ? 'badge-warning' : 'badge-success'}`}>
                      {user.firstLogin ? 'Chưa đổi mật khẩu' : 'Đã kích hoạt'}
                    </span>
                  </td>
                  <td>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="btn btn-secondary btn-sm"
                        title="Chỉnh sửa"
                      >
                        <FaEdit />
                      </button>
                      <button
                        onClick={() => handleResetPassword(user)}
                        className="btn btn-warning btn-sm"
                        title="Đặt lại mật khẩu"
                      >
                        <FaKey />
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="btn btn-danger btn-sm"
                        title="Xóa"
                      >
                        <FaTrash />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Modal for adding/editing user */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            <h2 className="text-xl font-bold mb-4">
              {editingUser ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới'}
            </h2>
            
            <Formik
              initialValues={{
                name: editingUser?.name || '',
                email: editingUser?.email || '',
                role: editingUser?.role || 'student',
                studentId: editingUser?.studentId || ''
              }}
              validationSchema={UserSchema}
              onSubmit={handleSubmitUser}
            >
              {({ isSubmitting, values }) => (
                <Form>
                  <div className="form-group">
                    <label htmlFor="name" className="block mb-2">Họ tên</label>
                    <Field name="name" type="text" className="form-control" />
                    <ErrorMessage name="name" component="div" className="error-message" />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="email" className="block mb-2">Email</label>
                    <Field name="email" type="email" className="form-control" />
                    <ErrorMessage name="email" component="div" className="error-message" />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="role" className="block mb-2">Vai trò</label>
                    <Field name="role" as="select" className="form-control">
                      <option value="student">Sinh viên</option>
                      <option value="instructor">Giảng viên</option>
                      <option value="admin">Quản trị viên</option>
                    </Field>
                    <ErrorMessage name="role" component="div" className="error-message" />
                  </div>
                  
                  {values.role === 'student' && (
                    <div className="form-group">
                      <label htmlFor="studentId" className="block mb-2">Mã sinh viên</label>
                      <Field name="studentId" type="text" className="form-control" />
                      <ErrorMessage name="studentId" component="div" className="error-message" />
                    </div>
                  )}
                  
                  {!editingUser && (
                    <div className="bg-secondary-color p-4 rounded mb-4 mt-4">
                      <p className="text-sm">
                        Mật khẩu mặc định sẽ được tạo tự động và người dùng sẽ được yêu cầu đổi mật khẩu khi đăng nhập lần đầu.
                      </p>
                    </div>
                  )}
                  
                  <div className="flex justify-end gap-2 mt-6">
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="btn btn-secondary"
                    >
                      Hủy
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Đang xử lý...' : (editingUser ? 'Cập nhật' : 'Thêm mới')}
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        </div>
      )}
      
      {/* Modal for resetting password */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            <h2 className="text-xl font-bold mb-4">Đặt lại mật khẩu</h2>
            
            <p className="mb-4">
              Bạn đang đặt lại mật khẩu cho người dùng: <strong>{resetUser.name}</strong>
            </p>
            
            <Formik
              initialValues={{ newPassword: '' }}
              validationSchema={ResetPasswordSchema}
              onSubmit={handleSubmitReset}
            >
              {({ isSubmitting }) => (
                <Form>
                  <div className="form-group">
                    <label htmlFor="newPassword" className="block mb-2">Mật khẩu mới</label>
                    <Field name="newPassword" type="password" className="form-control" />
                    <ErrorMessage name="newPassword" component="div" className="error-message" />
                  </div>
                  
                  <div className="bg-warning-color bg-opacity-20 p-4 rounded mb-4 mt-4">
                    <p className="text-sm text-warning-color">
                      Người dùng sẽ được yêu cầu đổi mật khẩu khi đăng nhập lần tiếp theo.
                    </p>
                  </div>
                  
                  <div className="flex justify-end gap-2 mt-6">
                    <button
                      type="button"
                      onClick={() => setShowResetModal(false)}
                      className="btn btn-secondary"
                    >
                      Hủy
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Đang xử lý...' : 'Đặt lại mật khẩu'}
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserManagement
