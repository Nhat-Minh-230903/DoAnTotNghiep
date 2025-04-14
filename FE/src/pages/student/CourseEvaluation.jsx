import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_URL, RATING_CATEGORIES, RATING_LABELS, MIN_RATING_WITHOUT_COMMENT } from '../../config/constants'
import { toast } from 'react-toastify'
import StarRating from '../../components/StarRating'

const CourseEvaluation = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [viewOnly, setViewOnly] = useState(false)
  
  const [ratings, setRatings] = useState({
    [RATING_CATEGORIES.LECTURE_QUALITY]: 0,
    [RATING_CATEGORIES.INSTRUCTOR_QUALITY]: 0,
    [RATING_CATEGORIES.CLASSROOM_QUALITY]: 0,
    [RATING_CATEGORIES.EQUIPMENT_QUALITY]: 0
  })
  
  const [comments, setComments] = useState({
    [RATING_CATEGORIES.LECTURE_QUALITY]: '',
    [RATING_CATEGORIES.INSTRUCTOR_QUALITY]: '',
    [RATING_CATEGORIES.CLASSROOM_QUALITY]: '',
    [RATING_CATEGORIES.EQUIPMENT_QUALITY]: ''
  })
  
  const [generalComment, setGeneralComment] = useState('')

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        const response = await axios.get(`${API_URL}/student/courses/${courseId}`)
        setCourse(response.data.course)
        
        // If course is already evaluated, load the evaluation data
        if (response.data.evaluation) {
          const evaluation = response.data.evaluation
          setRatings(evaluation.ratings)
          setComments(evaluation.comments)
          setGeneralComment(evaluation.generalComment)
          setViewOnly(true)
        }
      } catch (error) {
        toast.error('Không thể tải thông tin môn học')
        navigate('/')
      } finally {
        setLoading(false)
      }
    }

    fetchCourseDetails()
  }, [courseId, navigate])

  const handleRatingChange = (category, value) => {
    setRatings(prev => ({
      ...prev,
      [category]: value
    }))
  }

  const handleCommentChange = (category, value) => {
    setComments(prev => ({
      ...prev,
      [category]: value
    }))
  }

  const validateForm = () => {
    // Check if all categories are rated
    const unratedCategories = Object.entries(ratings).filter(([_, value]) => value === 0)
    
    if (unratedCategories.length > 0) {
      toast.error('Vui lòng đánh giá tất cả các mục')
      return false
    }
    
    // Check if comments are provided for ratings below MIN_RATING_WITHOUT_COMMENT
    const lowRatingsWithoutComments = Object.entries(ratings)
      .filter(([category, value]) => value < MIN_RATING_WITHOUT_COMMENT && !comments[category])
    
    if (lowRatingsWithoutComments.length > 0) {
      toast.error(`Vui lòng cung cấp bình luận cho các mục đánh giá dưới ${MIN_RATING_WITHOUT_COMMENT} sao`)
      return false
    }
    
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setSubmitting(true)
    
    try {
      await axios.post(`${API_URL}/student/courses/${courseId}/evaluate`, {
        ratings,
        comments,
        generalComment
      })
      
      toast.success('Đánh giá môn học thành công')
      navigate('/')
    } catch (error) {
      toast.error('Không thể gửi đánh giá')
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
        <h1 className="text-2xl font-bold">
          {viewOnly ? 'Xem đánh giá môn học' : 'Đánh giá môn học'}
        </h1>
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
            <p><strong>Giảng viên:</strong> {course.instructor}</p>
            <p><strong>Thời gian:</strong> {course.schedule}</p>
          </div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        {Object.entries(RATING_LABELS).map(([category, label]) => (
          <div key={category} className="card mb-4">
            <h3 className="text-lg font-bold mb-4">{label}</h3>
            
            <div className="mb-4">
              <label className="block mb-2">Đánh giá:</label>
              <StarRating
                name={`rating-${category}`}
                value={ratings[category]}
                onChange={(value) => handleRatingChange(category, value)}
                disabled={viewOnly}
              />
            </div>
            
            <div className="form-group mb-0">
              <label className="block mb-2">
                Bình luận:
                {ratings[category] < MIN_RATING_WITHOUT_COMMENT && !viewOnly && (
                  <span className="text-error-color ml-1">*</span>
                )}
              </label>
              <textarea
                className="form-control"
                value={comments[category]}
                onChange={(e) => handleCommentChange(category, e.target.value)}
                placeholder={`Nhập bình luận về ${label.toLowerCase()}`}
                rows={3}
                disabled={viewOnly}
                required={ratings[category] < MIN_RATING_WITHOUT_COMMENT}
              />
            </div>
          </div>
        ))}
        
        <div className="card mb-6">
          <h3 className="text-lg font-bold mb-4">Bình luận chung</h3>
          <div className="form-group mb-0">
            <textarea
              className="form-control"
              value={generalComment}
              onChange={(e) => setGeneralComment(e.target.value)}
              placeholder="Nhập bình luận chung về môn học (không bắt buộc)"
              rows={4}
              disabled={viewOnly}
            />
          </div>
        </div>
        
        {!viewOnly && (
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? 'Đang gửi...' : 'Gửi đánh giá'}
            </button>
          </div>
        )}
      </form>
    </div>
  )
}

export default CourseEvaluation
