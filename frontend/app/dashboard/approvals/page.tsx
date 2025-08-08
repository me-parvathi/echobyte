"use client"

import ManagerApprovals from "@/components/features/manager-approvals"
import useUserInfo from "@/hooks/use-user-info"
import withRBAC from "@/lib/withRBAC"

function ApprovalsContent() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <ManagerApprovals userInfo={userInfo} />
}

export default withRBAC(ApprovalsContent, ["manager", "hr"]) 