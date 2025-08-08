"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import {
  Zap,
  Search,
  StickyNote,
  Clock,
  CheckSquare,
  Calendar,
  Users,
  FileText,
  MessageSquare,
  Lightbulb,
  TrendingUp,
  Star,
  Target,
} from "lucide-react"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
}

interface QuickActionsProps {
  userInfo: UserInfo
  onNavigate: (view: string) => void
}

export default function QuickActions({ userInfo, onNavigate }: QuickActionsProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [quickNote, setQuickNote] = useState("")
  const [noteCharCount, setNoteCharCount] = useState(0)

  const quickActionButtons = [
    { id: "leave", label: "Request Leave", icon: Calendar, color: "from-green-500 to-emerald-600" },
    { id: "timesheet", label: "Log Time", icon: Clock, color: "from-blue-500 to-cyan-600" },
    { id: "support", label: "Get Help", icon: MessageSquare, color: "from-purple-500 to-pink-600" },
    { id: "team", label: "Team Info", icon: Users, color: "from-orange-500 to-amber-600" },
    { id: "directory", label: "Directory", icon: Users, color: "from-indigo-500 to-blue-600" },
    { id: "learning", label: "Learn", icon: FileText, color: "from-teal-500 to-cyan-600" },
  ]

  const recentActivities = [
    {
      id: 1,
      action: "Submitted timesheet",
      time: "2 hours ago",
      icon: Clock,
      color: "text-blue-600",
    },
    {
      id: 2,
      action: "Completed training module",
      time: "1 day ago",
      icon: CheckSquare,
      color: "text-green-600",
    },
    {
      id: 3,
      action: "Updated profile",
      time: "3 days ago",
      icon: Users,
      color: "text-purple-600",
    },
    {
      id: 4,
      action: "Requested vacation leave",
      time: "1 week ago",
      icon: Calendar,
      color: "text-orange-600",
    },
  ]

  const upcomingTasks = [
    {
      id: 1,
      task: "Complete Q4 performance review",
      dueDate: "Dec 30, 2024",
      priority: "high",
      icon: Target,
    },
    {
      id: 2,
      task: "Submit expense report",
      dueDate: "Dec 25, 2024",
      priority: "medium",
      icon: FileText,
    },
    {
      id: 3,
      task: "Attend team meeting",
      dueDate: "Tomorrow",
      priority: "low",
      icon: Users,
    },
  ]

  const dailyTips = [
    "💡 Use Ctrl+K to quickly search across the platform",
    "🚀 Set up your out-of-office message before taking leave",
    "⭐ Complete your learning modules to earn badges",
    "📊 Check your dashboard for pending approvals",
    "🎯 Update your goals regularly for better performance tracking",
    "☕ Take regular breaks to maintain productivity",
  ]

  const randomTip = dailyTips[Math.floor(Math.random() * dailyTips.length)]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "low":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const handleNoteChange = (value: string) => {
    if (value.length <= 280) {
      setQuickNote(value)
      setNoteCharCount(value.length)
    }
  }

  const saveNote = () => {
    if (quickNote.trim()) {
      // In a real app, this would save to backend
      console.log("Saving note:", quickNote)
      setQuickNote("")
      setNoteCharCount(0)
      // Show success message
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
          Quick Actions Hub
        </h2>
        <p className="text-gray-600 dark:text-gray-400">Fast access to your most-used features and tools</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Main Actions */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Action Buttons */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-orange-600" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {quickActionButtons.map((action) => {
                  const Icon = action.icon
                  return (
                    <Button
                      key={action.id}
                      onClick={() => onNavigate(action.id)}
                      className={`h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r ${action.color} text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105`}
                    >
                      <Icon className="w-8 h-8" />
                      <span className="text-sm font-medium">{action.label}</span>
                    </Button>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Global Search */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-orange-600" />
                Global Search
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search employees, documents, policies, or anything..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-12 text-base"
                />
              </div>
              {searchQuery && (
                <div className="mt-4 p-4 bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800 dark:to-slate-800 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Searching for: <span className="font-medium text-gray-900 dark:text-white">"{searchQuery}"</span>
                  </p>
                  <div className="mt-2 space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Users className="w-4 h-4 text-blue-600" />
                      <span>Found 3 employees matching your search</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="w-4 h-4 text-green-600" />
                      <span>Found 5 documents</span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Note */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <StickyNote className="w-5 h-5 text-orange-600" />
                Quick Note
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Textarea
                  placeholder="Jot down a quick note, reminder, or idea..."
                  value={quickNote}
                  onChange={(e) => handleNoteChange(e.target.value)}
                  rows={3}
                  className="resize-none"
                />
                <div className="absolute bottom-2 right-2 text-xs text-gray-400">{noteCharCount}/280</div>
              </div>
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Notes are saved automatically and synced across devices
                </p>
                <Button
                  onClick={saveNote}
                  disabled={!quickNote.trim()}
                  size="sm"
                  className="bg-gradient-to-r from-orange-500 to-amber-600 text-white"
                >
                  <StickyNote className="w-4 h-4 mr-1" />
                  Save
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Activity & Tasks */}
        <div className="space-y-8">
          {/* Recent Activities */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-600" />
                Recent Activities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => {
                  const Icon = activity.icon
                  return (
                    <div
                      key={activity.id}
                      className="flex items-center gap-3 p-3 bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800 dark:to-slate-800 rounded-lg hover:shadow-md transition-all duration-200"
                    >
                      <div className={`p-2 rounded-lg bg-white dark:bg-gray-700 shadow-sm`}>
                        <Icon className={`w-4 h-4 ${activity.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{activity.action}</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{activity.time}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Tasks */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="w-5 h-5 text-orange-600" />
                Upcoming Tasks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {upcomingTasks.map((task) => {
                  const Icon = task.icon
                  return (
                    <div
                      key={task.id}
                      className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-lg border border-blue-200/50 dark:border-blue-800/50"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white">{task.task}</span>
                        </div>
                        <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 ml-6">Due: {task.dueDate}</p>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Daily Tip */}
          <Card className="border-0 shadow-lg bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-orange-600" />
                Daily Tip
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg shadow-lg">
                  <Star className="w-4 h-4 text-white" />
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{randomTip}</p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-orange-600" />
                Your Stats
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Tasks Completed</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div className="w-3/4 h-full bg-gradient-to-r from-green-500 to-emerald-600"></div>
                    </div>
                    <span className="text-sm font-medium">75%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Learning Progress</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div className="w-1/2 h-full bg-gradient-to-r from-blue-500 to-cyan-600"></div>
                    </div>
                    <span className="text-sm font-medium">50%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Goal Achievement</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div className="w-5/6 h-full bg-gradient-to-r from-purple-500 to-pink-600"></div>
                    </div>
                    <span className="text-sm font-medium">83%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
