"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import useUserInfo from "@/hooks/use-user-info"

export default function withRBAC<P>(
  WrappedComponent: React.ComponentType<P>,
  allowedRoles: string[],
) {
  return function RBACGuard(props: P) {
    const { userInfo, loading } = useUserInfo()
    const router = useRouter()

    const isAllowed = userInfo && allowedRoles.includes(userInfo.type)

    // Always run this effect (even while loading) so hook order is stable
    useEffect(() => {
      if (!loading && userInfo && !isAllowed) {
        router.replace("/dashboard")
      }
    }, [loading, userInfo, isAllowed, router])

    if (loading) return null
    if (!userInfo) return null // still loading or redirected
    if (!isAllowed) return <div className="p-6">Access denied</div>

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return <WrappedComponent {...(props as any)} />
  }
} 