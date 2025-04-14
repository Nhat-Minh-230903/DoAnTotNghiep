import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL, RATING_LABELS } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaDownload, FaChartBar } from 'react-icons/fa'

const Reports = () => {
  const [loading, setLoading] = useState(true)
  const [reportType, setReportType] = useState('course')
  const [semester, setSemester] = useState('all')
  const [semesters, setSemesters] = useState([])
  const [courseData, setCourseData] = useState([])
  const [instructorData, setInstructorData] = useState([])
  const [exportLoading, setExportLoading] = useState(false)

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const [semestersResponse, courseResponse, instructorResponse] = await Promise.all([
          axios.get(`${API_URL}/admin/semesters`),
          axios.get(`${API_URL}/admin/reports/courses?semester=${semester}`),
          axios.get(`${API_URL}/admin/reports/instructors?semester=${semester}`)
        ])
        
        setSemesters(semestersResponse.data.semesters)
        setCourseData(courseResponse.data.courses)
        setInstructorData(instructorResponse.data.instructors)
      } catch (error) {
        toast.error('Không thể tải dữ liệu báo cáo')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchReportData()
  }, [semester])

  const handleExport = async () => {
    setExportLoading(true)
    
    try {
      const response = await axios.get(
        `${API_URL}/admin/reports/export?type=${reportType}&semester=${semester}`,
        { responseType: 'blob' }
      )
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${reportType}_report_${semester || 'all'}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      
      toast.success('Xuất báo cáo thành công')
    } catch (error) {
      toast.error('Không thể xuất báo cáo')
    } finally {
      setExportLoading(false)
    }
  }

  const displayData = reportType === 'course' ? courseData : instructorData

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Báo cáo thống kê</h1>
        <button 
          onClick={handleExport}
          className="btn btn-primary flex items-center"
          disabled={exportLoading}
        >
          <FaDownload className="mr-2" />
          {exportLoading ? 'Đang xuất...' : 'Xuất báo cáo'}
        </button>
      </div>
      
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="form-group mb-0 md:w-64">
          <label htmlFor="reportType" className="block mb-2">Loại báo cáo</label>
          <select
            id="reportType"
            className="form-control"
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
          >
            <option value="course">Theo môn học</option>
            <option value="instructor">Theo giảng viên</option>
          </select>
        </div>
        
        <div className="form-group mb-0 md:w-64">
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
      
      {displayData.length === 0 ? (
        <div className="card text-center p-6">
          <p>Không có dữ liệu báo cáo cho bộ lọc đã chọn.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>{reportType === 'course' ? 'Môn học' : 'Giảng viên'}</th>
                {reportType === 'course' && <th>Giảng viên</th>}
                {reportType === 'instructor' && <th>Số môn giảng dạy</th>}
                <th>Số SV đánh giá</th>
                <th>Tỷ lệ đánh giá</th>
                {Object.values(RATING_LABELS).map((label) => (
                  <th key={label}>{label}</th>
                ))}
                <th>Đánh giá TB</th>
              </tr>
            </thead>
            <tbody>
              {displayData.map((item) => (
                <tr key={item.id}>
                  <td>{reportType === 'course' ? item.name : item.name}</td>
                  {reportType === 'course' && <td>{item.instructor}</td>}
                  {reportType === 'instructor' && <td>{item.courseCount}</td>}
                  <td>{item.evaluationCount}/{item.studentCount}</td>
                  <td>{((item.evaluationCount / item.studentCount) * 100).toFixed(1)}%</td>
                  {Object.keys(RATING_LABELS).map((category) => (
                    <td key={category}>
                      <div className="flex items-center">
                        <span className="mr-1">{item.categoryRatings[category].toFixed(1)}</span>
                        <FaChartBar className="text-warning-color" />
                      </div>
                    </td>
                  ))}
                  <td>
                    <div className="flex items-center">
                      <span className="mr-1">{item.averageRating.toFixed(1)}</span>
                      <FaChartBar className="text-warning-color" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Reports
