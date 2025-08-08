"use client"

import EmployeeDirectory from "@/components/features/employee-directory"
import useUserInfo from "@/hooks/use-user-info"

export default function DirectoryPage() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <EmployeeDirectory userInfo={userInfo} />
} 