"use client"

import SettingsPanel from "@/components/features/settings-panel"
import useUserInfo from "@/hooks/use-user-info"

export default function SettingsPage() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <SettingsPanel userInfo={userInfo} />
} 