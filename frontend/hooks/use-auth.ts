"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import { LoginRequest, LoginResponse, UserResponse } from "@/lib/types"

interface UseAuthReturn {
  login: (credentials: LoginRequest) => Promise<LoginResponse | null>
  logout: () => void
  loading: boolean
  error: string | null
}

export function useAuth(): UseAuthReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (credentials: LoginRequest): Promise<LoginResponse | null> => {
    setLoading(true)
    setError(null)

    try {
      // Call backend login endpoint
      const response = await api.post<LoginResponse>("/auth/login", credentials)

      // Persist tokens in localStorage (browser only)
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", response.access_token)
        localStorage.setItem("refresh_token", response.refresh_token)
        // Store basic identity to satisfy dashboard guard; refined later
        localStorage.setItem("userEmail", credentials.username)
        localStorage.setItem("userType", "employee")
      }

      // Optionally fetch user info and store basic details
      try {
        const userInfo = await api.get<UserResponse>("/auth/me")
        if (typeof window !== "undefined") {
          localStorage.setItem("userEmail", userInfo.Email)
          localStorage.setItem("userName", userInfo.Username)
          localStorage.setItem("userType", "employee") // Placeholder role, adjust when role endpoint is used
        }
      } catch {
        // Silently ignore for now – can be handled by caller
      }

      return response
    } catch (err: any) {
      setError(err.message || "Login failed")
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
    }
  }

  return { login, logout, loading, error }
} 