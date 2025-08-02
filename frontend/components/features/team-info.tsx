"use client"
import { useMemo, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Users,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Building2,
  Crown,
  UserCheck,
  Clock,
  MessageSquare,
  Video,
} from "lucide-react"
import { useCurrentEmployee, useManagerTeamOverview, useCurrentEmployeeHierarchy } from "@/hooks/use-employees"
import { useTeamsAndDepartments } from "@/hooks/use-teams"
import { transformEmployeeToFrontend, getInitials, formatJoinDate, getStatusColor, getRoleColor, createLookupMaps } from "@/lib/employee-utils"
import { EmployeeWithDetails } from "@/lib/types"

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

interface TeamInfoProps {
  userInfo: UserInfo
}

export default function TeamInfo({ userInfo }: TeamInfoProps) {
  // Fetch current employee data
  const { data: currentEmployee, loading: currentEmployeeLoading, error: currentEmployeeError } = useCurrentEmployee()
  
  // Fetch team overview data for managers
  const { data: teamOverview, loading: teamOverviewLoading, error: teamOverviewError } = useManagerTeamOverview({
    immediate: userInfo.type === 'manager' || userInfo.type === 'hr'
  })

  // Fetch current employee hierarchy (reporting chain)
  const { data: hierarchyData, loading: hierarchyLoading, error: hierarchyError } = useCurrentEmployeeHierarchy({
    immediate: true
  })

  // Fetch teams and departments data for lookups
  const { teamsData, departmentsData, loading: lookupLoading, error: lookupError } = useTeamsAndDepartments()

  // Create lookup maps
  const { teamLookup, departmentLookup } = useMemo(() => {
    if (!teamsData?.teams || !departmentsData?.departments) {
      return { teamLookup: undefined, departmentLookup: undefined }
    }
    return createLookupMaps(teamsData.teams, departmentsData.departments)
  }, [teamsData, departmentsData])

  // Debug logging
  console.log('🔍 TeamInfo Debug:', {
    userInfoType: userInfo.type,
    shouldFetchTeamOverview: userInfo.type === 'manager' || userInfo.type === 'hr',
    currentEmployee,
    teamOverview,
    hierarchyData,
    teamLookup: teamLookup ? 'Available' : 'Not available',
    departmentLookup: departmentLookup ? 'Available' : 'Not available'
  })

  // Transform current employee to frontend format
  const currentEmployeeWithDetails = useMemo(() => {
    if (!currentEmployee) return null
    return transformEmployeeToFrontend(currentEmployee, teamLookup, departmentLookup)
  }, [currentEmployee, teamLookup, departmentLookup])

  // Transform team data to frontend format
  const teamData = useMemo(() => {
    if (!teamOverview || !currentEmployeeWithDetails) {
      return {
        manager: null,
        directReports: [],
        departmentTeam: [],
        peers: [],
        reportingChain: []
      }
    }

    const manager = teamOverview.manager ? transformEmployeeToFrontend(teamOverview.manager, teamLookup, departmentLookup) : null
    const directReports = teamOverview.subordinates.map(emp => transformEmployeeToFrontend(emp, teamLookup, departmentLookup))
    const departmentTeam = [currentEmployeeWithDetails, ...directReports]
    const peers: EmployeeWithDetails[] = [] // This would need additional API call to get peers
    
    // Use hierarchy data for reporting chain (managers above current employee)
    const reportingChain = hierarchyData ? hierarchyData.map(emp => transformEmployeeToFrontend(emp, teamLookup, departmentLookup)) : []

    return {
      manager,
      directReports,
      departmentTeam,
      peers,
      reportingChain
    }
  }, [teamOverview, currentEmployeeWithDetails, teamLookup, departmentLookup])

  const { manager, directReports, departmentTeam, peers, reportingChain } = teamData

  // Loading state
  if (currentEmployeeLoading || teamOverviewLoading || hierarchyLoading || lookupLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Team & Reporting Structure
          </h2>
          <p className="text-gray-600">Loading team information...</p>
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
  if (currentEmployeeError || teamOverviewError || hierarchyError || lookupError) {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Team & Reporting Structure
          </h2>
          <p className="text-red-600">Error loading team information. Please try again later.</p>
          {(currentEmployeeError || teamOverviewError || hierarchyError || lookupError) && (
            <p className="text-sm text-gray-500 mt-2">
              {currentEmployeeError && `Employee: ${currentEmployeeError.message}`}
              {teamOverviewError && `Team Overview: ${teamOverviewError.message}`}
              {hierarchyError && `Hierarchy: ${hierarchyError.message}`}
              {lookupError && `Lookup: ${lookupError.message}`}
            </p>
          )}
        </div>
      </div>
    )
  }

  // If no current employee data, show fallback
  if (!currentEmployeeWithDetails) {
    return (
      <div className="space-y-8">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Team & Reporting Structure
          </h2>
          <p className="text-gray-600">No employee data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
          Team & Reporting Structure
        </h2>
        <p className="text-gray-600">Your organizational relationships and team members</p>
      </div>

      {/* Team Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl shadow-lg">
                <Users className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-blue-100 text-blue-800">{departmentTeam.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Department Team</p>
              <p className="text-2xl font-bold text-gray-900">{departmentTeam.length}</p>
              <p className="text-xs text-gray-500">In {currentEmployeeWithDetails.departmentName || 'Department'}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-xl shadow-lg">
                <UserCheck className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-emerald-100 text-emerald-800">{directReports.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Direct Reports</p>
              <p className="text-2xl font-bold text-gray-900">{directReports.length}</p>
              <p className="text-xs text-gray-500">Report to you</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl shadow-lg">
                <Users className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-purple-100 text-purple-800">{peers.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Peers</p>
              <p className="text-2xl font-bold text-gray-900">{peers.length}</p>
              <p className="text-xs text-gray-500">Same manager</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-amber-400 to-orange-500 rounded-xl shadow-lg">
                <Crown className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-amber-100 text-amber-800">{reportingChain.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Reporting Chain</p>
              <p className="text-2xl font-bold text-gray-900">{reportingChain.length}</p>
              <p className="text-xs text-gray-500">Levels above</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reporting Chain */}
      {reportingChain.length > 0 && (
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="w-5 h-5 text-amber-600" />
              Reporting Chain
            </CardTitle>
            <CardDescription>Your management hierarchy</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {reportingChain.map((person, index) => (
                <div
                  key={person.EmployeeID}
                  className="flex items-center gap-4 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-200/50 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-sm font-medium text-amber-700 bg-amber-200 rounded-full w-6 h-6 flex items-center justify-center">
                      {index + 1}
                    </div>
                    <Avatar className="w-12 h-12 ring-2 ring-amber-200 shadow-md">
                      <AvatarFallback
                        className={`bg-gradient-to-r ${getRoleColor(person.role)} text-white font-medium`}
                      >
                        {person.initials}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900">{person.fullName}</h4>
                      <Badge className={getStatusColor(person.status)}>{person.status}</Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{person.designation?.DesignationName}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {person.CompanyEmail}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {person.City}, {person.State}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="bg-transparent">
                      <Mail className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="outline" className="bg-transparent">
                      <MessageSquare className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Direct Manager */}
      {manager && (
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="w-5 h-5 text-emerald-600" />
              Your Direct Manager
            </CardTitle>
            <CardDescription>Person you directly report to</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-start gap-4 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-200/50">
              <Avatar className="w-16 h-16 ring-2 ring-emerald-200 shadow-lg">
                <AvatarFallback
                  className={`bg-gradient-to-r ${getRoleColor(manager.role)} text-white font-medium text-lg`}
                >
                  {manager.initials}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">{manager.fullName}</h3>
                  <Badge className={getStatusColor(manager.status)}>{manager.status}</Badge>
                </div>
                <p className="text-gray-600 mb-3">{manager.designation?.DesignationName}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.CompanyEmail}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.WorkPhone || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.City}, {manager.State}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Since {formatJoinDate(manager.HireDate)}</span>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <Button size="sm" className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
                    <Mail className="w-4 h-4 mr-1" />
                    Email
                  </Button>
                  <Button size="sm" variant="outline" className="bg-transparent">
                    <MessageSquare className="w-4 h-4 mr-1" />
                    Chat
                  </Button>
                  <Button size="sm" variant="outline" className="bg-transparent">
                    <Video className="w-4 h-4 mr-1" />
                    Meet
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Direct Reports */}
      {directReports.length > 0 && (
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-purple-600" />
              Your Direct Reports ({directReports.length})
            </CardTitle>
            <CardDescription>Team members who report directly to you</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {directReports.map((member) => (
                <div
                  key={member.EmployeeID}
                  className="flex items-start gap-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200/50 hover:shadow-md transition-all duration-200"
                >
                  <Avatar className="w-12 h-12 ring-2 ring-purple-200 shadow-md">
                    <AvatarFallback className={`bg-gradient-to-r ${getRoleColor(member.role)} text-white font-medium`}>
                      {member.initials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 truncate">{member.fullName}</h4>
                      <Badge className={getStatusColor(member.status)} variant="secondary">
                        {member.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{member.designation?.DesignationName}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {member.CompanyEmail.split("@")[0]}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(member.HireDate).getFullYear()}
                      </span>
                    </div>
                    <div className="flex gap-1 mt-2">
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs bg-transparent">
                        <Mail className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs bg-transparent">
                        <MessageSquare className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Peers */}
      {peers.length > 0 && (
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Your Peers ({peers.length})
            </CardTitle>
            <CardDescription>Colleagues who report to the same manager</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {peers.map((peer) => (
                <div
                  key={peer.EmployeeID}
                  className="p-4 rounded-xl border bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200/50 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-start gap-3">
                    <Avatar className="w-10 h-10 ring-2 ring-blue-200 shadow-md">
                      <AvatarFallback
                        className={`bg-gradient-to-r ${getRoleColor(peer.role)} text-white font-medium text-sm`}
                      >
                        {peer.initials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-gray-900 truncate text-sm">{peer.fullName}</h4>
                        <Badge className={getStatusColor(peer.status)} variant="secondary">
                          {peer.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{peer.designation?.DesignationName}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3 h-3" />
                          <span>{peer.departmentName || 'Department'}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          <span>{peer.City}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Department Team */}
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5 text-orange-600" />
            {currentEmployeeWithDetails.departmentName || 'Department'} Team ({departmentTeam.length})
          </CardTitle>
          <CardDescription>All members of your department</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departmentTeam.map((member) => (
              <div
                key={member.EmployeeID}
                className={`p-4 rounded-xl border transition-all duration-200 hover:shadow-md ${
                  member.EmployeeID === currentEmployeeWithDetails.EmployeeID
                    ? "bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200/50 ring-2 ring-orange-300"
                    : "bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200/50"
                }`}
              >
                <div className="flex items-start gap-3">
                  <Avatar className="w-10 h-10 ring-2 ring-white shadow-md">
                    <AvatarFallback
                      className={`font-medium text-white text-sm ${
                        member.EmployeeID === currentEmployeeWithDetails.EmployeeID
                          ? "bg-gradient-to-r from-orange-500 to-amber-500"
                          : `bg-gradient-to-r ${getRoleColor(member.role)}`
                      }`}
                    >
                      {member.initials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 truncate text-sm">
                        {member.fullName}
                        {member.EmployeeID === currentEmployeeWithDetails.EmployeeID && <span className="text-orange-600 ml-1">(You)</span>}
                      </h4>
                      <Badge className={getStatusColor(member.status)} variant="secondary">
                        {member.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{member.designation?.DesignationName}</p>
                    <div className="space-y-1 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        <span>{member.EmployeeCode}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        <span>{member.City}, {member.State}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>Joined {new Date(member.HireDate).getFullYear()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
