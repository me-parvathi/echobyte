"use client"

import { useState, useEffect, useRef } from "react"
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
  passwordChangedAt?: string
  emergencyContacts?: EmergencyContact[]
  // New comprehensive fields
  employeeCode?: string
  firstName?: string
  middleName?: string
  lastName?: string
  dateOfBirth?: string
  genderCode?: string
  genderName?: string
  maritalStatus?: string
  personalEmail?: string
  personalPhone?: string
  workPhone?: string
  address1?: string
  address2?: string
  city?: string
  state?: string
  country?: string
  postalCode?: string
  hireDate?: string
  terminationDate?: string
  employmentDuration?: number
  designation?: {
    designationId: number
    designationName: string
  }
  employmentType?: {
    employmentTypeCode: string
    employmentTypeName: string
  }
  workMode?: {
    workModeCode: string
    workModeName: string
  }
  team?: {
    teamId: number
    teamName: string
    teamCode: string
  }
  departmentInfo?: {
    departmentId: number
    departmentName: string
    departmentCode: string
  }
  location?: {
    locationId: number
    locationName: string
    city: string
    state: string
    country: string
  }
  manager?: {
    employeeId: number
    employeeCode: string
    name: string
    designation: string
  }
}

interface EmergencyContact {
  ContactID: number
  EmployeeID: number
  ContactName: string
  Relationship: string
  Phone1: string
  Phone2?: string
  Email?: string
  Address?: string
  IsPrimary: boolean
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
}

interface ComprehensiveEmployeeResponse {
  EmployeeID: number
  EmployeeCode: string
  UserID: string
  CompanyEmail: string
  FirstName: string
  MiddleName?: string
  LastName: string
  FullName: string
  DateOfBirth?: string
  GenderCode: string
  GenderName?: string
  MaritalStatus?: string
  PersonalEmail?: string
  PersonalPhone?: string
  WorkPhone?: string
  Address1?: string
  Address2?: string
  City?: string
  State?: string
  Country?: string
  PostalCode?: string
  HireDate: string
  TerminationDate?: string
  EmploymentDuration: number
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
  Designation?: {
    DesignationID: number
    DesignationName: string
  }
  EmploymentType?: {
    EmploymentTypeCode: string
    EmploymentTypeName: string
  }
  WorkMode?: {
    WorkModeCode: string
    WorkModeName: string
  }
  Team?: {
    TeamID: number
    TeamName: string
    TeamCode: string
  }
  Department?: {
    DepartmentID: number
    DepartmentName: string
    DepartmentCode: string
  }
  Location?: {
    LocationID: number
    LocationName: string
    City: string
    State: string
    Country: string
  }
  Manager?: {
    EmployeeID: number
    EmployeeCode: string
    Name: string
    Designation: string
  }
  EmergencyContacts: EmergencyContact[]
}

interface UseUserInfoReturn {
  userInfo: UserInfo | null
  loading: boolean
  error: string | null
  isFemale: boolean
  isManager: boolean
  isHR: boolean
  isIT: boolean
  refetch: () => Promise<void>
}

