import React, { createContext, useContext, useState, useEffect } from 'react'

// Create context
const AuthContext = createContext()

// Mock user data for development
const MOCK_USERS = [
  { id: 1, email: 'admin@example.com', password: 'admin123', name: 'Admin User', role: 'admin' },
  { id: 2, email: 'instructor@example.com', password: 'instructor123', name: 'Instructor User', role: 'instructor' },
  { id: 3, email: 'student@example.com', password: 'student123', name: 'Student User', role: 'student' }
]

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is stored in localStorage
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    // Mock authentication - in production, this would be an API call
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const foundUser = MOCK_USERS.find(
          u => u.email === email && u.password === password
        )
        
        if (foundUser) {
          // Remove password before storing
          const { password, ...userWithoutPassword } = foundUser
          setUser(userWithoutPassword)
          localStorage.setItem('user', JSON.stringify(userWithoutPassword))
          resolve(userWithoutPassword)
        } else {
          reject(new Error('Invalid credentials'))
        }
      }, 500) // Simulate network delay
    })
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  const changePassword = async (currentPassword, newPassword) => {
    // Mock password change - in production, this would be an API call
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Find the user in our mock data
        const userIndex = MOCK_USERS.findIndex(u => u.id === user.id)
        
        if (userIndex === -1) {
          reject(new Error('User not found'))
          return
        }
        
        if (MOCK_USERS[userIndex].password !== currentPassword) {
          reject(new Error('Current password is incorrect'))
          return
        }
        
        // Update password in mock data
        MOCK_USERS[userIndex].password = newPassword
        resolve(true)
      }, 500)
    })
  }

  const value = {
    user,
    loading,
    login,
    logout,
    changePassword
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  return useContext(AuthContext)
}

export default AuthContext
