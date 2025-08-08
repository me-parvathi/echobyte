"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '@/lib/api'

interface AuthState {
  isAuthenticated: boolean
  isInitialized: boolean
  isLoading: boolean
  user: {
    email: string
    name: string
    type: string
    employeeId?: string
  } | null
}

interface AuthContextType extends AuthState {
  login: (credentials: { username: string; password: string }) => Promise<boolean>
  logout: () => void
  refreshAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isInitialized: false,
    isLoading: true,
    user: null,
  })

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const userEmail = localStorage.getItem('userEmail')
        const userType = localStorage.getItem('userType')
        const employeeId = localStorage.getItem('employeeId')

        if (!token || !userEmail || !userType) {
          setAuthState({
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            user: null,
          })
          return
        }

        // Verify token is still valid
        try {
          await api.get('/api/auth/me')
          
          setAuthState({
            isAuthenticated: true,
            isInitialized: true,
            isLoading: false,
            user: {
              email: userEmail,
              name: localStorage.getItem('userName') || userEmail,
              type: userType,
              employeeId: employeeId || undefined,
            },
          })
        } catch (error) {
          // Token is invalid, clear storage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('userEmail')
          localStorage.removeItem('userName')
          localStorage.removeItem('userType')
          localStorage.removeItem('employeeId')
          
          setAuthState({
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            user: null,
          })
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        setAuthState({
          isAuthenticated: false,
          isInitialized: true,
          isLoading: false,
          user: null,
        })
      }
    }

    checkAuth()
  }, [])

  const login = async (credentials: { username: string; password: string }): Promise<boolean> => {
    setAuthState(prev => ({ ...prev, isLoading: true }))

    try {
      // Call login API
      const response = await api.post('/api/auth/login', credentials)
      
      // Store tokens
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('userEmail', credentials.username)

      // Fetch user info and roles
      const [userInfo, { userType }, employeeInfo] = await Promise.all([
        api.get('/api/auth/me'),
        import('@/lib/role-utils').then(m => m.fetchUserRoles()),
        api.get('/api/employees/profile/current').catch(() => null)
      ])

      // Store user data
      localStorage.setItem('userEmail', userInfo.Email)
      localStorage.setItem('userName', userInfo.Username)
      localStorage.setItem('userType', userType)
      
      if (employeeInfo?.EmployeeID) {
        localStorage.setItem('employeeId', employeeInfo.EmployeeID.toString())
      }

      setAuthState({
        isAuthenticated: true,
        isInitialized: true,
        isLoading: false,
        user: {
          email: userInfo.Email,
          name: userInfo.Username,
          type: userType,
          employeeId: employeeInfo?.EmployeeID?.toString(),
        },
      })

      return true
    } catch (error) {
      console.error('Login failed:', error)
      setAuthState(prev => ({ ...prev, isLoading: false }))
      return false
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userName')
    localStorage.removeItem('userType')
    localStorage.removeItem('employeeId')
    
    setAuthState({
      isAuthenticated: false,
      isInitialized: true,
      isLoading: false,
      user: null,
    })
  }

  const refreshAuth = async () => {
    if (!authState.isAuthenticated) return

    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        logout()
        return
      }

      const response = await api.post('/api/auth/refresh', {
        refresh_token: refreshToken
      })

      localStorage.setItem('access_token', response.access_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 