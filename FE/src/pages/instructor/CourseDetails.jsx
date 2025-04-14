import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL, RATING_LABELS } from '../../config/constants'
import { toast } from 'react-toastify'
import { FaStar, FaReply, FaCheck } from 'react-icons/fa'

const InstructorCourseDetails = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState(null)
  const [evaluations, setEvaluations] = useState([])
  const [loading, setLoading] = useState(true)
  const [replies, setReplies] = useState({})
  const [replyingTo, setReplyingTo] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        const response = await axios.get(`${API_URL}/instructor/courses/${courseId}`)
        setCourse(response.data.course)
        setEvaluations(response.data.evaluations)
        
        // Initialize replies from existing data
        const initialReplies = {}
        response.data.evaluations.forEach(evaluation => {
          if (evaluation.instructorReply) {
            initialReplies[evaluation.id] = evaluation.instructorReply
          }
        })
        setReplies(initialReplies)
      } catch (error) {
        toast.error('Không thể tải thông tin môn học')
        navigate('/')
      } finally {
        setLoading(false)
      }
    }

    fetchCourseDetails()
  }, [courseId, navigate])

  const handleReplyChange = (evaluationId, value) => {
    setReplies(prev => ({
      ...prev,
      [evaluationId]: value
    }))
  }

  const handleSubmitReply = async (evaluationId) => {
    if (!replies[evaluationId]?.trim()) {
      toast.error('Vui lòng nhập nội dung phản hồi')
      return
    }
    
    setSubmitting(true)
    
    try {
      await axios.post(`${API_URL}/instructor/evaluations/${evaluationId}/reply`, {
        reply: replies[evaluationId]
      })
      
      // Update the local state
      setEvaluations(prev => 
        prev.map(evaluation => 
          evaluation.id === evaluationId 
            ? { ...evaluation, instructorReply: replies[evaluationId] } 
            : evaluation
        )
      )
      
      setReplyingTo(null)
      toast.success('Gửi phản hồi thành công')
    } catch (error) {
      toast.error('Không thể gửi phản hồi')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Chi tiết môn học</h1>
        <button 
          onClick={() => navigate('/')}
          className="btn btn-secondary"
        >
          Quay lại
        </button>
      </div>
      
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-4">{course.name}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p><strong>Mã môn:</strong> {course.code}</p>
            <p><strong>Học kỳ:</strong> {course.semester}</p>
          </div>
          <div>
            <p><strong>Số sinh viên:</strong> {course.studentCount}</p>
            <p><strong>Đã đánh giá:</strong> {course.evaluationCount} / {course.studentCount}</p>
          </div>
        </div>
      </div>
      
      <div className="card mb-6">
        <h3 className="text-lg font-bold mb-4">Thống kê đánh giá</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(RATING_LABELS).map(([category, label]) => (
            <div key={category} className="flex items-center justify-between">
              <span>{label}:</span>
              <div className="flex items-center">
                <span className="mr-2">{course.averageRatings[category].toFixed(1)}</span>
                <FaStar className="text-warning-color" />
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <h3 className="text-lg font-bold mb-4">Đánh giá của sinh viên ({evaluations.length})</h3>
      
      {evaluations.length === 0 ? (
        <div className="card text-center p-6">
          <p>Chưa có đánh giá nào cho môn học này.</p>
        </div>
      ) : (
        evaluations.map((evaluation) => (
          <div key={evaluation.id} className="card mb-4">
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="font-bold">Sinh viên: {evaluation.studentId}</span>
                <span className="text-sm text-gray-500">{new Date(evaluation.createdAt).toLocaleDateString()}</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
                {Object.entries(RATING_LABELS).map(([category, label]) => (
                  <div key={category} className="flex items-center">
                    <span className="mr-2">{label}:</span>
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <FaStar 
                          key={i}
                          className={i < evaluation.ratings[category] ? "text-warning-color" : "text-gray-300"}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              
              {Object.entries(evaluation.comments).filter(([_, comment]) => comment).map(([category, comment]) => (
                <div key={category} className="mb-2">
                  <p><strong>{RATING_LABELS[category]}:</strong> {comment}</p>
                </div>
              ))}
              
              {evaluation.generalComment && (
                <div className="mt-4">
                  <p><strong>Bình luận chung:</strong> {evaluation.generalComment}</p>
                </div>
              )}
            </div>
            
            {evaluation.instructorReply && (
              <div className="bg-secondary-color p-4 rounded mb-4">
                <div className="flex items-center mb-2">
                  <FaReply className="mr-2" />
                  <span className="font-bold">Phản hồi của giảng viên</span>
                </div>
                <p>{evaluation.instructorReply}</p>
              </div>
            )}
            
            {replyingTo === evaluation.id ? (
              <div>
                <textarea
                  className="form-control mb-2"
                  value={replies[evaluation.id] || ''}
                  onChange={(e) => handleReplyChange(evaluation.id, e.target.value)}
                  placeholder="Nhập phản hồi của bạn"
                  rows={3}
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setReplyingTo(null)}
                    className="btn btn-secondary"
                    disabled={submitting}
                  >
                    Hủy
                  </button>
                  <button
                    onClick={() => handleSubmitReply(evaluation.id)}
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? 'Đang gửi...' : 'Gửi phản hồi'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex justify-end">
                <button
                  onClick={() => setReplyingTo(evaluation.id)}
                  className="btn btn-primary"
                >
                  {evaluation.instructorReply ? 'Chỉnh sửa phản hồi' : 'Phản hồi'}
                </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}

export default InstructorCourseDetails
