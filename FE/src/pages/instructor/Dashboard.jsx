import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_URL, ROUTES } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaChartBar, FaEye, FaUsers } from 'react-icons/fa'

const InstructorDashboard = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [semester, setSemester] = useState('all')
  const [semesters, setSemesters] = useState([])

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        // In a real app, this would be an actual API call
        // For now, we'll simulate the data
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Mock data
        const mockCourses = [
          {
            id: 1,
            code: 'CS101',
            name: 'Nhập môn lập trình',
            semester: '2023-1',
            students: 45,
            evaluationsCompleted: 38,
            evaluationRate: 84,
            averageRating: 4.2
          },
          {
            id: 2,
            code: 'CS201',
            name: 'Cấu trúc dữ liệu và giải thuật',
            semester: '2023-1',
            students: 32,
            evaluationsCompleted: 28,
            evaluationRate: 87,
            averageRating: 4.5
          },
          {
            id: 3,
            code: 'CS301',
            name: 'Cơ sở dữ liệu',
            semester: '2022-2',
            students: 38,
            evaluationsCompleted: 35,
            evaluationRate: 92,
            averageRating: 4.7
          },
          {
            id: 4,
            code: 'CS401',
            name: 'Trí tuệ nhân tạo',
            semester: '2022-2',
            students: 25,
            evaluationsCompleted: 20,
            evaluationRate: 80,
            averageRating: 4.0
          }
        ]
        
        setCourses(mockCourses)
        
        // Extract unique semesters
        const uniqueSemesters = [...new Set(mockCourses.map(course => course.semester))]
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
    return semester === 'all' || course.semester === semester
  })

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Môn học của tôi</h1>
      
      <div className="flex gap-4 mb-6">
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
              <div className="mb-2">
                <h3 className="text-lg font-bold">{course.name}</h3>
                <p className="text-sm text-gray-600">{course.code}</p>
              </div>
              
              <div className="mb-4">
                <p><strong>Học kỳ:</strong> {course.semester}</p>
                <p><strong>Số sinh viên:</strong> {course.students}</p>
                <p><strong>Tỷ lệ đánh giá:</strong> {course.evaluationRate}% ({course.evaluationsCompleted}/{course.students})</p>
                <p><strong>Điểm trung bình:</strong> {course.averageRating}/5</p>
              </div>
              
              <div className="flex justify-between">
                <Link 
                  to={`${ROUTES.INSTRUCTOR.COURSE_DETAILS}/${course.id}`} 
                  className="btn btn-primary flex items-center gap-1"
                >
                  <FaEye />
                  <span>Chi tiết</span>
                </Link>
                
                <Link 
                  to={`${ROUTES.INSTRUCTOR.COURSE_DETAILS}/${course.id}/analytics`} 
                  className="btn btn-secondary flex items-center gap-1"
                >
                  <FaChartBar />
                  <span>Phân tích</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default InstructorDashboard