export default function useUserInfo(): UseUserInfoReturn {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFemale, setIsFemale] = useState(false)
  const [isManager, setIsManager] = useState(false)
  const [isHR, setIsHR] = useState(false)
  const [isIT, setIsIT] = useState(false)
  
  // Ref to track if component is mounted
  const isMountedRef = useRef(true)
  // Ref to track if we've already fetched user info
  const hasFetchedRef = useRef(false)

  const fetchUserInfo = async () => {
    // Don't fetch if already fetched or component is unmounted
    if (hasFetchedRef.current || !isMountedRef.current) {
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      // Check if we have basic auth data first
      const token = localStorage.getItem('access_token')
      const userEmail = localStorage.getItem('userEmail')
      const userType = localStorage.getItem('userType')

      if (!token || !userEmail || !userType) {
        console.log('No auth data available, skipping user info fetch')
        setLoading(false)
        return
      }

      console.log('Fetching comprehensive user info...')
      
      // Fetch comprehensive employee profile, roles, and user auth data
      const [employeeResponse, { roles, userType: fetchedUserType }, userAuthData] = await Promise.all([
        api.get<ComprehensiveEmployeeResponse>("/api/employees/profile/current/comprehensive"),
        fetchUserRoles(),
        api.get<any>("/api/auth/me")
      ])
      
      // Check if component is still mounted before updating state
      if (!isMountedRef.current) {
        return
      }
      
      console.log("Comprehensive employee response:", employeeResponse)
      console.log("User roles:", roles)
      console.log("User type:", fetchedUserType)
      console.log("User auth data:", userAuthData)
      
      // Transform the response to match the expected UserInfo interface
      const transformedUserInfo: UserInfo = {
        email: employeeResponse.CompanyEmail,
        name: employeeResponse.FullName,
        department: employeeResponse.Department?.DepartmentName || "Unknown",
        type: fetchedUserType,
        employeeId: employeeResponse.EmployeeID.toString(),
        employeeCode: employeeResponse.EmployeeCode,
        position: employeeResponse.Designation?.DesignationName || "Employee",
        joinDate: employeeResponse.HireDate,
        passwordChangedAt: userAuthData.PasswordChangedAt,
        emergencyContacts: employeeResponse.EmergencyContacts,
        // Personal information
        firstName: employeeResponse.FirstName,
        middleName: employeeResponse.MiddleName,
        lastName: employeeResponse.LastName,
        dateOfBirth: employeeResponse.DateOfBirth,
        genderCode: employeeResponse.GenderCode,
        genderName: employeeResponse.GenderName,
        maritalStatus: employeeResponse.MaritalStatus,
        personalEmail: employeeResponse.PersonalEmail,
        personalPhone: employeeResponse.PersonalPhone,
        workPhone: employeeResponse.WorkPhone,
        // Address information
        address1: employeeResponse.Address1,
        address2: employeeResponse.Address2,
        city: employeeResponse.City,
        state: employeeResponse.State,
        country: employeeResponse.Country,
        postalCode: employeeResponse.PostalCode,
        // Work information
        hireDate: employeeResponse.HireDate,
        terminationDate: employeeResponse.TerminationDate,
        employmentDuration: employeeResponse.EmploymentDuration,
        designation: employeeResponse.Designation ? {
          designationId: employeeResponse.Designation.DesignationID,
          designationName: employeeResponse.Designation.DesignationName
        } : undefined,
        employmentType: employeeResponse.EmploymentType ? {
          employmentTypeCode: employeeResponse.EmploymentType.EmploymentTypeCode,
          employmentTypeName: employeeResponse.EmploymentType.EmploymentTypeName
        } : undefined,
        workMode: employeeResponse.WorkMode ? {
          workModeCode: employeeResponse.WorkMode.WorkModeCode,
          workModeName: employeeResponse.WorkMode.WorkModeName
        } : undefined,
        team: employeeResponse.Team ? {
          teamId: employeeResponse.Team.TeamID,
          teamName: employeeResponse.Team.TeamName,
          teamCode: employeeResponse.Team.TeamCode
        } : undefined,
        departmentInfo: employeeResponse.Department ? {
          departmentId: employeeResponse.Department.DepartmentID,
          departmentName: employeeResponse.Department.DepartmentName,
          departmentCode: employeeResponse.Department.DepartmentCode
        } : undefined,
        location: employeeResponse.Location ? {
          locationId: employeeResponse.Location.LocationID,
          locationName: employeeResponse.Location.LocationName,
          city: employeeResponse.Location.City,
          state: employeeResponse.Location.State,
          country: employeeResponse.Location.Country
        } : undefined,
        manager: employeeResponse.Manager ? {
          employeeId: employeeResponse.Manager.EmployeeID,
          employeeCode: employeeResponse.Manager.EmployeeCode,
          name: employeeResponse.Manager.Name,
          designation: employeeResponse.Manager.Designation
        } : undefined,
        // Legacy fields for backward compatibility
        managerName: employeeResponse.Manager?.Name,
        reportsTo: employeeResponse.Manager?.Name
      }
      
      setUserInfo(transformedUserInfo)
      
      // Determine user characteristics based on roles and gender
      setIsFemale(employeeResponse.GenderCode === 'F')
      setIsManager(fetchedUserType === 'manager')
      setIsHR(fetchedUserType === 'hr')
      setIsIT(fetchedUserType === 'it')
      
      console.log("User characteristics:", {
        isFemale: employeeResponse.GenderCode === 'F',
        isManager: fetchedUserType === 'manager',
        isHR: fetchedUserType === 'hr',
        isIT: fetchedUserType === 'it'
      })
      
      // Mark as fetched
      hasFetchedRef.current = true
      
    } catch (err: any) {
      if (!isMountedRef.current) {
        return
      }
      
      console.error("❌ Failed to fetch user info:", err)
      setError(err.message || "Failed to fetch user information")
      
      // Set default values on error
      setIsFemale(false)
      setIsManager(false)
      setIsHR(false)
      setIsIT(false)
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
      }
    }
  }

  const refetch = async () => {
    hasFetchedRef.current = false
    await fetchUserInfo()
  }

  useEffect(() => {
    isMountedRef.current = true
    fetchUserInfo()
    
    return () => {
      isMountedRef.current = false
    }
  }, [])

  return {
    userInfo,
    loading,
    error,
    isFemale,
    isManager,
    isHR,
    isIT,
    refetch
  }
} 