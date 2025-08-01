"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Users, Mail, Phone, MapPin, Building2, Calendar, Filter, Crown, User, Briefcase } from "lucide-react"

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

  // Mock employee data - in real app, this would come from API
  const employees = [
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
      skills: ["React", "TypeScript", "Node.js"],
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
      reportsTo: "ceo@company.com",
      managerName: "CEO",
      status: "active",
      skills: ["Leadership", "Project Management", "Strategy"],
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
      managerName: "CEO",
      status: "active",
      skills: ["Recruitment", "Employee Relations", "Policy Development"],
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
      managerName: "CTO",
      status: "active",
      skills: ["System Administration", "Network Security", "Cloud Infrastructure"],
    },
    {
      id: "EMP002",
      name: "Sarah Wilson",
      position: "Frontend Developer",
      email: "sarah.wilson@company.com",
      phone: "+1 (555) 345-6789",
      department: "Engineering",
      role: "employee",
      joinDate: "2023-01-20",
      location: "San Francisco, CA",
      reportsTo: "jane.manager@company.com",
      managerName: "Jane Smith",
      status: "active",
      skills: ["Vue.js", "CSS", "UI/UX Design"],
    },
    {
      id: "EMP003",
      name: "Mike Johnson",
      position: "DevOps Engineer",
      email: "mike.johnson@company.com",
      phone: "+1 (555) 567-8901",
      department: "Engineering",
      role: "employee",
      joinDate: "2021-11-10",
      location: "Austin, TX",
      reportsTo: "jane.manager@company.com",
      managerName: "Jane Smith",
      status: "active",
      skills: ["Docker", "Kubernetes", "AWS"],
    },
    {
      id: "EMP004",
      name: "Emily Davis",
      position: "Marketing Specialist",
      email: "emily.davis@company.com",
      phone: "+1 (555) 678-9012",
      department: "Marketing",
      role: "employee",
      joinDate: "2022-09-15",
      location: "Los Angeles, CA",
      reportsTo: "marketing.manager@company.com",
      managerName: "Marketing Manager",
      status: "active",
      skills: ["Content Marketing", "SEO", "Social Media"],
    },
    {
      id: "EMP005",
      name: "David Brown",
      position: "Sales Representative",
      email: "david.brown@company.com",
      phone: "+1 (555) 789-0123",
      department: "Sales",
      role: "employee",
      joinDate: "2023-02-28",
      location: "Miami, FL",
      reportsTo: "sales.manager@company.com",
      managerName: "Sales Manager",
      status: "active",
      skills: ["B2B Sales", "CRM", "Negotiation"],
    },
  ]

  const departments = ["Engineering", "Human Resources", "IT Support", "Marketing", "Sales", "Finance", "Operations"]
  const roles = ["employee", "manager", "hr", "it"]

  const filteredEmployees = employees.filter((employee) => {
    const matchesSearch =
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.skills.some((skill) => skill.toLowerCase().includes(searchTerm.toLowerCase()))

    const matchesDepartment = departmentFilter === "all" || employee.department === departmentFilter
    const matchesRole = roleFilter === "all" || employee.role === roleFilter

    return matchesSearch && matchesDepartment && matchesRole
  })

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "manager":
        return <Crown className="w-4 h-4 text-amber-600" />
      case "hr":
        return <Users className="w-4 h-4 text-purple-600" />
      case "it":
        return <Building2 className="w-4 h-4 text-blue-600" />
      default:
        return <User className="w-4 h-4 text-gray-600" />
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case "manager":
        return "from-amber-500 to-orange-500"
      case "hr":
        return "from-purple-500 to-pink-500"
      case "it":
        return "from-blue-500 to-cyan-500"
      default:
        return "from-gray-500 to-slate-500"
    }
  }

  const getStatusColor = (status: string) => {
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
  }

  const formatJoinDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    })
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
              <Badge className="bg-blue-100 text-blue-800">{employees.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900">{employees.length}</p>
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
              <Badge className="bg-emerald-100 text-emerald-800">{departments.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Departments</p>
              <p className="text-2xl font-bold text-gray-900">{departments.length}</p>
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
                {employees.filter((e) => e.role === "manager").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Managers</p>
              <p className="text-2xl font-bold text-gray-900">{employees.filter((e) => e.role === "manager").length}</p>
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
                {employees.filter((e) => e.department === userInfo.department).length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Your Department</p>
              <p className="text-2xl font-bold text-gray-900">
                {employees.filter((e) => e.department === userInfo.department).length}
              </p>
              <p className="text-xs text-gray-500">{userInfo.department}</p>
            </div>
          </CardContent>
        </Card>
      </div>

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
                    {dept} ({employees.filter((e) => e.department === dept).length})
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
            key={employee.id}
            className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer group bg-white/80 backdrop-blur-sm hover:scale-105 ${
              employee.email === userInfo.email ? "ring-2 ring-orange-300" : ""
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-start gap-4 mb-4">
                <Avatar className="w-16 h-16 ring-2 ring-white shadow-lg">
                  <AvatarFallback
                    className={`bg-gradient-to-r ${getRoleColor(employee.role)} text-white font-medium text-lg`}
                  >
                    {getInitials(employee.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {employee.name}
                      {employee.email === userInfo.email && <span className="text-orange-600 ml-1">(You)</span>}
                    </h3>
                    <div className="flex items-center gap-1">
                      {getRoleIcon(employee.role)}
                      <Badge className={getStatusColor(employee.status)} variant="secondary">
                        {employee.status}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{employee.position}</p>
                  <Badge variant="outline" className="text-xs bg-orange-50 border-orange-200">
                    {employee.department}
                  </Badge>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="truncate">{employee.email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span>{employee.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span>{employee.location}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <User className="w-4 h-4 text-gray-400" />
                  <span>Reports to: {employee.managerName}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>Joined {formatJoinDate(employee.joinDate)}</span>
                </div>
              </div>

              {/* Skills */}
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-500 mb-2">Skills</p>
                <div className="flex flex-wrap gap-1">
                  {employee.skills.slice(0, 3).map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs bg-gray-100">
                      {skill}
                    </Badge>
                  ))}
                  {employee.skills.length > 3 && (
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
    </div>
  )
}
