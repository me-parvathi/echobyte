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

// Move large data outside component to prevent recreation
const ALL_EMPLOYEES = [
  {
    id: "CEO001",
    name: "Robert CEO",
    position: "Chief Executive Officer",
    email: "ceo@company.com",
    phone: "+1 (555) 000-0001",
    department: "Executive",
    role: "ceo",
    joinDate: "2018-01-01",
    location: "New York, NY",
    reportsTo: null,
    managerName: null,
    status: "active",
    avatar: null,
  },
  {
    id: "CTO001",
    name: "David CTO",
    position: "Chief Technology Officer",
    email: "cto@company.com",
    phone: "+1 (555) 000-0002",
    department: "Technology",
    role: "cto",
    joinDate: "2018-06-01",
    location: "San Francisco, CA",
    reportsTo: "ceo@company.com",
    managerName: "Robert CEO",
    status: "active",
    avatar: null,
  },
  {
    id: "MGR001",
    name: "Jane Smith",
    position: "Engineering Manager",
    email: "jane.manager@company.com",
    phone: "+1 (555) 456-7890",
    department: "Engineering",
    role: "manager",
    joinDate: "2020-01-10",
    location: "New York, NY",
    reportsTo: "cto@company.com",
    managerName: "David CTO",
    status: "active",
    avatar: null,
  },
  {
    id: "HR001",
    name: "Sarah Johnson",
    position: "HR Director",
    email: "hr.admin@company.com",
    phone: "+1 (555) 789-0123",
    department: "Human Resources",
    role: "hr",
    joinDate: "2019-06-20",
    location: "Chicago, IL",
    reportsTo: "ceo@company.com",
    managerName: "Robert CEO",
    status: "active",
    avatar: null,
  },
  {
    id: "IT001",
    name: "Mike Wilson",
    position: "IT Manager",
    email: "it.support@company.com",
    phone: "+1 (555) 234-5678",
    department: "IT Support",
    role: "it",
    joinDate: "2021-08-05",
    location: "Austin, TX",
    reportsTo: "cto@company.com",
    managerName: "David CTO",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP001",
    name: "John Doe",
    position: "Senior Software Engineer",
    email: "john.doe@company.com",
    phone: "+1 (555) 123-4567",
    department: "Engineering",
    role: "employee",
    joinDate: "2022-03-15",
    location: "New York, NY",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP002",
    name: "Alice Johnson",
    position: "Frontend Developer",
    email: "alice.johnson@company.com",
    phone: "+1 (555) 234-5678",
    department: "Engineering",
    role: "employee",
    joinDate: "2022-06-20",
    location: "Remote",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP003",
    name: "Bob Wilson",
    position: "Backend Developer",
    email: "bob.wilson@company.com",
    phone: "+1 (555) 345-6789",
    department: "Engineering",
    role: "employee",
    joinDate: "2022-09-10",
    location: "San Francisco, CA",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP004",
    name: "Carol Brown",
    position: "UX Designer",
    email: "carol.brown@company.com",
    phone: "+1 (555) 456-7890",
    department: "Design",
    role: "employee",
    joinDate: "2022-11-05",
    location: "Chicago, IL",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP005",
    name: "David Lee",
    position: "QA Engineer",
    email: "david.lee@company.com",
    phone: "+1 (555) 567-8901",
    department: "Engineering",
    role: "employee",
    joinDate: "2023-01-15",
    location: "Remote",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP006",
    name: "Eva Garcia",
    position: "DevOps Engineer",
    email: "eva.garcia@company.com",
    phone: "+1 (555) 678-9012",
    department: "Engineering",
    role: "employee",
    joinDate: "2023-03-20",
    location: "Austin, TX",
    reportsTo: "jane.manager@company.com",
    managerName: "Jane Smith",
    status: "active",
    avatar: null,
  },
  {
    id: "EMP007",
    name: "Tom Rodriguez",
    position: "Network Engineer",
    email: "tom.rodriguez@company.com",
    phone: "+1 (555) 901-2345",
    department: "IT Support",
    role: "employee",
    joinDate: "2023-04-18",
    location: "Denver, CO",
    reportsTo: "it.support@company.com",
    managerName: "Mike Wilson",
    status: "active",
    avatar: null,
  },
]

