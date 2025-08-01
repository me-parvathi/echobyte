"use client"

import { Loader2, Clock, LayoutDashboard, Calendar, TicketIcon, Briefcase, BookOpen, GraduationCap, Users, Search, User, Zap, CheckSquare, BarChart3, Award, HardDrive } from "lucide-react"
import { useRouter } from "next/navigation"
import useUserInfo from "@/hooks/use-user-info"
import React from "react"

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

export default function DashboardHome() {
  const { userInfo, loading } = useUserInfo()
  const router = useRouter()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-indigo-600" />
      </div>
    )
  }

  if (!userInfo) return null

  return <DashboardOverview userInfo={userInfo} onNavigate={(id)=>router.push(`/dashboard/${id}`)} />
}

// -----------------------------------------------------------------------------
// Dashboard Overview (kept from original file, unchanged)
// -----------------------------------------------------------------------------

function DashboardOverview({ userInfo, onNavigate }: { userInfo: UserInfo; onNavigate: (section: string) => void }) {
  const currentHour = new Date().getHours()
  const hoursWorkedToday = 6.5
  const targetHours = 8

  const getStats = (userType: string) => {
    const baseStats = [
      {
        title: "Hours Today",
        value: hoursWorkedToday,
        target: targetHours,
        icon: Clock,
        color: "from-blue-500 to-cyan-500",
        bgColor: "from-blue-50 to-cyan-50",
        darkBgColor: "dark:from-blue-900/20 dark:to-cyan-900/20",
      },
      {
        title: "This Week",
        value: "32.5h",
        subtitle: "of 40h target",
        icon: LayoutDashboard,
        color: "from-green-500 to-emerald-500",
        bgColor: "from-green-50 to-emerald-50",
        darkBgColor: "dark:from-green-900/20 dark:to-emerald-900/20",
      },
      {
        title: "Leave Balance",
        value: "18",
        subtitle: "days remaining",
        icon: Calendar,
        color: "from-purple-500 to-pink-500",
        bgColor: "from-purple-50 to-pink-50",
        darkBgColor: "dark:from-purple-900/20 dark:to-pink-900/20",
      },
    ]

    const managerStats = [
      ...baseStats,
      {
        title: "Pending Approvals",
        value: "5",
        subtitle: "requests",
        icon: CheckSquare,
        color: "from-orange-500 to-amber-500",
        bgColor: "from-orange-50 to-amber-50",
        darkBgColor: "dark:from-orange-900/20 dark:to-amber-900/20",
      },
    ]

    const hrStats = [
      ...managerStats,
      {
        title: "Active Employees",
        value: "45",
        subtitle: "total",
        icon: Users,
        color: "from-indigo-500 to-purple-500",
        bgColor: "from-indigo-50 to-purple-50",
        darkBgColor: "dark:from-indigo-900/20 dark:to-purple-900/20",
      },
    ]

    const itStats = [
      ...baseStats,
      {
        title: "Active Tickets",
        value: "12",
        subtitle: "open",
        icon: TicketIcon,
        color: "from-red-500 to-pink-500",
        bgColor: "from-red-50 to-pink-50",
        darkBgColor: "dark:from-red-900/20 dark:to-pink-900/20",
      },
    ]

    switch (userType) {
      case "employee":
        return baseStats
      case "manager":
        return managerStats
      case "hr":
        return hrStats
      case "it":
        return itStats
      default:
        return baseStats
    }
  }

  const getQuickActions = (userType: string) => {
    const baseActions = [
      {
        title: "Log Time",
        description: "Quick timesheet entry",
        icon: Clock,
        action: () => onNavigate("timesheet"),
        color: "from-blue-500 to-cyan-500",
      },
      {
        title: "Request Leave",
        description: "Submit time off request",
        icon: Calendar,
        action: () => onNavigate("leave"),
        color: "from-green-500 to-emerald-500",
      },
      {
        title: "Get Help",
        description: "Create support ticket",
        icon: TicketIcon,
        action: () => onNavigate("support"),
        color: "from-orange-500 to-amber-500",
      },
    ]

    const managerActions = [
      ...baseActions,
      {
        title: "Review Approvals",
        description: "Team approvals",
        icon: CheckSquare,
        action: () => onNavigate("approvals"),
        color: "from-purple-500 to-pink-500",
      },
    ]

    const hrActions = [
      ...managerActions,
      {
        title: "Employee Management",
        description: "HR tools",
        icon: Users,
        action: () => onNavigate("employees"),
        color: "from-indigo-500 to-purple-500",
      },
    ]

    const itActions = [
      ...baseActions,
      {
        title: "Asset Management",
        description: "IT assets",
        icon: HardDrive,
        action: () => onNavigate("assets"),
        color: "from-gray-500 to-slate-500",
      },
    ]

    switch (userType) {
      case "employee":
        return baseActions
      case "manager":
        return managerActions
      case "hr":
        return hrActions
      case "it":
        return itActions
      default:
        return baseActions
    }
  }

  const getGreeting = () => {
    if (currentHour < 12) return "Good morning"
    if (currentHour < 17) return "Good afternoon"
    return "Good evening"
  }

  const stats = getStats(userInfo.type)
  const quickActions = getQuickActions(userInfo.type)

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="relative overflow-hidden">
        <div className="border-0 shadow-xl bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 text-white rounded-lg">
          <div className="p-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  {getGreeting()}, {userInfo.name.split(" ")[0]}! 👋
                </h1>
                <p className="text-orange-100 text-lg">
                  Ready to make today productive? Here's your dashboard overview.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div
              key={index}
              className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-gradient-to-br ${stat.bgColor} ${stat.darkBgColor} backdrop-blur-sm hover:scale-105 cursor-pointer rounded-lg p-6`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 bg-gradient-to-r ${stat.color} rounded-xl shadow-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
                {stat.subtitle && <p className="text-xs text-gray-500 dark:text-gray-400">{stat.subtitle}</p>}
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="border-0 shadow-lg bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-orange-600" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon
              return (
                <button
                  key={index}
                  onClick={action.action}
                  className="h-20 flex flex-col items-center gap-2 bg-white/60 dark:bg-gray-700/60 hover:bg-white dark:hover:bg-gray-700 border border-gray-200/50 hover:border-orange-300 hover:shadow-md transition-all duration-200 group rounded-lg"
                >
                  <div
                    className={`p-2 bg-gradient-to-r ${action.color} rounded-lg shadow-md group-hover:scale-110 transition-transform duration-200`}
                  >
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{action.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{action.description}</p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
