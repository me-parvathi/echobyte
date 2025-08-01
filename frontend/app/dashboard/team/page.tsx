"use client"

import TeamInfo from "@/components/features/team-info"
import useUserInfo from "@/hooks/use-user-info"

export default function TeamPage() {
  const { userInfo } = useUserInfo()
  if (!userInfo) return null
  return <TeamInfo userInfo={userInfo} />
} 