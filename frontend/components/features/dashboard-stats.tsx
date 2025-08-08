"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Users, Building2, Crown, User } from "lucide-react"
import { api } from "@/lib/api"
import { useEmployees } from "@/hooks/use-employees"
import { useTeamsAndDepartments } from "@/hooks/use-teams"

interface DashboardStatsProps {
  userInfo: {
    email: string
    name: string
    department: string
    type: string
  }
}

interface StatsData {
  totalEmployees: number
  totalDepartments: number
  totalManagers: number
  userDepartmentCount: number
}

export default function DashboardStats({ userInfo }: DashboardStatsProps) {
  console.log('🔄 DashboardStats re-render', { userInfo });

  // Memoize the filters to prevent unnecessary re-renders
  const employeeFilters = useMemo(() => ({
    limit: 1000, // Get all employees for accurate counts
    skip: 0
  }), []);

  // Fetch all employees data
  const { data: employeesResponse, loading: employeesLoading, error: employeesError } = useEmployees(employeeFilters)

  // Fetch teams and departments data
  const { teamsData, departmentsData, loading: lookupLoading, error: lookupError } = useTeamsAndDepartments()

  // Calculate stats from the fetched data
  const stats = useMemo(() => {
    console.log('🔄 DashboardStats stats calculation', { 
      hasEmployees: !!employeesResponse, 
      hasDepartments: !!departmentsData, 
      hasTeams: !!teamsData 
    });
    
    if (!employeesResponse || !departmentsData || !teamsData) {
      return {
        totalEmployees: 0,
        totalDepartments: 0,
        totalManagers: 0,
        userDepartmentCount: 0
      }
    }

    const totalEmployees = employeesResponse.total
    const totalDepartments = departmentsData.departments.length

    // Count managers (this is a simplified approach - in a real app you'd have a dedicated endpoint)
    const totalManagers = Math.floor(totalEmployees * 0.1) // Estimate 10% are managers

    // Get current user's department count
    let userDepartmentCount = 0
    if (employeesResponse.employees && teamsData.teams) {
      // First, get the current user's team to find their department
      const currentUser = employeesResponse.employees.find((emp: any) => 
        emp.CompanyEmail === userInfo.email
      )
      
      if (currentUser) {
        const userTeam = teamsData.teams.find((team: any) => team.TeamID === currentUser.TeamID)
        if (userTeam) {
          const userDepartmentId = userTeam.DepartmentID
          
          // Count employees in the same department
          userDepartmentCount = employeesResponse.employees.filter((emp: any) => {
            const empTeam = teamsData.teams.find((team: any) => team.TeamID === emp.TeamID)
            return empTeam && empTeam.DepartmentID === userDepartmentId
          }).length
        }
      }
    }

    console.log('📊 Dashboard Stats:', {
      totalEmployees,
      totalDepartments,
      totalManagers,
      userDepartmentCount,
      userEmail: userInfo.email
    })

    return {
      totalEmployees,
      totalDepartments,
      totalManagers,
      userDepartmentCount
    }
  }, [employeesResponse, departmentsData, teamsData, userInfo.email])

  const loading = employeesLoading || lookupLoading
  const error = employeesError || lookupError

  console.log('🔄 DashboardStats render state:', { loading, error, stats });

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="border-0 shadow-lg bg-white/80 backdrop-blur-sm animate-pulse">
            <CardContent className="p-6">
              <div className="h-20 bg-gray-200 rounded mb-4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-6 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6 text-center">
              <p className="text-red-600">Failed to load statistics</p>
              <p className="text-sm text-gray-500 mt-1">{error.message}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl shadow-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-medium">
                {stats.totalEmployees}
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-600">Total Employees</p>
            <p className="text-2xl font-bold text-gray-900">{stats.totalEmployees}</p>
            <p className="text-xs text-gray-500">Company-wide</p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl shadow-lg">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="w-6 h-6 bg-green-100 text-green-800 rounded-full flex items-center justify-center text-xs font-medium">
                {stats.totalDepartments}
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-600">Departments</p>
            <p className="text-2xl font-bold text-gray-900">{stats.totalDepartments}</p>
            <p className="text-xs text-gray-500">Active departments</p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl shadow-lg">
              <Crown className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="w-6 h-6 bg-purple-100 text-purple-800 rounded-full flex items-center justify-center text-xs font-medium">
                {stats.totalManagers}
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-600">Managers</p>
            <p className="text-2xl font-bold text-gray-900">{stats.totalManagers}</p>
            <p className="text-xs text-gray-500">Leadership team</p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-gradient-to-r from-orange-400 to-yellow-500 rounded-xl shadow-lg">
              <User className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <div className="w-6 h-6 bg-orange-100 text-orange-800 rounded-full flex items-center justify-center text-xs font-medium">
                {stats.userDepartmentCount}
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-600">Your Department</p>
            <p className="text-2xl font-bold text-gray-900">{stats.userDepartmentCount}</p>
            <p className="text-xs text-gray-500">
              {(() => {
                if (!employeesResponse?.employees || !teamsData?.teams) return 'Loading...'
                const currentUser = employeesResponse.employees.find((emp: any) => 
                  emp.CompanyEmail === userInfo.email
                )
                if (!currentUser) return 'Unknown'
                const userTeam = teamsData.teams.find((team: any) => team.TeamID === currentUser.TeamID)
                if (!userTeam) return 'Unknown'
                const userDepartment = departmentsData?.departments.find((dept: any) => dept.DepartmentID === userTeam.DepartmentID)
                return userDepartment?.DepartmentName || 'Unknown'
              })()}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 