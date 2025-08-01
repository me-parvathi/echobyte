"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

export interface UserInfo {
  email: string
  name: string
  department: string
  type: string
  reportsTo?: string
  managerName?: string
  employeeId?: string
  position?: string
  joinDate?: string
}

interface UseUserInfoResult {
  userInfo: UserInfo | null
  loading: boolean
}

export default function useUserInfo(): UseUserInfoResult {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  const fetchAndPersistUser = async () => {
    try {
      const { api } = await import("@/lib/api")
      const user = await api.get<any>("/auth/me")
      if (typeof window !== "undefined") {
        localStorage.setItem("userEmail", user.Email || user.Username)
        localStorage.setItem("userName", user.Username)
        localStorage.setItem("userType", "employee") // TODO: map real role
      }
      return {
        email: user.Email || user.Username,
        name: user.Username,
        department: "Unknown",
        type: "employee",
      } as UserInfo
    } catch {
      return null
    }
  }

  useEffect(() => {
    const storedUserType = localStorage.getItem("userType")
    const storedUserEmail = localStorage.getItem("userEmail")
    const token = localStorage.getItem("access_token")

    const init = async () => {
      if (!storedUserType || !storedUserEmail) {
        if (token) {
          const fetched = await fetchAndPersistUser()
          if (fetched) {
            setUserInfo(fetched)
            setLoading(false)
            return
          }
        }
        router.push("/")
        return
      }

      const info: UserInfo = {
        email: storedUserEmail,
        name: localStorage.getItem("userName") || storedUserEmail,
        department: localStorage.getItem("userDepartment") || "Unknown",
        type: storedUserType,
        reportsTo: localStorage.getItem("userReportsTo") || undefined,
        managerName: localStorage.getItem("userManagerName") || undefined,
        employeeId: localStorage.getItem("userEmployeeId") || undefined,
        position: localStorage.getItem("userPosition") || undefined,
        joinDate: localStorage.getItem("userJoinDate") || undefined,
      }
      setUserInfo(info)
      setLoading(false)
    }

    init()
  }, [router])

  return { userInfo, loading }
} 