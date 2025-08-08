"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import { LoginRequest, LoginResponse, UserResponse } from "@/lib/types"
import { fetchUserRoles } from "@/lib/role-utils"

interface UseAuthReturn {
  login: (credentials: LoginRequest) => Promise<LoginResponse | null>
  logout: () => void
  refreshToken: () => Promise<boolean>
  loading: boolean
  error: string | null
  setError: (error: string | null) => void
}

export function useAuth(): UseAuthReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        console.log('No refresh token available')
        return false
      }

      console.log('🔄 Manually refreshing token...')
      const response = await api.post<LoginResponse>("/api/auth/refresh", {
        refresh_token: refreshToken
      })

      if (response && response.access_token) {
        localStorage.setItem("access_token", response.access_token)
        console.log('✅ Token refreshed successfully')
        return true
      }
      return false
    } catch (error) {
      console.error('❌ Manual token refresh failed:', error)
      // Clear tokens on failure
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      return false
    }
  }

  const login = async (credentials: LoginRequest): Promise<LoginResponse | null> => {
    setLoading(true)
    setError(null)
    
    console.log("🔐 Starting login process...", { username: credentials.username })

    try {
      // Call backend login endpoint
      console.log("📡 Making API call to /api/auth/login...")
      const response = await api.post<LoginResponse>("/api/auth/login", credentials)
      console.log("✅ Login successful:", response)

      // Persist tokens in localStorage (browser only)
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", response.access_token)
        localStorage.setItem("refresh_token", response.refresh_token)
        // Store basic identity to satisfy dashboard guard; refined later
        localStorage.setItem("userEmail", credentials.username)
        console.log("💾 Tokens stored in localStorage")
      }

      // Fetch user info and roles
      try {
        console.log("👤 Fetching user info...")
        const userInfo = await api.get<UserResponse>("/api/auth/me")
        console.log("✅ User info fetched:", userInfo)

        // Fetch user roles and determine user type
        const { roles, userType } = await fetchUserRoles()
        console.log("✅ User roles and type determined:", { roles, userType })

        if (typeof window !== "undefined") {
          localStorage.setItem("userEmail", userInfo.Email)
          localStorage.setItem("userName", userInfo.Username)
          localStorage.setItem("userType", userType)
          console.log("💾 User info and roles stored in localStorage")
        }
      } catch (userError) {
        console.warn("⚠️ Failed to fetch user info or roles:", userError)
        // Set default user type if role fetching fails
        if (typeof window !== "undefined") {
          localStorage.setItem("userType", "employee")
        }
      }

      // Fetch current employee information and store employee ID
      try {
        console.log("👤 Fetching employee info...")
        const employeeInfo = await api.get<any>("/api/employees/profile/current")
        console.log("✅ Employee info fetched:", employeeInfo)
        if (typeof window !== "undefined" && employeeInfo.EmployeeID) {
          localStorage.setItem("employeeId", employeeInfo.EmployeeID.toString())
          console.log("💾 Employee ID stored in localStorage:", employeeInfo.EmployeeID)
        }
      } catch (employeeError) {
        console.warn("⚠️ Failed to fetch employee info:", employeeError)
        // Silently ignore for now – can be handled by caller
      }

      return response
    } catch (err: any) {
      console.error("❌ Login failed:", err)
      
      // Handle different types of errors gracefully
      if (err.isAuthError) {
        // Authentication errors (401, 403)
        if (err.authErrorType === "username_not_found") {
          setError("No existing user with this username. Please contact your IT department.")
        } else if (err.authErrorType === "password_incorrect") {
          setError("Password is incorrect. Please contact IT for assistance.")
        } else if (err.message.includes("terminated")) {
          setError("Access denied. Your employment has been terminated. Please contact HR for assistance.")
        } else {
          setError("Authentication failed. Please check your credentials and try again.")
        }
      } else if (err.isDatabaseError) {
        // Database connection errors (500 with database-related messages)
        setError("Database connection error. Please try again in a few moments or contact IT support if the problem persists.")
      } else if (err.isNetworkError) {
        // Other server errors (500+)
        setError("Server error. Please try again later or contact support if the problem persists.")
      } else if (err.message.includes("fetch") || err.message.includes("network")) {
        // Network errors
        setError("Network error. Please check your internet connection and try again.")
      } else {
        // Generic error fallback
        setError(err.message || "Login failed. Please try again.")
      }
      
      return null
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("userEmail")
      localStorage.removeItem("userName")
      localStorage.removeItem("userType")
      localStorage.removeItem("employeeId")
    }
  }

  return { login, logout, refreshToken, loading, error, setError }
} 