export default function TeamInfo({ userInfo }: TeamInfoProps) {
  // Memoize expensive calculations
  const teamData = useMemo(() => {
    const manager = ALL_EMPLOYEES.find((emp) => emp.email === userInfo.reportsTo)
    const directReports = ALL_EMPLOYEES.filter((emp) => emp.reportsTo === userInfo.email)
    const departmentTeam = ALL_EMPLOYEES.filter((emp) => emp.department === userInfo.department)
    const peers = ALL_EMPLOYEES.filter((emp) => emp.reportsTo === userInfo.reportsTo && emp.email !== userInfo.email)
    
    // Get reporting chain
    const getReportingChain = (email: string): any[] => {
      const chain = []
      let currentEmployee = ALL_EMPLOYEES.find((emp) => emp.email === email)
      
      while (currentEmployee && currentEmployee.reportsTo) {
        const manager = ALL_EMPLOYEES.find((emp) => emp.email === currentEmployee.reportsTo)
        if (manager) {
          chain.push(manager)
          currentEmployee = manager
        } else {
          break
        }
      }
      return chain
    }
    
    const reportingChain = getReportingChain(userInfo.email)
    
    return {
      manager,
      directReports,
      departmentTeam,
      peers,
      reportingChain
    }
  }, [userInfo.email, userInfo.reportsTo, userInfo.department])

  const getInitials = useCallback((name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }, [])

  const formatJoinDate = useCallback((dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    })
  }, [])

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "away":
        return "bg-yellow-100 text-yellow-800"
      case "offline":
        return "bg-gray-100 text-gray-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }, [])

  const getRoleColor = useCallback((role: string) => {
    switch (role) {
      case "ceo":
        return "from-red-500 to-rose-500"
      case "cto":
        return "from-indigo-500 to-blue-500"
      case "manager":
        return "from-emerald-500 to-teal-500"
      case "hr":
        return "from-purple-500 to-pink-500"
      case "it":
        return "from-blue-500 to-cyan-500"
      default:
        return "from-orange-500 to-amber-500"
    }
  }, [])

  const { manager, directReports, departmentTeam, peers, reportingChain } = teamData

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
              <p className="text-xs text-gray-500">In {userInfo.department}</p>
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
                  key={person.id}
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
                        {getInitials(person.name)}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900">{person.name}</h4>
                      <Badge className={getStatusColor(person.status)}>{person.status}</Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{person.position}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {person.email}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {person.location}
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
                  {getInitials(manager.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">{manager.name}</h3>
                  <Badge className={getStatusColor(manager.status)}>{manager.status}</Badge>
                </div>
                <p className="text-gray-600 mb-3">{manager.position}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.phone}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{manager.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Since {formatJoinDate(manager.joinDate)}</span>
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
                  key={member.id}
                  className="flex items-start gap-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200/50 hover:shadow-md transition-all duration-200"
                >
                  <Avatar className="w-12 h-12 ring-2 ring-purple-200 shadow-md">
                    <AvatarFallback className={`bg-gradient-to-r ${getRoleColor(member.role)} text-white font-medium`}>
                      {getInitials(member.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 truncate">{member.name}</h4>
                      <Badge className={getStatusColor(member.status)} variant="secondary">
                        {member.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{member.position}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {member.email.split("@")[0]}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(member.joinDate).getFullYear()}
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
                  key={peer.id}
                  className="p-4 rounded-xl border bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200/50 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-start gap-3">
                    <Avatar className="w-10 h-10 ring-2 ring-blue-200 shadow-md">
                      <AvatarFallback
                        className={`bg-gradient-to-r ${getRoleColor(peer.role)} text-white font-medium text-sm`}
                      >
                        {getInitials(peer.name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-gray-900 truncate text-sm">{peer.name}</h4>
                        <Badge className={getStatusColor(peer.status)} variant="secondary">
                          {peer.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{peer.position}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3 h-3" />
                          <span>{peer.department}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          <span>{peer.location.split(",")[0]}</span>
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
            {userInfo.department} Team ({departmentTeam.length})
          </CardTitle>
          <CardDescription>All members of your department</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departmentTeam.map((member) => (
              <div
                key={member.id}
                className={`p-4 rounded-xl border transition-all duration-200 hover:shadow-md ${
                  member.email === userInfo.email
                    ? "bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200/50 ring-2 ring-orange-300"
                    : "bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200/50"
                }`}
              >
                <div className="flex items-start gap-3">
                  <Avatar className="w-10 h-10 ring-2 ring-white shadow-md">
                    <AvatarFallback
                      className={`font-medium text-white text-sm ${
                        member.email === userInfo.email
                          ? "bg-gradient-to-r from-orange-500 to-amber-500"
                          : `bg-gradient-to-r ${getRoleColor(member.role)}`
                      }`}
                    >
                      {getInitials(member.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-gray-900 truncate text-sm">
                        {member.name}
                        {member.email === userInfo.email && <span className="text-orange-600 ml-1">(You)</span>}
                      </h4>
                      <Badge className={getStatusColor(member.status)} variant="secondary">
                        {member.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{member.position}</p>
                    <div className="space-y-1 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        <span>{member.id}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        <span>{member.location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>Joined {new Date(member.joinDate).getFullYear()}</span>
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
