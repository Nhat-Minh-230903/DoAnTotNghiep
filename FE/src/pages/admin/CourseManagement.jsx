import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'

const CourseSchema = Yup.object().shape({
  code: Yup.string().required('Vui lòng nhập mã môn học'),
  name: Yup.string().required('Vui lòng nhập tên môn học'),
  semester: Yup.string().required('Vui lòng nhập học kỳ'),
  instructorId: Yup.string().required('Vui lòng chọn giảng viên')
})

const CourseManagement = () => {
  const [courses, setCourses] = useState([])
  const [instructors, setInstructors] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingCourse, setEditingCourse] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [semester, setSemester] = useState('all')
  const [semesters, setSemesters] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [coursesResponse, instructorsResponse] = await Promise.all([
          axios.get(`${API_URL}/admin/courses`),
          axios.get(`${API_URL}/admin/instructors`)
        ])
        
        setCourses(coursesResponse.data.courses)
        setInstructors(instructorsResponse.data.instructors)
        
        // Extract unique semesters
        const uniqueSemesters = [...new Set(coursesResponse.data.courses.map(course => course.semester))]
        setSemesters(uniqueSemesters)
      } catch (error) {
        toast.error('Không thể tải dữ liệu')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleAddCourse = () => {
    setEditingCourse(null)
    setShowModal(true)
  }

  const handleEditCourse = (course) => {
    setEditingCourse(course)
    setShowModal(true)
  }

  const handleDeleteCourse = async (courseId) => {
    if (!confirm('Bạn có chắc chắn muốn xóa môn học này?')) return
    
    try {
      await axios.delete(`${API_URL}/admin/courses/${courseId}`)
      setCourses(courses.filter(course => course.id !== courseId))
      toast.success('Xóa môn học thành công')
    } catch (error) {
      toast.error('Không thể xóa môn học')
    }
  }

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      if (editingCourse) {
        // Update existing course
        const response = await axios.put(`${API_URL}/admin/courses/${editingCourse.id}`, values)
        setCourses(courses.map(course => 
          course.id === editingCourse.id ? response.data.course : course
        ))
        toast.success('Cập nhật môn học thành công')
      } else {
        // Create new course
        const response = await axios.post(`${API_URL}/admin/courses`, values)
        setCourses([...courses, response.data.course])
        toast.success('Thêm môn học thành công')
      }
      
      setShowModal(false)
      resetForm()
    } catch (error) {
      toast.error(error.response?.data?.message || 'Có lỗi xảy ra')
    } finally {
      setSubmitting(false)
    }
  }

  const filteredCourses = courses.filter(course => {
    const matchesSemester = semester === 'all' || course.semester === semester
    const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          course.code.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesSemester && matchesSearch
  })

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Quản lý môn học</h1>
        <button 
          onClick={handleAddCourse}
          className="btn btn-primary flex items-center"
        >
          <FaPlus className="mr-2" />
          Thêm môn học
        </button>
      </div>
      
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="form-group mb-0 flex-1">
          <input
            type="text"
            className="form-control"
            placeholder="Tìm kiếm theo tên hoặc mã môn học"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="form-group mb-0 md:w-64">
          <select
            className="form-control"
            value={semester}
            onChange={(e) => setSemester(e.target.value)}
          >
            <option value="all">Tất cả học kỳ</option>
            {semesters.map((sem) => (
              <option key={sem} value={sem}>{sem}</option>
            ))}
          </select>
        </div>
      </div>
      
      {filteredCourses.length === 0 ? (
        <div className="card text-center p-6">
          <p>Không tìm thấy môn học nào.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Mã môn</th>
                <th>Tên môn học</th>
                <th>Học kỳ</th>
                <th>Giảng viên</th>
                <th>Số SV đánh giá</th>
                <th>Đánh giá TB</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredCourses.map((course) => (
                <tr key={course.id}>
                  <td>{course.code}</td>
                  <td>{course.name}</td>
                  <td>{course.semester}</td>
                  <td>{course.instructor}</td>
                  <td>{course.evaluationCount}/{course.studentCount}</td>
                  <td>{course.averageRating ? course.averageRating.toFixed(1) : 'N/A'}</td>
                  <td>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditCourse(course)}
                        className="btn btn-secondary btn-sm"
                      >
                        <FaEdit />
                      </button>
                      <button
                        onClick={() => handleDeleteCourse(course.id)}
                        className="btn btn-danger btn-sm"
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
      
      {/* Modal for adding/editing course */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-md p-6">
            <h2 className="text-xl font-bold mb-4">
              {editingCourse ? 'Chỉnh sửa môn học' : 'Thêm môn học mới'}
            </h2>
            
            <Formik
              initialValues={{
                code: editingCourse?.code || '',
                name: editingCourse?.name || '',
                semester: editingCourse?.semester || '',
                instructorId: editingCourse?.instructorId || ''
              }}
              validationSchema={CourseSchema}
              onSubmit={handleSubmit}
            >
              {({ isSubmitting }) => (
                <Form>
                  <div className="form-group">
                    <label htmlFor="code" className="block mb-2">Mã môn học</label>
                    <Field name="code" type="text" className="form-control" />
                    <ErrorMessage name="code" component="div" className="error-message" />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="name" className="block mb-2">Tên môn học</label>
                    <Field name="name" type="text" className="form-control" />
                    <ErrorMessage name="name" component="div" className="error-message" />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="semester" className="block mb-2">Học kỳ</label>
                    <Field name="semester" type="text" className="form-control" />
                    <ErrorMessage name="semester" component="div" className="error-message" />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="instructorId" className="block mb-2">Giảng viên</label>
                    <Field name="instructorId" as="select" className="form-control">
                      <option value="">Chọn giảng viên</option>
                      {instructors.map((instructor) => (
                        <option key={instructor.id} value={instructor.id}>
                          {instructor.name}
                        </option>
                      ))}
                    </Field>
                    <ErrorMessage name="instructorId" component="div" className="error-message" />
                  </div>
                  
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
                      {isSubmitting ? 'Đang xử lý...' : (editingCourse ? 'Cập nhật' : 'Thêm mới')}
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

export default CourseManagement
