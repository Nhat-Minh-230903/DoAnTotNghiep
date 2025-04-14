import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_URL } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaCheckCircle, FaExclamationCircle } from 'react-icons/fa'

const StudentDashboard = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'evaluated', 'not-evaluated'
  const [semester, setSemester] = useState('all')
  const [semesters, setSemesters] = useState([])

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get(`${API_URL}/student/courses`)
        setCourses(response.data.courses)
        
        // Extract unique semesters
        const uniqueSemesters = [...new Set(response.data.courses.map(course => course.semester))]
        setSemesters(uniqueSemesters)
      } catch (error) {
        toast.error('Không thể tải danh sách môn học')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()
  }, [])

  const filteredCourses = courses.filter(course => {
    const semesterMatch = semester === 'all' || course.semester === semester
    
    if (filter === 'all') return semesterMatch
    if (filter === 'evaluated') return course.isEvaluated && semesterMatch
    if (filter === 'not-evaluated') return !course.isEvaluated && semesterMatch
    
    return true
  })

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Danh sách môn học</h1>
      
      <div className="flex gap-4 mb-6">
        <div className="form-group mb-0">
          <label htmlFor="filter" className="block mb-2">Lọc theo trạng thái</label>
          <select
            id="filter"
            className="form-control"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">Tất cả</option>
            <option value="evaluated">Đã đánh giá</option>
            <option value="not-evaluated">Chưa đánh giá</option>
          </select>
        </div>
        
        <div className="form-group mb-0">
          <label htmlFor="semester" className="block mb-2">Học kỳ</label>
          <select
            id="semester"
            className="form-control"
            value={semester}
            onChange={(e) => setSemester(e.target.value)}
          >
            <option value="all">Tất cả</option>
            {semesters.map((sem) => (
              <option key={sem} value={sem}>{sem}</option>
            ))}
          </select>
        </div>
      </div>
      
      {filteredCourses.length === 0 ? (
        <div className="card text-center p-6">
          <p>Không có môn học nào phù hợp với bộ lọc.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCourses.map((course) => (
            <div key={course.id} className="card">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-bold">{course.name}</h3>
                {course.isEvaluated ? (
                  <span className="flex items-center text-success-color">
                    <FaCheckCircle className="mr-1" />
                    Đã đánh giá
                  </span>
                ) : (
                  <span className="flex items-center text-warning-color">
                    <FaExclamationCircle className="mr-1" />
                    Chưa đánh giá
                  </span>
                )}
              </div>
              
              <div className="mb-4">
                <p><strong>Mã môn:</strong> {course.code}</p>
                <p><strong>Giảng viên:</strong> {course.instructor}</p>
                <p><strong>Học kỳ:</strong> {course.semester}</p>
              </div>
              
              <div className="flex justify-end">
                {course.isEvaluated ? (
                  <Link 
                    to={`/evaluate/${course.id}`} 
                    className="btn btn-secondary"
                  >
                    Xem đánh giá
                  </Link>
                ) : (
                  <Link 
                    to={`/evaluate/${course.id}`} 
                    className="btn btn-primary"
                  >
                    Đánh giá
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default StudentDashboard
