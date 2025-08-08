"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Users,
  UserPlus,
  Search,
  MoreHorizontal,
  Clock,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Building2,
  Mail,
  Phone,
  MapPin,
} from "lucide-react"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
}

interface HRManagementProps {
  userInfo: UserInfo
}

export default function HRManagement({ userInfo }: HRManagementProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedDepartment, setSelectedDepartment] = useState("all")
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null)

  // Mock data for demonstration
  const employees = [
    {
      id: 1,
      name: "John Smith",
      email: "john.smith@echobyte.com",
      employeeId: "EMP001",
      department: "Engineering",
      position: "Senior Developer",
      manager: "Sarah Wilson",
      joinDate: "2022-01-15",
      status: "active",
      phone: "+1 (555) 123-4567",
      address: "123 Main St, San Francisco, CA",
      salary: 95000,
      performance: 4.5,
      leaveBalance: 18,
    },
    {
      id: 2,
      name: "Emily Davis",
      email: "emily.davis@echobyte.com",
      employeeId: "EMP002",
      department: "Marketing",
      position: "Marketing Manager",
      manager: "Mike Johnson",
      joinDate: "2021-08-20",
      status: "active",
      phone: "+1 (555) 234-5678",
      address: "456 Oak Ave, San Francisco, CA",
      salary: 78000,
      performance: 4.2,
      leaveBalance: 22,
    },
    {
      id: 3,
      name: "Michael Chen",
      email: "michael.chen@echobyte.com",
      employeeId: "EMP003",
      department: "Engineering",
      position: "Frontend Developer",
      manager: "Sarah Wilson",
      joinDate: "2023-03-10",
      status: "active",
      phone: "+1 (555) 345-6789",
      address: "789 Pine St, San Francisco, CA",
      salary: 72000,
      performance: 4.0,
      leaveBalance: 15,
    },
    {
      id: 4,
      name: "Lisa Wang",
      email: "lisa.wang@echobyte.com",
      employeeId: "EMP004",
      department: "HR",
      position: "HR Specialist",
      manager: "David Brown",
      joinDate: "2022-06-01",
      status: "on-leave",
      phone: "+1 (555) 456-7890",
      address: "321 Elm St, San Francisco, CA",
      salary: 65000,
      performance: 4.3,
      leaveBalance: 8,
    },
  ]

  const onboardingTasks = [
    {
      id: 1,
      employeeName: "Alex Rodriguez",
      employeeId: "EMP005",
      startDate: "2024-01-22",
      department: "Engineering",
      position: "Junior Developer",
      progress: 75,
      completedTasks: 6,
      totalTasks: 8,
      status: "in-progress",
      tasks: [
        { name: "Complete paperwork", completed: true },
        { name: "IT setup", completed: true },
        { name: "Office tour", completed: true },
        { name: "Meet team members", completed: true },
        { name: "Security training", completed: true },
        { name: "System access setup", completed: true },
        { name: "First project assignment", completed: false },
        { name: "30-day check-in", completed: false },
      ],
    },
    {
      id: 2,
      employeeName: "Maria Garcia",
      employeeId: "EMP006",
      startDate: "2024-01-29",
      department: "Marketing",
      position: "Content Writer",
      progress: 25,
      completedTasks: 2,
      totalTasks: 8,
      status: "in-progress",
      tasks: [
        { name: "Complete paperwork", completed: true },
        { name: "IT setup", completed: true },
        { name: "Office tour", completed: false },
        { name: "Meet team members", completed: false },
        { name: "Security training", completed: false },
        { name: "System access setup", completed: false },
        { name: "First project assignment", completed: false },
        { name: "30-day check-in", completed: false },
      ],
    },
  ]

  const hrTickets = [
    {
      id: 1,
      employeeName: "Sarah Johnson",
      employeeId: "EMP007",
      subject: "Payroll Inquiry",
      category: "Payroll",
      priority: "medium",
      status: "open",
      createdDate: "2024-01-15",
      description: "Question about overtime calculation on last paycheck",
    },
    {
      id: 2,
      employeeName: "Tom Wilson",
      employeeId: "EMP008",
      subject: "Benefits Enrollment",
      category: "Benefits",
      priority: "high",
      status: "in-progress",
      createdDate: "2024-01-14",
      description: "Need help enrolling in health insurance plan",
    },
    {
      id: 3,
      employeeName: "Jennifer Lee",
      employeeId: "EMP009",
      subject: "Policy Clarification",
      category: "Policy",
      priority: "low",
      status: "resolved",
      createdDate: "2024-01-10",
      description: "Questions about remote work policy",
    },
  ]

  const departmentStats = [
    { name: "Engineering", count: 25, growth: "+12%" },
    { name: "Marketing", count: 8, growth: "+25%" },
    { name: "Sales", count: 12, growth: "+8%" },
    { name: "HR", count: 4, growth: "0%" },
    { name: "Finance", count: 6, growth: "+16%" },
  ]

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      case "on-leave":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "inactive":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "low":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const getTicketStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
      case "in-progress":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "resolved":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const filteredEmployees = employees.filter((employee) => {
    const matchesSearch =
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.employeeId.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDepartment = selectedDepartment === "all" || employee.department === selectedDepartment
    return matchesSearch && matchesDepartment
  })

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">HR Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage employees, onboarding, and HR operations</p>
        </div>
        <div className="flex items-center gap-4">
          <Button className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
            <UserPlus className="w-4 h-4 mr-2" />
            Add Employee
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Employees</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{employees.length}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Onboarding</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{onboardingTasks.length}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
                <UserPlus className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Open Tickets</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {hrTickets.filter((t) => t.status !== "resolved").length}
                </p>
              </div>
              <div className="p-3 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Departments</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{departmentStats.length}</p>
              </div>
              <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="employees" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 bg-white dark:bg-gray-800 shadow-lg">
          <TabsTrigger value="employees" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Employees
          </TabsTrigger>
          <TabsTrigger value="onboarding" className="flex items-center gap-2">
            <UserPlus className="w-4 h-4" />
            Onboarding
          </TabsTrigger>
          <TabsTrigger value="tickets" className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            HR Tickets
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Employees Tab */}
        <TabsContent value="employees">
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Employee Directory</CardTitle>
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search employees..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Filter by department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Departments</SelectItem>
                      <SelectItem value="Engineering">Engineering</SelectItem>
                      <SelectItem value="Marketing">Marketing</SelectItem>
                      <SelectItem value="Sales">Sales</SelectItem>
                      <SelectItem value="HR">HR</SelectItem>
                      <SelectItem value="Finance">Finance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredEmployees.map((employee) => (
                  <div
                    key={employee.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                          {getInitials(employee.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold text-lg">{employee.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {employee.position} • {employee.department}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                          ID: {employee.employeeId} • Joined: {employee.joinDate}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">Performance: {employee.performance}/5.0</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Leave: {employee.leaveBalance} days</p>
                      </div>
                      <Badge className={getStatusColor(employee.status)}>{employee.status}</Badge>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="ghost" size="sm" onClick={() => setSelectedEmployee(employee)}>
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Employee Details</DialogTitle>
                            <DialogDescription>Complete information for {employee.name}</DialogDescription>
                          </DialogHeader>
                          {selectedEmployee && (
                            <div className="space-y-6">
                              <div className="flex items-center gap-4">
                                <Avatar className="w-16 h-16">
                                  <AvatarFallback className="bg-gradient-to-r from-orange-500 to-amber-500 text-white text-xl">
                                    {getInitials(selectedEmployee.name)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <h3 className="text-xl font-semibold">{selectedEmployee.name}</h3>
                                  <p className="text-gray-600 dark:text-gray-400">{selectedEmployee.position}</p>
                                  <Badge className={getStatusColor(selectedEmployee.status)}>
                                    {selectedEmployee.status}
                                  </Badge>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-6">
                                <div className="space-y-4">
                                  <h4 className="font-semibold">Contact Information</h4>
                                  <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                      <Mail className="w-4 h-4 text-gray-400" />
                                      <span className="text-sm">{selectedEmployee.email}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Phone className="w-4 h-4 text-gray-400" />
                                      <span className="text-sm">{selectedEmployee.phone}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <MapPin className="w-4 h-4 text-gray-400" />
                                      <span className="text-sm">{selectedEmployee.address}</span>
                                    </div>
                                  </div>
                                </div>

                                <div className="space-y-4">
                                  <h4 className="font-semibold">Work Information</h4>
                                  <div className="space-y-2">
                                    <div className="flex justify-between">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">Employee ID:</span>
                                      <span className="text-sm font-medium">{selectedEmployee.employeeId}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">Department:</span>
                                      <span className="text-sm font-medium">{selectedEmployee.department}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">Manager:</span>
                                      <span className="text-sm font-medium">{selectedEmployee.manager}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">Join Date:</span>
                                      <span className="text-sm font-medium">{selectedEmployee.joinDate}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">Salary:</span>
                                      <span className="text-sm font-medium">
                                        ${selectedEmployee.salary.toLocaleString()}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                          <DialogFooter>
                            <Button variant="outline">Edit Employee</Button>
                            <Button>View Full Profile</Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Onboarding Tab */}
        <TabsContent value="onboarding">
          <div className="space-y-6">
            {onboardingTasks.map((task) => (
              <Card key={task.id} className="shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="bg-gradient-to-r from-green-500 to-emerald-500 text-white text-sm">
                            {getInitials(task.employeeName)}
                          </AvatarFallback>
                        </Avatar>
                        {task.employeeName}
                      </CardTitle>
                      <CardDescription>
                        {task.position} • {task.department} • Starts: {task.startDate}
                      </CardDescription>
                    </div>
                    <Badge
                      className={
                        task.status === "completed" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"
                      }
                    >
                      {task.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Progress</span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {task.completedTasks}/{task.totalTasks} tasks completed
                        </span>
                      </div>
                      <Progress value={task.progress} className="h-2" />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {task.tasks.map((taskItem, index) => (
                        <div key={index} className="flex items-center gap-3 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                          {taskItem.completed ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <Clock className="w-5 h-5 text-gray-400" />
                          )}
                          <span
                            className={`text-sm ${taskItem.completed ? "text-gray-900 dark:text-white" : "text-gray-600 dark:text-gray-400"}`}
                          >
                            {taskItem.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* HR Tickets Tab */}
        <TabsContent value="tickets">
          <div className="space-y-4">
            {hrTickets.map((ticket) => (
              <Card key={ticket.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-10 h-10">
                        <AvatarFallback className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                          {getInitials(ticket.employeeName)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold">{ticket.subject}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {ticket.employeeName} • {ticket.employeeId}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(ticket.priority)}>{ticket.priority}</Badge>
                      <Badge className={getTicketStatusColor(ticket.status)}>{ticket.status}</Badge>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Category: {ticket.category} • Created: {ticket.createdDate}
                    </p>
                    <p className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">{ticket.description}</p>
                  </div>

                  {ticket.status !== "resolved" && (
                    <div className="flex justify-end gap-2 mt-4">
                      <Button variant="outline" size="sm">
                        Assign
                      </Button>
                      <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white">
                        Resolve
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Department Distribution</CardTitle>
                <CardDescription>Employee count by department</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {departmentStats.map((dept, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"></div>
                        <span className="font-medium">{dept.name}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-2xl font-bold">{dept.count}</span>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                          {dept.growth}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Performance Overview</CardTitle>
                <CardDescription>Average performance ratings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-orange-600 mb-2">4.25</div>
                    <p className="text-gray-600 dark:text-gray-400">Average Rating</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Excellent (4.5-5.0)</span>
                      <span className="text-sm font-medium">25%</span>
                    </div>
                    <Progress value={25} className="h-2" />

                    <div className="flex justify-between items-center">
                      <span className="text-sm">Good (4.0-4.4)</span>
                      <span className="text-sm font-medium">50%</span>
                    </div>
                    <Progress value={50} className="h-2" />

                    <div className="flex justify-between items-center">
                      <span className="text-sm">Average (3.5-3.9)</span>
                      <span className="text-sm font-medium">20%</span>
                    </div>
                    <Progress value={20} className="h-2" />

                    <div className="flex justify-between items-center">
                      <span className="text-sm">Below Average (3.0-3.4)</span>
                      <span className="text-sm font-medium">5%</span>
                    </div>
                    <Progress value={5} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
