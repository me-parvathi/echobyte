"use client"

import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  Search,
  Bell,
  Settings,
  User,
  LogOut,
  Moon,
  Sun,
  Monitor,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Building2,
  Loader2,
  RefreshCw,
  AlertCircle,
  WifiOff,
  Mail,
  Smartphone,
  Volume2,
  X,
} from "lucide-react"
import { useProfilePicture } from "@/hooks/use-profile-picture"
import { useNotifications } from "@/hooks/use-notifications"
import { formatDistanceToNow } from "date-fns"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { api } from "@/lib/api"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
  employeeId?: string
}

interface DashboardHeaderProps {
  userInfo: UserInfo
  onSettingsClick?: () => void
}

interface NotificationPreferences {
  email_enabled: boolean
  push_enabled: boolean
  desktop_enabled: boolean
  sound_enabled: boolean
  quiet_hours_start?: string
  quiet_hours_end?: string
  timezone: string
  preferences?: string
}

export default function DashboardHeader({ userInfo, onSettingsClick }: DashboardHeaderProps) {
  const { theme, setTheme } = useTheme()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [searchQuery, setSearchQuery] = useState("")
  
  // Get employee ID for profile picture fetching
  const employeeId = userInfo.employeeId ? parseInt(userInfo.employeeId) : 1
  
  // Fetch profile picture
  const { pictureUrl } = useProfilePicture(employeeId)

  // Track if notifications have been initially loaded
  const [hasInitiallyLoaded, setHasInitiallyLoaded] = useState(false)

  // Use the notifications hook with enabled option to prevent premature fetching
  const {
    notifications,
    unreadCount,
    loading,
    error,
    hasMore,
    refetch,
    markAsRead,
    loadMore,
    clearError,
  } = useNotifications({
    autoPoll: true,
    pollInterval: 30000, // 30 seconds
    initialLimit: 10,
    loadMoreLimit: 10,
    enabled: true, // This will be controlled by the auth state
  })

  // Mark as initially loaded when first data fetch completes
  useEffect(() => {
    if (!loading && !hasInitiallyLoaded) {
      setHasInitiallyLoaded(true)
    }
  }, [loading, hasInitiallyLoaded])

  // Notification settings state
  const [showNotificationSettings, setShowNotificationSettings] = useState(false)
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_enabled: true,
    push_enabled: true,
    desktop_enabled: true,
    sound_enabled: true,
    timezone: "UTC",
  })
  const [preferencesLoading, setPreferencesLoading] = useState(false)
  const [preferencesError, setPreferencesError] = useState<string | null>(null)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
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

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    })
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  // Helper functions for notification display
  const formatNotificationTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return "Unknown time"
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "leave":
        return Calendar
      case "timesheet":
        return Clock
      case "meeting":
        return Calendar
      case "system":
        return AlertTriangle
      case "approval":
        return CheckCircle
      default:
        return Bell
    }
  }

  const getNotificationColor = (type: string, priority: string) => {
    if (priority === "urgent") return "text-red-600"
    if (priority === "high") return "text-orange-600"
    
    switch (type.toLowerCase()) {
      case "leave":
        return "text-green-600"
      case "timesheet":
        return "text-blue-600"
      case "meeting":
        return "text-purple-600"
      case "system":
        return "text-orange-600"
      case "approval":
        return "text-green-600"
      default:
        return "text-gray-600"
    }
  }

  const handleMarkAsRead = async (notificationId: string) => {
    await markAsRead(notificationId)
  }

  // Fetch notification preferences
  const fetchPreferences = async () => {
    try {
      setPreferencesLoading(true)
      setPreferencesError(null)
      const response = await api.get<NotificationPreferences>('/api/notifications/preferences')
      setPreferences(response)
    } catch (error) {
      setPreferencesError('Failed to load notification preferences')
      console.error('Error fetching preferences:', error)
    } finally {
      setPreferencesLoading(false)
    }
  }

  // Update notification preferences
  const updatePreferences = async (newPreferences: Partial<NotificationPreferences>) => {
    try {
      setPreferencesLoading(true)
      setPreferencesError(null)
      const response = await api.put<NotificationPreferences>('/api/notifications/preferences', newPreferences)
      setPreferences(response)
    } catch (error) {
      setPreferencesError('Failed to update notification preferences')
      console.error('Error updating preferences:', error)
    } finally {
      setPreferencesLoading(false)
    }
  }

  // Handle preference toggle
  const handlePreferenceToggle = async (key: keyof NotificationPreferences, value: boolean) => {
    const newPreferences = { ...preferences, [key]: value }
    setPreferences(newPreferences) // Optimistic update
    await updatePreferences({ [key]: value })
  }

  // Open notification settings
  const handleOpenNotificationSettings = async () => {
    setShowNotificationSettings(true)
    await fetchPreferences()
  }

  // Skeleton loading component for notifications
  const NotificationSkeleton = () => (
    <div className="p-4 border-b border-gray-100 dark:border-gray-800 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  )

  // Empty state component
  const EmptyState = () => (
    <div className="p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900/20 dark:to-amber-900/20 rounded-full flex items-center justify-center">
        <Bell className="w-8 h-8 text-orange-500 dark:text-orange-400" />
      </div>
      <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
        No notifications yet
      </h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        We'll notify you when there's something new
      </p>
      <Button
        variant="outline"
        size="sm"
        onClick={refetch}
        className="text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-800"
      >
        <RefreshCw className="w-3 h-3 mr-1" />
        Check for updates
      </Button>
    </div>
  )

  // Error state component
  const ErrorState = () => (
    <div className="p-6 text-center">
      <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-red-100 to-rose-100 dark:from-red-900/20 dark:to-rose-900/20 rounded-full flex items-center justify-center">
        <WifiOff className="w-8 h-8 text-red-500 dark:text-red-400" />
      </div>
      <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
        Unable to load notifications
      </h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4 max-w-xs mx-auto">
        {error || "Something went wrong. Please try again."}
      </p>
      <div className="flex gap-2 justify-center">
        <Button
          variant="outline"
          size="sm"
          onClick={refetch}
          className="text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-800"
        >
          <RefreshCw className="w-3 h-3 mr-1" />
          Try again
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearError}
          className="text-gray-500 dark:text-gray-400"
        >
          Dismiss
        </Button>
      </div>
    </div>
  )

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
    window.location.href = "/"
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-orange-200/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left Section - Company Logo & Time */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center shadow-lg">
              <Building2 className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                EchoByte
              </h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">Employee Portal</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-4 px-4 py-2 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl border border-orange-200/50 dark:border-orange-800/50">
            <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            <div className="text-sm">
              <div className="font-mono font-medium text-gray-900 dark:text-white">{formatTime(currentTime)}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">{formatDate(currentTime)}</div>
            </div>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search employees, documents, or features..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-white/60 dark:bg-gray-800/60 border-orange-200/50 dark:border-orange-800/50 focus:border-orange-400 dark:focus:border-orange-600"
            />
          </div>
        </div>

        {/* Right Section - Actions & Profile */}
        <div className="flex items-center gap-3">
          {/* Mobile Search */}
          <Button variant="ghost" size="sm" className="md:hidden">
            <Search className="w-4 h-4" />
          </Button>

          {/* Notifications */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-4 h-4" />
                {unreadCount > 0 && (
                  <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center bg-gradient-to-r from-red-500 to-rose-600 text-white text-xs border-0">
                    {unreadCount}
                  </Badge>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0" align="end">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
                  <div className="flex items-center gap-2">
                    {loading && !hasInitiallyLoaded && <Loader2 className="w-4 h-4 animate-spin text-orange-500" />}
                    <Badge 
                      variant="secondary" 
                      className={unreadCount > 0 ? "bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300" : ""}
                    >
                      {unreadCount} new
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={refetch}
                      disabled={loading}
                      className="h-6 w-6 p-0 hover:bg-orange-50 dark:hover:bg-orange-900/20"
                      title="Refresh notifications"
                    >
                      <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {/* Error State - Show full error state when API fails */}
                {error && !loading && notifications.length === 0 && <ErrorState />}
                
                {/* Loading State - Show skeleton only during initial load */}
                {loading && !hasInitiallyLoaded && (
                  <div>
                    {Array.from({ length: 3 }).map((_, index) => (
                      <NotificationSkeleton key={index} />
                    ))}
                  </div>
                )}
                
                {/* Empty State - Show when no notifications exist and not loading */}
                {!loading && !error && notifications.length === 0 && hasInitiallyLoaded && <EmptyState />}
                
                {/* Notifications List - Show when data is available */}
                {!loading && !error && notifications.length > 0 && (
                  <>
                    {notifications.map((notification) => {
                      const Icon = getNotificationIcon(notification.type)
                      const color = getNotificationColor(notification.type, notification.priority)
                      
                      return (
                        <div
                          key={notification.id}
                          className={`p-4 border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors ${
                            !notification.is_read ? "bg-orange-50/50 dark:bg-orange-900/10" : ""
                          }`}
                          onClick={() => handleMarkAsRead(notification.id)}
                        >
                          <div className="flex items-start gap-3">
                            <div className={`p-1.5 rounded-lg bg-white dark:bg-gray-700 shadow-sm`}>
                              <Icon className={`w-4 h-4 ${color}`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-1">
                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                  {notification.title}
                                </p>
                                {!notification.is_read && (
                                  <div className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0"></div>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1 line-clamp-2">
                                {notification.message}
                              </p>
                              <div className="flex items-center gap-2">
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                  {formatNotificationTime(notification.created_at)}
                                </p>
                                {notification.priority !== "normal" && (
                                  <Badge 
                                    variant="outline" 
                                    className={`text-xs ${
                                      notification.priority === "urgent" ? "border-red-300 text-red-600" :
                                      notification.priority === "high" ? "border-orange-300 text-orange-600" :
                                      "border-blue-300 text-blue-600"
                                    }`}
                                  >
                                    {notification.priority}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                    
                    {/* Load More Button - Only show if more data exists */}
                    {hasMore && (
                      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={loadMore}
                          disabled={loading}
                          className="w-full text-orange-600 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20"
                        >
                          {loading ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Loading more...
                            </>
                          ) : (
                            <>
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Load more notifications
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                  </>
                )}
                
                {/* Partial Error State - Show when there's an error but some data exists */}
                {error && notifications.length > 0 && (
                  <div className="p-3 border-t border-red-200 bg-red-50 dark:bg-red-900/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <p className="text-sm text-red-600 dark:text-red-400">
                          Some notifications may not be up to date
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearError}
                        className="h-6 px-2 text-red-600 dark:text-red-400"
                      >
                        ×
                      </Button>
                    </div>
                  </div>
                )}
              </div>
              <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                <Button variant="ghost" size="sm" className="w-full text-orange-600 dark:text-orange-400">
                  View all notifications
                </Button>
              </div>
            </PopoverContent>
          </Popover>

          {/* Settings Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Settings</DropdownMenuLabel>
              <DropdownMenuSeparator />

              <DropdownMenuItem onClick={onSettingsClick}>
                <User className="w-4 h-4 mr-2" />
                Preferences
              </DropdownMenuItem>

              <DropdownMenuItem onClick={handleOpenNotificationSettings}>
                <Bell className="w-4 h-4 mr-2" />
                Notification Settings
              </DropdownMenuItem>

              <DropdownMenuSeparator />
              <DropdownMenuLabel>Theme</DropdownMenuLabel>

              <DropdownMenuItem onClick={() => setTheme("light")}>
                <Sun className="w-4 h-4 mr-2" />
                Light
                {theme === "light" && <CheckCircle className="w-4 h-4 ml-auto text-green-600" />}
              </DropdownMenuItem>

              <DropdownMenuItem onClick={() => setTheme("dark")}>
                <Moon className="w-4 h-4 mr-2" />
                Dark
                {theme === "dark" && <CheckCircle className="w-4 h-4 ml-auto text-green-600" />}
              </DropdownMenuItem>

              <DropdownMenuItem onClick={() => setTheme("system")}>
                <Monitor className="w-4 h-4 mr-2" />
                System
                {theme === "system" && <CheckCircle className="w-4 h-4 ml-auto text-green-600" />}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar className="h-10 w-10 ring-2 ring-orange-200 dark:ring-orange-800">
                  {pictureUrl && (
                    <AvatarImage src={pictureUrl} alt={userInfo.name} />
                  )}
                  <AvatarFallback className={`bg-gradient-to-r ${getRoleColor(userInfo.type)} text-white font-medium`}>
                    {getInitials(userInfo.name)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{userInfo.name}</p>
                  <p className="text-xs leading-none text-muted-foreground">{userInfo.email}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={`bg-gradient-to-r ${getRoleColor(userInfo.type)} text-white border-0 text-xs`}>
                      {userInfo.type.charAt(0).toUpperCase() + userInfo.type.slice(1)}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {userInfo.department}
                    </Badge>
                  </div>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="w-4 h-4 mr-2" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onSettingsClick}>
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600 dark:text-red-400">
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Notification Settings Modal */}
      <Dialog open={showNotificationSettings} onOpenChange={setShowNotificationSettings}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-orange-500" />
              Notification Settings
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {preferencesError && (
              <div className="p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <p className="text-sm text-red-600 dark:text-red-400">{preferencesError}</p>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                    <Mail className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <Label htmlFor="email-notifications" className="text-sm font-medium">
                      Email Notifications
                    </Label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Receive notifications via email
                    </p>
                  </div>
                </div>
                <Switch
                  id="email-notifications"
                  checked={preferences.email_enabled}
                  onCheckedChange={(checked) => handlePreferenceToggle('email_enabled', checked)}
                  disabled={preferencesLoading}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                    <Smartphone className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <Label htmlFor="push-notifications" className="text-sm font-medium">
                      Push Notifications
                    </Label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Receive push notifications on mobile
                    </p>
                  </div>
                </div>
                <Switch
                  id="push-notifications"
                  checked={preferences.push_enabled}
                  onCheckedChange={(checked) => handlePreferenceToggle('push_enabled', checked)}
                  disabled={preferencesLoading}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                    <Monitor className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <Label htmlFor="desktop-notifications" className="text-sm font-medium">
                      Desktop Notifications
                    </Label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Show desktop notifications
                    </p>
                  </div>
                </div>
                <Switch
                  id="desktop-notifications"
                  checked={preferences.desktop_enabled}
                  onCheckedChange={(checked) => handlePreferenceToggle('desktop_enabled', checked)}
                  disabled={preferencesLoading}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                    <Volume2 className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                  </div>
                  <div>
                    <Label htmlFor="sound-notifications" className="text-sm font-medium">
                      Sound Notifications
                    </Label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Play sound for notifications
                    </p>
                  </div>
                </div>
                <Switch
                  id="sound-notifications"
                  checked={preferences.sound_enabled}
                  onCheckedChange={(checked) => handlePreferenceToggle('sound_enabled', checked)}
                  disabled={preferencesLoading}
                />
              </div>
            </div>

            {preferencesLoading && (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 animate-spin text-orange-500" />
                <span className="ml-2 text-sm text-gray-500">Saving preferences...</span>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </header>
  )
}
