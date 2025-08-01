"use client"

import EmployeeProfile from "@/components/features/employee-profile"
import useUserInfo from "@/hooks/use-user-info"

export default function ProfilePage() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <EmployeeProfile userInfo={userInfo} />
} 