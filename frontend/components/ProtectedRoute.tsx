"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
  const { isAuthenticated, isInitialized, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isInitialized && !isLoading) {
      if (requireAuth && !isAuthenticated) {
        // User is not authenticated, redirect to login
        router.push('/')
      } else if (!requireAuth && isAuthenticated) {
        // User is authenticated but on login page, redirect to dashboard
        router.push('/dashboard')
      }
    }
  }, [isAuthenticated, isInitialized, isLoading, requireAuth, router])

  // Show loading spinner while checking authentication
  if (!isInitialized || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // If we require auth and user is not authenticated, don't render children
  if (requireAuth && !isAuthenticated) {
    return null
  }

  // If we don't require auth and user is authenticated, don't render children
  if (!requireAuth && isAuthenticated) {
    return null
  }

  // Render children when authentication state matches requirements
  return <>{children}</>
} 