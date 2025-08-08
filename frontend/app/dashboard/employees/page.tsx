"use client"

import HRManagement from "@/components/features/hr-management"
import useUserInfo from "@/hooks/use-user-info"
import withRBAC from "@/lib/withRBAC"

function EmployeesContent() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <HRManagement userInfo={userInfo} />
}

export default withRBAC(EmployeesContent, ["hr"]) 