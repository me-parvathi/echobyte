"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { fetchUserRoles } from "@/lib/role-utils"

interface UserInfo {
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

interface EmployeeResponse {
  EmployeeID: number
  FirstName: string
  LastName: string
  GenderCode: string
  ManagerID?: number
  TeamID: number
  LocationID: number
  DesignationID: number
  EmploymentTypeCode: string
  WorkModeCode: string
  HireDate: string
  TerminationDate?: string
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
  designation?: {
    DesignationID: number
    DesignationName: string
    IsActive: boolean
    CreatedAt: string
  }
  employment_type?: {
    EmploymentTypeCode: string
    EmploymentTypeName: string
    IsActive: boolean
    CreatedAt: string
  }
  work_mode?: {
    WorkModeCode: string
    WorkModeName: string
    IsActive: boolean
    CreatedAt: string
  }
  gender?: {
    GenderCode: string
    GenderName: string
    IsActive: boolean
    CreatedAt: string
  }
}

interface UseUserInfoReturn {
  userInfo: UserInfo | null
  loading: boolean
  error: string | null
  isFemale: boolean
  isManager: boolean
  isHR: boolean
  refetch: () => Promise<void>
}

export default function useUserInfo(): UseUserInfoReturn {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFemale, setIsFemale] = useState(false)
  const [isManager, setIsManager] = useState(false)
  const [isHR, setIsHR] = useState(false)

  const fetchUserInfo = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch employee profile and roles in parallel
      const [employeeResponse, { roles, userType }] = await Promise.all([
        api.get<EmployeeResponse>("/api/employees/profile/current"),
        fetchUserRoles()
      ])
      
      console.log("Employee response:", employeeResponse)
      console.log("User roles:", roles)
      console.log("User type:", userType)
      
      // Transform the response to match the expected UserInfo interface
      const transformedUserInfo: UserInfo = {
        email: `${employeeResponse.FirstName.toLowerCase()}.${employeeResponse.LastName.toLowerCase()}@company.com`,
        name: `${employeeResponse.FirstName} ${employeeResponse.LastName}`,
        department: employeeResponse.designation?.DesignationName || "Unknown",
        type: userType,
        employeeId: employeeResponse.EmployeeID.toString(),
        position: employeeResponse.designation?.DesignationName || "Employee",
        joinDate: employeeResponse.HireDate,
        // We'll need to fetch manager name separately if needed
        managerName: undefined,
        reportsTo: undefined
      }
      
      setUserInfo(transformedUserInfo)
      
      // Determine user characteristics based on roles and gender
      setIsFemale(employeeResponse.GenderCode === 'F')
      setIsManager(userType === 'manager')
      setIsHR(userType === 'hr')
      
      console.log("User characteristics:", {
        isFemale: employeeResponse.GenderCode === 'F',
        isManager: userType === 'manager',
        isHR: userType === 'hr'
      })
      
    } catch (err: any) {
      console.error("❌ Failed to fetch user info:", err)
      setError(err.message || "Failed to fetch user information")
      
      // Set default values on error
      setIsFemale(false)
      setIsManager(false)
      setIsHR(false)
    } finally {
      setLoading(false)
    }
  }

  const refetch = async () => {
    await fetchUserInfo()
  }

  useEffect(() => {
    fetchUserInfo()
  }, [])

  return {
    userInfo,
    loading,
    error,
    isFemale,
    isManager,
    isHR,
    refetch
  }
} 