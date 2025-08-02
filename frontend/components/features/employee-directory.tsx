"use client"

import { useState, useMemo, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Users, Mail, Phone, MapPin, Building2, Calendar, Filter, Crown, User, Briefcase } from "lucide-react"
import { useEmployees } from "@/hooks/use-employees"
import { useTeamsAndDepartments } from "@/hooks/use-teams"
import { transformEmployeesToFrontend, filterEmployeesBySearch, filterEmployeesByDepartment, filterEmployeesByRole, getInitials, getRoleIcon, getRoleColor, getStatusColor, formatJoinDate, createLookupMaps } from "@/lib/employee-utils"
import { EmployeeWithDetails } from "@/lib/types"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
}

interface EmployeeDirectoryProps {
  userInfo: UserInfo
}

export default function EmployeeDirectory({ userInfo }: EmployeeDirectoryProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [departmentFilter, setDepartmentFilter] = useState("all")
  const [roleFilter, setRoleFilter] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(50) // Load 50 employees per page

  // Calculate skip for pagination
  const skip = (currentPage - 1) * pageSize

  // Fetch employees data with pagination and filters
  const { data: employeesResponse, loading, error } = useEmployees({
    limit: pageSize,
    skip: skip,
    search: searchTerm || undefined,
    department_id: departmentFilter !== 'all' ? parseInt(departmentFilter) : undefined
  })

  // Fetch teams and departments data for lookups
  const { teamsData, departmentsData, loading: lookupLoading, error: lookupError } = useTeamsAndDepartments()

  // State for user's department count
  const [userDepartmentCount, setUserDepartmentCount] = useState(0)
  const [userDepartmentName, setUserDepartmentName] = useState('Loading...')

  // Create lookup maps
  const { teamLookup, departmentLookup } = useMemo(() => {
    if (!teamsData?.teams || !departmentsData?.departments) {
      return { teamLookup: undefined, departmentLookup: undefined }
    }
    return createLookupMaps(teamsData.teams, departmentsData.departments)
  }, [teamsData, departmentsData])

  // Transform employees to frontend format
  const employees = useMemo(() => {
    if (!employeesResponse?.employees) return []
    return transformEmployeesToFrontend(employeesResponse.employees, teamLookup, departmentLookup)
  }, [employeesResponse, teamLookup, departmentLookup])

  // Get unique departments and roles for filters
  const departments = useMemo(() => {
    const deptSet = new Set(employees.map(emp => emp.departmentName).filter(Boolean))
    return Array.from(deptSet).sort()
  }, [employees])

  const roles = useMemo(() => {
    const roleSet = new Set(employees.map(emp => emp.role))
    return Array.from(roleSet).sort()
  }, [employees])

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, departmentFilter, pageSize])

  // Fetch user's department count
  useEffect(() => {
    const fetchUserDepartmentCount = async () => {
      if (!employeesResponse?.employees || !teamsData?.teams || !departmentsData?.departments) return

      try {
        // Find current user
        const currentUser = employeesResponse.employees.find((emp: any) => 
          emp.CompanyEmail === userInfo.email
        )
        
        if (!currentUser) {
          console.log('❌ Current user not found in employees list')
          return
        }

        // Find user's team
        const userTeam = teamsData.teams.find((team: any) => team.TeamID === currentUser.TeamID)
        if (!userTeam) {
          console.log('❌ User team not found')
          return
        }

        const userDepartmentId = userTeam.DepartmentID
        console.log('🔍 User department ID:', userDepartmentId)

        // Find user's department name
        const userDepartment = departmentsData.departments.find((dept: any) => dept.DepartmentID === userDepartmentId)
        if (userDepartment) {
          setUserDepartmentName(userDepartment.DepartmentName)
        }

        // Get all teams in the user's department
        const departmentTeams = teamsData.teams.filter((team: any) => team.DepartmentID === userDepartmentId)
        console.log('🔍 Teams in user department:', departmentTeams.length)

        // Count all employees in all teams of the user's department
        let count = 0
        for (const team of departmentTeams) {
          try {
            const teamEmployeesResponse = await api.get(`/employees/?team_id=${team.TeamID}&limit=1000`)
            count += teamEmployeesResponse.total
            console.log(`🔍 Team ${team.TeamName}: ${teamEmployeesResponse.total} employees`)
          } catch (err) {
            console.warn(`Could not fetch employees for team ${team.TeamID}:`, err)
          }
        }

        console.log('📊 Total employees in user department:', count)
        setUserDepartmentCount(count)
      } catch (err) {
        console.error('Error fetching user department count:', err)
      }
    }

    fetchUserDepartmentCount()
  }, [employeesResponse, teamsData, departmentsData, userInfo.email])

  // Filter employees based on role filter (backend handles search and department)
  const filteredEmployees = useMemo(() => {
    let filtered = employees

    // Apply role filter (frontend only since backend doesn't support role filtering)
    if (roleFilter !== 'all') {
      filtered = filterEmployeesByRole(filtered, roleFilter)
    }

    return filtered
  }, [employees, roleFilter])

  // Loading state
  if (loading || lookupLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Employee Directory
          </h2>
          <p className="text-gray-600">Loading employee directory...</p>
        </div>
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
      </div>
    )
  }

  // Error state
  if (error || lookupError) {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Employee Directory
          </h2>
          <p className="text-red-600">Error loading employee directory. Please try again later.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
          Employee Directory
        </h2>
        <p className="text-gray-600">Find colleagues and explore organizational structure</p>
      </div>

      {/* Directory Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl shadow-lg">
                <Users className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-blue-100 text-blue-800">{employeesResponse?.total || 0}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900">{employeesResponse?.total || 0}</p>
              <p className="text-xs text-gray-500">Company-wide</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-xl shadow-lg">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-emerald-100 text-emerald-800">{departmentsData?.departments?.length || 0}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Departments</p>
              <p className="text-2xl font-bold text-gray-900">{departmentsData?.departments?.length || 0}</p>
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
              <Badge className="bg-purple-100 text-purple-800">
                {Math.floor((employeesResponse?.total || 0) * 0.1)}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Managers</p>
              <p className="text-2xl font-bold text-gray-900">{Math.floor((employeesResponse?.total || 0) * 0.1)}</p>
              <p className="text-xs text-gray-500">Leadership team</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-orange-400 to-amber-500 rounded-xl shadow-lg">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-orange-100 text-orange-800">
                {userDepartmentCount}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Your Department</p>
              <p className="text-2xl font-bold text-gray-900">
                {userDepartmentCount}
              </p>
              <p className="text-xs text-gray-500">
                {userDepartmentName}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Summary Stats */}
      {employeesResponse && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Employees</p>
                  <p className="text-2xl font-bold text-gray-900">{employeesResponse.total}</p>
                </div>
                <Users className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Current Page</p>
                  <p className="text-2xl font-bold text-gray-900">{currentPage}</p>
                </div>
                <Building2 className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Page Size</p>
                  <p className="text-2xl font-bold text-gray-900">{pageSize}</p>
                </div>
                <Crown className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Showing</p>
                  <p className="text-2xl font-bold text-gray-900">{filteredEmployees.length}</p>
                </div>
                <User className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search employees..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-11"
              />
            </div>

            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Departments" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                {departments.map((dept) => (
                  <SelectItem key={dept} value={dept}>
                    {dept} ({employees.filter((e) => e.departmentName === dept).length})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Roles" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="employee">Employees</SelectItem>
                <SelectItem value="manager">Managers</SelectItem>
                <SelectItem value="hr">HR</SelectItem>
                <SelectItem value="it">IT</SelectItem>
              </SelectContent>
            </Select>

            <Select value={pageSize.toString()} onValueChange={(value) => setPageSize(parseInt(value))}>
              <SelectTrigger className="h-11 w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="25">25/page</SelectItem>
                <SelectItem value="50">50/page</SelectItem>
                <SelectItem value="100">100/page</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" className="h-11 bg-transparent">
              <Filter className="w-4 h-4 mr-2" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Employee Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEmployees.map((employee) => (
          <Card
            key={employee.EmployeeID}
            className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer group bg-white/80 backdrop-blur-sm hover:scale-105 ${
              employee.CompanyEmail === userInfo.email ? "ring-2 ring-orange-300" : ""
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-start gap-4 mb-4">
                <Avatar className="w-16 h-16 ring-2 ring-white shadow-lg">
                  <AvatarFallback
                    className={`bg-gradient-to-r ${getRoleColor(employee.role)} text-white font-medium text-lg`}
                  >
                    {employee.initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {employee.fullName}
                      {employee.CompanyEmail === userInfo.email && <span className="text-orange-600 ml-1">(You)</span>}
                    </h3>
                    <div className="flex items-center gap-1">
                      <span className="text-lg">{getRoleIcon(employee.role)}</span>
                      <Badge className={getStatusColor(employee.status)} variant="secondary">
                        {employee.status}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{employee.designation?.DesignationName}</p>
                  <Badge variant="outline" className="text-xs bg-orange-50 border-orange-200">
                    {employee.departmentName || 'Department'}
                  </Badge>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="truncate">{employee.CompanyEmail}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span>{employee.WorkPhone || employee.PersonalPhone || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span>{employee.City}, {employee.State}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <User className="w-4 h-4 text-gray-400" />
                  <span>Reports to: {employee.managerName || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>Joined {formatJoinDate(employee.HireDate)}</span>
                </div>
              </div>

              {/* Skills */}
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-500 mb-2">Skills</p>
                <div className="flex flex-wrap gap-1">
                  {employee.skills?.slice(0, 3).map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs bg-gray-100">
                      {skill}
                    </Badge>
                  ))}
                  {employee.skills && employee.skills.length > 3 && (
                    <Badge variant="secondary" className="text-xs bg-gray-100">
                      +{employee.skills.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                  <Mail className="w-4 h-4 mr-1" />
                  Contact
                </Button>
                <Button size="sm" variant="outline" className="bg-transparent">
                  <User className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEmployees.length === 0 && (
        <Card className="border-0 shadow-sm bg-white/80 backdrop-blur-sm">
          <CardContent className="p-12 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No employees found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters</p>
          </CardContent>
        </Card>
      )}

      {/* Pagination Controls */}
      {employeesResponse && employeesResponse.total > pageSize && (
        <div className="flex items-center justify-between mt-8">
          <div className="text-sm text-gray-600">
            Showing {skip + 1} to {Math.min(skip + pageSize, employeesResponse.total)} of {employeesResponse.total} employees
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, Math.ceil(employeesResponse.total / pageSize)) }, (_, i) => {
                const page = i + 1;
                return (
                  <Button
                    key={page}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(page)}
                    className="w-8 h-8 p-0"
                  >
                    {page}
                  </Button>
                );
              })}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= Math.ceil(employeesResponse.total / pageSize)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
