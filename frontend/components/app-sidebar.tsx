"use client"

import type React from "react"

import { useRouter, usePathname } from "next/navigation"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Building2, LogOut, User, Calendar, Users } from "lucide-react"

interface SidebarItem {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

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

interface AppSidebarProps {
  items: SidebarItem[]
  userInfo: UserInfo
}

export function AppSidebar({ items, userInfo }: AppSidebarProps) {
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = () => {
    localStorage.removeItem("userType")
    localStorage.removeItem("userEmail")
    localStorage.removeItem("userName")
    localStorage.removeItem("userDepartment")
    localStorage.removeItem("userReportsTo")
    localStorage.removeItem("userManagerName")
    localStorage.removeItem("userEmployeeId")
    localStorage.removeItem("userPosition")
    localStorage.removeItem("userJoinDate")
    router.push("/")
  }

  const getRoleColor = (type: string) => {
    switch (type) {
      case "employee":
        return "from-orange-500 to-amber-500"
      case "manager":
        return "from-emerald-500 to-teal-500"
      case "hr":
        return "from-purple-500 to-pink-500"
      case "it":
        return "from-blue-500 to-cyan-500"
      default:
        return "from-gray-500 to-gray-600"
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const formatJoinDate = (dateString?: string) => {
    if (!dateString) return ""
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", { month: "short", year: "numeric" })
  }

  return (
    <Sidebar className="border-r border-orange-200/50 bg-gradient-to-b from-white to-orange-50/30 backdrop-blur-xl">
      <SidebarHeader className="border-b border-orange-200/50 p-6 bg-gradient-to-r from-white/80 to-orange-50/80">
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-xl bg-gradient-to-r ${getRoleColor(userInfo.type)} flex items-center justify-center shadow-lg`}
          >
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Employee Portal</h2>
            <p className="text-sm text-gray-600 capitalize">{userInfo.type} Dashboard</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-4 py-6">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-2">
              {items.map((item) => {
                const Icon = item.icon
                return (
                  <SidebarMenuItem key={item.id}>
                    <SidebarMenuButton
                      onClick={() => router.push(item.id === "dashboard" ? "/dashboard" : `/dashboard/${item.id}`)}
                      isActive={item.id === "dashboard" ? pathname === "/dashboard" : pathname === `/dashboard/${item.id}`}
                      className={`w-full justify-start px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-200 hover:shadow-md ${
                        (item.id === "dashboard" ? pathname === "/dashboard" : pathname === `/dashboard/${item.id}`)
                          ? `bg-gradient-to-r ${getRoleColor(userInfo.type)} text-white shadow-lg`
                          : "hover:bg-orange-100/80 hover:scale-105"
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {item.label}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-orange-200/50 p-4 bg-gradient-to-r from-white/80 to-orange-50/80">
        {/* User Profile Card */}
        <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 mb-4 border border-orange-200/50 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <Avatar className="w-12 h-12 ring-2 ring-white shadow-lg">
              <AvatarFallback
                className={`bg-gradient-to-r ${getRoleColor(userInfo.type)} text-white font-medium text-lg`}
              >
                {getInitials(userInfo.name)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900 truncate">{userInfo.name}</p>
              <p className="text-sm text-gray-600 truncate">{userInfo.position}</p>
            </div>
          </div>

          {/* Employee Details */}
          <div className="space-y-2 text-xs">
            {userInfo.managerName && (
              <div className="flex items-center justify-between">
                <span className="text-gray-500 flex items-center gap-1">
                  <User className="w-3 h-3" />
                  Reports to:
                </span>
                <span className="font-medium text-gray-700">{userInfo.managerName}</span>
              </div>
            )}
            {userInfo.joinDate && (
              <div className="flex items-center justify-between">
                <span className="text-gray-500 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Joined:
                </span>
                <span className="font-medium text-gray-700">{formatJoinDate(userInfo.joinDate)}</span>
              </div>
            )}
            <div className="flex items-center justify-between">
              <span className="text-gray-500 flex items-center gap-1">
                <Users className="w-3 h-3" />
                Department:
              </span>
              <span className="font-medium text-orange-600">{userInfo.department}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-500">Employee ID:</span>
              <span className="font-mono font-medium text-orange-600">{userInfo.employeeId}</span>
            </div>
          </div>
        </div>

        <Button
          variant="outline"
          onClick={handleLogout}
          className="w-full justify-start text-gray-700 hover:text-red-600 hover:border-red-200 hover:bg-red-50/50 bg-white/60 backdrop-blur-sm border-orange-200/50 transition-all duration-200"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </Button>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
