import React, { useState, useEffect } from 'react'
import { FaUsers, FaBook, FaChartBar, FaExclamationTriangle } from 'react-icons/fa'
import axios from 'axios'
import { API_URL } from '../../config/constants'
import { toast } from 'react-toastify'

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalCourses: 0,
    totalEvaluations: 0,
    pendingEvaluations: 0
  })
  const [loading, setLoading] = useState(true)
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // In a real app, these would be actual API calls
        // For now, we'll simulate the data
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Mock data
        setStats({
          totalUsers: 245,
          totalCourses: 32,
          totalEvaluations: 1876,
          pendingEvaluations: 43
        })
        
        setRecentActivity([
          { id: 1, type: 'evaluation', user: 'Nguyễn Văn A', course: 'Lập trình web', timestamp: '2023-06-15T08:30:00Z' },
          { id: 2, type: 'user_added', user: 'Trần Thị B', role: 'student', timestamp: '2023-06-14T14:45:00Z' },
          { id: 3, type: 'course_added', course: 'Trí tuệ nhân tạo', instructor: 'Dr. Nguyễn C', timestamp: '2023-06-14T10:15:00Z' },
          { id: 4, type: 'evaluation', user: 'Lê Văn D', course: 'Cơ sở dữ liệu', timestamp: '2023-06-13T16:20:00Z' },
          { id: 5, type: 'user_added', user: 'Phạm Thị E', role: 'instructor', timestamp: '2023-06-12T09:10:00Z' }
        ])
      } catch (error) {
        toast.error('Không thể tải dữ liệu tổng quan')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'evaluation':
        return <FaChartBar className="text-primary-color" />
      case 'user_added':
        return <FaUsers className="text-success-color" />
      case 'course_added':
        return <FaBook className="text-info-color" />
      default:
        return null
    }
  }

  const getActivityText = (activity) => {
    switch (activity.type) {
      case 'evaluation':
        return `${activity.user} đã đánh giá môn học ${activity.course}`
      case 'user_added':
        return `${activity.user} (${activity.role === 'student' ? 'Sinh viên' : 'Giảng viên'}) đã được thêm vào hệ thống`
      case 'course_added':
        return `Môn học ${activity.course} (${activity.instructor}) đã được thêm vào hệ thống`
      default:
        return ''
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Tổng quan hệ thống</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="card bg-white p-4 rounded shadow">
          <div className="flex items-center">
            <div className="rounded-full bg-blue-100 p-3 mr-4">
              <FaUsers className="text-blue-500 text-xl" />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Tổng số người dùng</h3>
              <p className="text-2xl font-bold">{stats.totalUsers}</p>
            </div>
          </div>
        </div>
        
        <div className="card bg-white p-4 rounded shadow">
          <div className="flex items-center">
            <div className="rounded-full bg-green-100 p-3 mr-4">
              <FaBook className="text-green-500 text-xl" />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Tổng số môn học</h3>
              <p className="text-2xl font-bold">{stats.totalCourses}</p>
            </div>
          </div>
        </div>
        
        <div className="card bg-white p-4 rounded shadow">
          <div className="flex items-center">
            <div className="rounded-full bg-purple-100 p-3 mr-4">
              <FaChartBar className="text-purple-500 text-xl" />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Đánh giá đã hoàn thành</h3>
              <p className="text-2xl font-bold">{stats.totalEvaluations}</p>
            </div>
          </div>
        </div>
        
        <div className="card bg-white p-4 rounded shadow">
          <div className="flex items-center">
            <div className="rounded-full bg-yellow-100 p-3 mr-4">
              <FaExclamationTriangle className="text-yellow-500 text-xl" />
            </div>
            <div>
              <h3 className="text-gray-500 text-sm">Đánh giá đang chờ</h3>
              <p className="text-2xl font-bold">{stats.pendingEvaluations}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card bg-white p-4 rounded shadow">
        <h2 className="text-xl font-bold mb-4">Hoạt động gần đây</h2>
        
        <div className="divide-y">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="py-3 flex items-start">
              <div className="mr-3 mt-1">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1">
                <p>{getActivityText(activity)}</p>
                <p className="text-sm text-gray-500">{formatDate(activity.timestamp)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
