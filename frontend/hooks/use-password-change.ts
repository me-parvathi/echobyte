"use client"

import { useState } from "react"
import { api } from "@/lib/api"

interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

interface PasswordChangeResponse {
  message: string
}

interface UsePasswordChangeReturn {
  changePassword: (data: PasswordChangeRequest) => Promise<boolean>
  loading: boolean
  error: string | null
  success: boolean
  resetState: () => void
}

export function usePasswordChange(onSuccess?: () => void): UsePasswordChangeReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const changePassword = async (data: PasswordChangeRequest): Promise<boolean> => {
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      // Get current user ID from localStorage
      const userEmail = localStorage.getItem("userEmail")
      if (!userEmail) {
        throw new Error("User not authenticated")
      }

      // Get user info to get UserID
      const userInfo = await api.get<any>("/api/auth/me")
      const userId = userInfo.UserID

      // Make API call to change password
      const response = await api.post<PasswordChangeResponse>(
        `/api/auth/users/${userId}/change-password`,
        data
      )

      setSuccess(true)
      if (onSuccess) {
        onSuccess()
      }
      return true
    } catch (err: any) {
      console.error("Password change failed:", err)
      
      // Handle different error types
      if (err.message?.includes("Current password is incorrect")) {
        setError("Current password is incorrect")
      } else if (err.message?.includes("New password must be different")) {
        setError("New password must be different from current password")
      } else if (err.message?.includes("Password must be at least")) {
        setError("Password must be at least 8 characters long")
      } else if (err.message?.includes("Password must contain at least one uppercase")) {
        setError("Password must contain at least one uppercase letter")
      } else if (err.message?.includes("Password must contain at least one lowercase")) {
        setError("Password must contain at least one lowercase letter")
      } else if (err.message?.includes("Password must contain at least one number")) {
        setError("Password must contain at least one number")
      } else if (err.message?.includes("You can only change your own password")) {
        setError("You can only change your own password")
      } else {
        setError(err.message || "Failed to change password")
      }
      
      return false
    } finally {
      setLoading(false)
    }
  }

  const resetState = () => {
    setLoading(false)
    setError(null)
    setSuccess(false)
  }

  return {
    changePassword,
    loading,
    error,
    success,
    resetState
  }
} 