"use client"

import { useState } from "react"
import { useTheme } from "next-themes"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import {
  Moon,
  Sun,
  Monitor,
  Bell,
  Shield,
  Globe,
  Download,
  Upload,
  RotateCcw,
  Palette,
  Volume2,
  Mail,
  Smartphone,
  Eye,
  EyeOff,
  Clock,
  Save,
  Sparkles,
} from "lucide-react"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
}

interface SettingsPanelProps {
  userInfo: UserInfo
}

export default function SettingsPanel({ userInfo }: SettingsPanelProps) {
  const { theme, setTheme } = useTheme()
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      desktop: false,
      sound: true,
      marketing: false,
      security: true,
    },
    privacy: {
      profileVisible: true,
      statusVisible: true,
      activityVisible: false,
      contactInfoVisible: true,
    },
    preferences: {
      language: "en",
      timezone: "America/New_York",
      dateFormat: "MM/DD/YYYY",
      timeFormat: "12h",
      currency: "USD",
    },
    accessibility: {
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      screenReader: false,
    },
  })

  const handleSettingChange = (category: string, setting: string, value: boolean | string) => {
    setSettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [setting]: value,
      },
    }))
  }

  const exportData = () => {
    // In a real app, this would export user data
    const dataStr = JSON.stringify(settings, null, 2)
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr)
    const exportFileDefaultName = "echobyte-settings.json"

    const linkElement = document.createElement("a")
    linkElement.setAttribute("href", dataUri)
    linkElement.setAttribute("download", exportFileDefaultName)
    linkElement.click()
  }

  const resetSettings = () => {
    if (confirm("Are you sure you want to reset all settings to default? This action cannot be undone.")) {
      // Reset to default settings
      setSettings({
        notifications: {
          email: true,
          push: true,
          desktop: false,
          sound: true,
          marketing: false,
          security: true,
        },
        privacy: {
          profileVisible: true,
          statusVisible: true,
          activityVisible: false,
          contactInfoVisible: true,
        },
        preferences: {
          language: "en",
          timezone: "America/New_York",
          dateFormat: "MM/DD/YYYY",
          timeFormat: "12h",
          currency: "USD",
        },
        accessibility: {
          highContrast: false,
          largeText: false,
          reducedMotion: false,
          screenReader: false,
        },
      })
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Settings & Preferences
          </h2>
          <p className="text-gray-600 dark:text-gray-400">Customize your EchoByte experience</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={exportData} variant="outline" className="bg-transparent">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button onClick={resetSettings} variant="outline" className="bg-transparent">
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Theme & Appearance */}
        <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5 text-orange-600" />
              Theme & Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <Label className="text-base font-medium">Theme Mode</Label>
              <div className="grid grid-cols-3 gap-3">
                <Button
                  variant={theme === "light" ? "default" : "outline"}
                  onClick={() => setTheme("light")}
                  className={`flex flex-col items-center gap-2 h-auto p-4 ${
                    theme === "light" ? "bg-gradient-to-r from-orange-500 to-amber-600 text-white" : "bg-transparent"
                  }`}
                >
                  <Sun className="w-5 h-5" />
                  <span className="text-sm">Light</span>
                </Button>
                <Button
                  variant={theme === "dark" ? "default" : "outline"}
                  onClick={() => setTheme("dark")}
                  className={`flex flex-col items-center gap-2 h-auto p-4 ${
                    theme === "dark" ? "bg-gradient-to-r from-orange-500 to-amber-600 text-white" : "bg-transparent"
                  }`}
                >
                  <Moon className="w-5 h-5" />
                  <span className="text-sm">Dark</span>
                </Button>
                <Button
                  variant={theme === "system" ? "default" : "outline"}
                  onClick={() => setTheme("system")}
                  className={`flex flex-col items-center gap-2 h-auto p-4 ${
                    theme === "system" ? "bg-gradient-to-r from-orange-500 to-amber-600 text-white" : "bg-transparent"
                  }`}
                >
                  <Monitor className="w-5 h-5" />
                  <span className="text-sm">System</span>
                </Button>
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <Label className="text-base font-medium">Accessibility</Label>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="high-contrast">High Contrast</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Increase contrast for better visibility</p>
                  </div>
                  <Switch
                    id="high-contrast"
                    checked={settings.accessibility.highContrast}
                    onCheckedChange={(checked) => handleSettingChange("accessibility", "highContrast", checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="large-text">Large Text</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Increase text size throughout the app</p>
                  </div>
                  <Switch
                    id="large-text"
                    checked={settings.accessibility.largeText}
                    onCheckedChange={(checked) => handleSettingChange("accessibility", "largeText", checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="reduced-motion">Reduced Motion</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Minimize animations and transitions</p>
                  </div>
                  <Switch
                    id="reduced-motion"
                    checked={settings.accessibility.reducedMotion}
                    onCheckedChange={(checked) => handleSettingChange("accessibility", "reducedMotion", checked)}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-orange-600" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="email-notifications">Email Notifications</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Receive notifications via email</p>
                  </div>
                </div>
                <Switch
                  id="email-notifications"
                  checked={settings.notifications.email}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "email", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Smartphone className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="push-notifications">Push Notifications</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Receive push notifications on your device
                    </p>
                  </div>
                </div>
                <Switch
                  id="push-notifications"
                  checked={settings.notifications.push}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "push", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Monitor className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="desktop-notifications">Desktop Notifications</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Show notifications on your desktop</p>
                  </div>
                </div>
                <Switch
                  id="desktop-notifications"
                  checked={settings.notifications.desktop}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "desktop", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Volume2 className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="sound-notifications">Sound Notifications</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Play sounds for notifications</p>
                  </div>
                </div>
                <Switch
                  id="sound-notifications"
                  checked={settings.notifications.sound}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "sound", checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Sparkles className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="marketing-notifications">Marketing Updates</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Receive product updates and tips</p>
                  </div>
                </div>
                <Switch
                  id="marketing-notifications"
                  checked={settings.notifications.marketing}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "marketing", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Shield className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="security-notifications">Security Alerts</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Important security notifications</p>
                  </div>
                </div>
                <Switch
                  id="security-notifications"
                  checked={settings.notifications.security}
                  onCheckedChange={(checked) => handleSettingChange("notifications", "security", checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Privacy & Security */}
        <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-orange-600" />
              Privacy & Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Eye className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="profile-visible">Profile Visibility</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Make your profile visible to colleagues</p>
                  </div>
                </div>
                <Switch
                  id="profile-visible"
                  checked={settings.privacy.profileVisible}
                  onCheckedChange={(checked) => handleSettingChange("privacy", "profileVisible", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="status-visible">Online Status</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Show when you're online or away</p>
                  </div>
                </div>
                <Switch
                  id="status-visible"
                  checked={settings.privacy.statusVisible}
                  onCheckedChange={(checked) => handleSettingChange("privacy", "statusVisible", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <EyeOff className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="activity-visible">Activity Tracking</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Allow activity tracking for analytics</p>
                  </div>
                </div>
                <Switch
                  id="activity-visible"
                  checked={settings.privacy.activityVisible}
                  onCheckedChange={(checked) => handleSettingChange("privacy", "activityVisible", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <div className="space-y-0.5">
                    <Label htmlFor="contact-visible">Contact Information</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Show contact info in directory</p>
                  </div>
                </div>
                <Switch
                  id="contact-visible"
                  checked={settings.privacy.contactInfoVisible}
                  onCheckedChange={(checked) => handleSettingChange("privacy", "contactInfoVisible", checked)}
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <Label className="text-base font-medium">Data Management</Label>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" onClick={exportData} className="bg-transparent">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </Button>
                <Button variant="outline" className="bg-transparent">
                  <Upload className="w-4 h-4 mr-2" />
                  Import Data
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Regional & Language */}
        <Card className="border-0 shadow-lg bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-orange-600" />
              Regional & Language
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="language">Language</Label>
                <Select
                  value={settings.preferences.language}
                  onValueChange={(value) => handleSettingChange("preferences", "language", value)}
                >
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                    <SelectItem value="zh">中文</SelectItem>
                    <SelectItem value="ja">日本語</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timezone">Timezone</Label>
                <Select
                  value={settings.preferences.timezone}
                  onValueChange={(value) => handleSettingChange("preferences", "timezone", value)}
                >
                  <SelectTrigger id="timezone">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="America/New_York">Eastern Time</SelectItem>
                    <SelectItem value="America/Chicago">Central Time</SelectItem>
                    <SelectItem value="America/Denver">Mountain Time</SelectItem>
                    <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    <SelectItem value="Europe/London">GMT</SelectItem>
                    <SelectItem value="Europe/Paris">CET</SelectItem>
                    <SelectItem value="Asia/Tokyo">JST</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date-format">Date Format</Label>
                <Select
                  value={settings.preferences.dateFormat}
                  onValueChange={(value) => handleSettingChange("preferences", "dateFormat", value)}
                >
                  <SelectTrigger id="date-format">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                    <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                    <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                    <SelectItem value="DD MMM YYYY">DD MMM YYYY</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="time-format">Time Format</Label>
                <Select
                  value={settings.preferences.timeFormat}
                  onValueChange={(value) => handleSettingChange("preferences", "timeFormat", value)}
                >
                  <SelectTrigger id="time-format">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="12h">12 Hour</SelectItem>
                    <SelectItem value="24h">24 Hour</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency</Label>
              <Select
                value={settings.preferences.currency}
                onValueChange={(value) => handleSettingChange("preferences", "currency", value)}
              >
                <SelectTrigger id="currency">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD - US Dollar</SelectItem>
                  <SelectItem value="EUR">EUR - Euro</SelectItem>
                  <SelectItem value="GBP">GBP - British Pound</SelectItem>
                  <SelectItem value="JPY">JPY - Japanese Yen</SelectItem>
                  <SelectItem value="CAD">CAD - Canadian Dollar</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button className="bg-gradient-to-r from-orange-500 to-amber-600 text-white shadow-lg hover:shadow-xl transition-all duration-300">
          <Save className="w-4 h-4 mr-2" />
          Save All Settings
        </Button>
      </div>
    </div>
  )
}
