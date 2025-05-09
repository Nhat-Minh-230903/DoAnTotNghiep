import React, { useState } from 'react'
import { FaStar } from 'react-icons/fa'

const StarRating = ({ rating, onChange, readOnly = false }) => {
  const [hover, setHover] = useState(null)
  
  return (
    <div className="flex">
      {[...Array(5)].map((_, index) => {
        const ratingValue = index + 1
        
        return (
          <label key={index} className="cursor-pointer">
            <input
              type="radio"
              name="rating"
              value={ratingValue}
              className="hidden"
              onClick={() => !readOnly && onChange(ratingValue)}
            />
            <FaStar
              className="mr-1"
              size={24}
              color={ratingValue <= (hover || rating) ? "#ffc107" : "#e4e5e9"}
              onMouseEnter={() => !readOnly && setHover(ratingValue)}
              onMouseLeave={() => !readOnly && setHover(null)}
            />
          </label>
        )
      })}
    </div>
  )
}

export default StarRating
