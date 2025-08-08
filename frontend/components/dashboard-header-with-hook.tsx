"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { SidebarTrigger } from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
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
} from "lucide-react";
import { useProfilePicture } from "@/hooks/use-profile-picture";
import { useNotifications } from "@/hooks/use-notifications";
import { formatDistanceToNow } from "date-fns";

interface UserInfo {
  email: string;
  name: string;
  department: string;
  type: string;
  employeeId?: string;
}

interface DashboardHeaderProps {
  userInfo: UserInfo;
  onSettingsClick?: () => void;
}

export default function DashboardHeader({
  userInfo,
  onSettingsClick,
}: DashboardHeaderProps) {
  const { theme, setTheme } = useTheme();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState("");

  // Get employee ID for profile picture fetching
  const employeeId = userInfo.employeeId ? parseInt(userInfo.employeeId) : 1;

  // Fetch profile picture
  const { pictureUrl } = useProfilePicture(employeeId);

  // Use the notifications hook
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
  });

  // Update current time
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "hr":
        return "from-purple-500 to-purple-600";
      case "manager":
        return "from-blue-500 to-blue-600";
      case "employee":
        return "from-green-500 to-green-600";
      case "admin":
        return "from-red-500 to-red-600";
      default:
        return "from-gray-500 to-gray-600";
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  const formatNotificationTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return "Unknown time";
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "leave":
        return Calendar;
      case "timesheet":
        return Clock;
      case "meeting":
        return Calendar;
      case "system":
        return AlertTriangle;
      case "approval":
        return CheckCircle;
      default:
        return Bell;
    }
  };

  const getNotificationColor = (type: string, priority: string) => {
    if (priority === "urgent") return "text-red-600";
    if (priority === "high") return "text-orange-600";

    switch (type.toLowerCase()) {
      case "leave":
        return "text-green-600";
      case "timesheet":
        return "text-blue-600";
      case "meeting":
        return "text-purple-600";
      case "system":
        return "text-orange-600";
      case "approval":
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    await markAsRead(notificationId);
  };

  const handleLogout = () => {
    localStorage.removeItem("userType");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    localStorage.removeItem("userDepartment");
    localStorage.removeItem("userReportsTo");
    localStorage.removeItem("userManagerName");
    localStorage.removeItem("userEmployeeId");
    localStorage.removeItem("userPosition");
    localStorage.removeItem("userJoinDate");
    window.location.href = "/";
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-orange-200/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left Section - Hamburger + Company Logo & Time */}
        <div className="flex items-center gap-6">
          {/* Built-in trigger shows a menu icon and toggles the sidebar */}
          <SidebarTrigger className="mr-1 shrink-0" />

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center shadow-lg">
              <Building2 className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                EchoByte
              </h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Employee Portal
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-4 px-4 py-2 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl border border-orange-200/50 dark:border-orange-800/50">
            <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            <div className="text-sm">
              <div className="font-mono font-medium text-gray-900 dark:text-white">
                {formatTime(currentTime)}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                {formatDate(currentTime)}
              </div>
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
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    Notifications
                  </h3>
                  <div className="flex items-center gap-2">
                    {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                    <Badge variant="secondary">{unreadCount} new</Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={refetch}
                      className="h-6 w-6 p-0"
                    >
                      <RefreshCw className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Error State */}
              {error && (
                <div className="p-4 border-b border-red-200 bg-red-50 dark:bg-red-900/10">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-red-600 dark:text-red-400">
                      {error}
                    </p>
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

              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 && !loading ? (
                  <div className="p-8 text-center">
                    <Bell className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      No notifications
                    </p>
                  </div>
                ) : (
                  notifications.map((notification) => {
                    const Icon = getNotificationIcon(notification.type);
                    const color = getNotificationColor(
                      notification.type,
                      notification.priority
                    );

                    return (
                      <div
                        key={notification.id}
                        className={`p-4 border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer transition-colors ${
                          !notification.is_read
                            ? "bg-orange-50/50 dark:bg-orange-900/10"
                            : ""
                        }`}
                        onClick={() => handleMarkAsRead(notification.id)}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`p-1.5 rounded-lg bg-white dark:bg-gray-700 shadow-sm`}
                          >
                            <Icon className={`w-4 h-4 ${color}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                {notification.title}
                              </p>
                              {!notification.is_read && (
                                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2">
                              <p className="text-xs text-gray-500 dark:text-gray-500">
                                {formatNotificationTime(
                                  notification.created_at
                                )}
                              </p>
                              {notification.priority !== "normal" && (
                                <Badge
                                  variant="outline"
                                  className={`text-xs ${
                                    notification.priority === "urgent"
                                      ? "border-red-300 text-red-600"
                                      : notification.priority === "high"
                                      ? "border-orange-300 text-orange-600"
                                      : "border-blue-300 text-blue-600"
                                  }`}
                                >
                                  {notification.priority}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Load More Button */}
              {hasMore && notifications.length > 0 && (
                <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={loadMore}
                    disabled={loading}
                    className="w-full text-orange-600 dark:text-orange-400"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      "Load more notifications"
                    )}
                  </Button>
                </div>
              )}

              <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-orange-600 dark:text-orange-400"
                >
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

              <DropdownMenuSeparator />
              <DropdownMenuLabel>Theme</DropdownMenuLabel>

              <DropdownMenuItem onClick={() => setTheme("light")}>
                <Sun className="w-4 h-4 mr-2" />
                Light
                {theme === "light" && (
                  <CheckCircle className="w-4 h-4 ml-auto text-green-600" />
                )}
              </DropdownMenuItem>

              <DropdownMenuItem onClick={() => setTheme("dark")}>
                <Moon className="w-4 h-4 mr-2" />
                Dark
                {theme === "dark" && (
                  <CheckCircle className="w-4 h-4 ml-auto text-green-600" />
                )}
              </DropdownMenuItem>

              <DropdownMenuItem onClick={() => setTheme("system")}>
                <Monitor className="w-4 h-4 mr-2" />
                System
                {theme === "system" && (
                  <CheckCircle className="w-4 h-4 ml-auto text-green-600" />
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-10 w-10 rounded-full"
              >
                <Avatar className="h-10 w-10 ring-2 ring-orange-200 dark:ring-orange-800">
                  {pictureUrl && (
                    <AvatarImage src={pictureUrl} alt={userInfo.name} />
                  )}
                  <AvatarFallback
                    className={`bg-gradient-to-r ${getRoleColor(
                      userInfo.type
                    )} text-white font-medium`}
                  >
                    {getInitials(userInfo.name)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {userInfo.name}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {userInfo.email}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge
                      className={`bg-gradient-to-r ${getRoleColor(
                        userInfo.type
                      )} text-white border-0 text-xs`}
                    >
                      {userInfo.type.charAt(0).toUpperCase() +
                        userInfo.type.slice(1)}
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
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-red-600 dark:text-red-400"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
