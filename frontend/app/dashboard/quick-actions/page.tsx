"use client"

import QuickActions from "@/components/features/quick-actions"
import useUserInfo from "@/hooks/use-user-info"
import { useRouter } from "next/navigation"

export default function QuickActionsPage() {
  const { userInfo } = useUserInfo()
  const router = useRouter()
  if (!userInfo) return null
  return <QuickActions userInfo={userInfo} onNavigate={(id)=>router.push(`/dashboard/${id}`)} />
} 