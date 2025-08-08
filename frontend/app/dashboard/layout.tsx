"use client"

import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import DashboardHeader from "@/components/dashboard-header"
import useUserInfo from "@/hooks/use-user-info"
import { Toaster } from "@/components/ui/toaster"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { LayoutDashboard, Clock, Calendar, TicketIcon, Briefcase, BookOpen, GraduationCap, Users, Search, User, Zap, Settings, CheckSquare, BarChart3, Award, UserPlus, FileText, HardDrive, Shield, Server, Globe } from "lucide-react"
import { Loader2 } from "lucide-react"
import React from "react"

interface DashboardLayoutProps {
  children: React.ReactNode
}

interface SidebarItem {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

function DashboardLayoutContent({ children }: DashboardLayoutProps) {
  const { userInfo, loading } = useUserInfo()

  const getSidebarItems = (userType: string): SidebarItem[] => {
    const baseItems = [
      { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
      { id: "timesheet", label: "Timesheet", icon: Clock },
      { id: "leave", label: "Leave", icon: Calendar },
      { id: "feedback", label: "Feedback", icon: TicketIcon },
      { id: "support", label: "Support", icon: TicketIcon },
      { id: "career", label: "Career", icon: Briefcase },
      { id: "induction", label: "Induction", icon: BookOpen },
      { id: "learning", label: "Learning", icon: GraduationCap },
      { id: "team", label: "Team", icon: Users },
      { id: "directory", label: "Directory", icon: Search },
      { id: "profile", label: "Profile", icon: User },
      { id: "quick-actions", label: "Quick Actions", icon: Zap },
      { id: "settings", label: "Settings", icon: Settings },
    ]

    const managerItems = [
      ...baseItems,
      { id: "approvals", label: "Approvals", icon: CheckSquare },
      { id: "reports", label: "Team Reports", icon: BarChart3 },
    ]

    const hrItems = [
      ...managerItems,
      { id: "employees", label: "Employees", icon: UserPlus },
      { id: "onboarding", label: "Onboarding", icon: UserPlus },
      { id: "policies", label: "Policies", icon: FileText },
      { id: "analytics", label: "Analytics", icon: BarChart3 },
    ]

    const itItems = [
      ...baseItems,
      { id: "it-tickets", label: "IT Tickets", icon: TicketIcon },
      { id: "assets", label: "Assets", icon: HardDrive },
      { id: "security", label: "Security", icon: Shield },
      { id: "infrastructure", label: "Infrastructure", icon: Server },
    ]

    switch (userType) {
      case "employee":
        return baseItems
      case "manager":
        return managerItems
      case "hr":
        return hrItems
      case "it":
        return itItems
      default:
        return baseItems
    }
  }

  if (loading || !userInfo) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  const sidebarItems = getSidebarItems(userInfo.type)

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-orange-50/30 via-amber-50/20 to-yellow-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <AppSidebar items={sidebarItems} userInfo={userInfo} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <DashboardHeader userInfo={userInfo} />
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
      <Toaster />
    </SidebarProvider>
  )
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <ProtectedRoute requireAuth={true}>
      <DashboardLayoutContent>{children}</DashboardLayoutContent>
    </ProtectedRoute>
  )
} 