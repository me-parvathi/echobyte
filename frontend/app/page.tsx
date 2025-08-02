"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Building2, Eye, EyeOff, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const { login, loading: isLoading, error } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Redirect to dashboard only when token AND basic user info exist
    const token = localStorage.getItem("access_token")
    const userEmail = localStorage.getItem("userEmail")
    const userType = localStorage.getItem("userType")

    console.log("🔍 Login page - Checking auth status:", { 
      hasToken: !!token, 
      userEmail, 
      userType 
    })

    if (token && userEmail && userType) {
      console.log("✅ User authenticated, redirecting to dashboard")
      router.push("/dashboard")
    } else {
      console.log("❌ User not authenticated, staying on login")
    }
  }, [router])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log("🚀 Login form submitted with:", { username, password: "***" })
    
    const result = await login({ username, password })
    console.log("📋 Login result:", result ? "SUCCESS" : "FAILED")
    
    if (result) {
      console.log("✅ Login successful, redirecting to dashboard")
      router.push("/dashboard")
    } else {
      console.log("❌ Login failed, staying on login page")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-2xl border-0 bg-white/90 backdrop-blur-xl">
          <CardHeader className="text-center pb-8">
            <div className="mx-auto mb-6 w-16 h-16 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-indigo-900 via-purple-900 to-pink-900 bg-clip-text text-transparent">
              Welcome Back
            </CardTitle>
            <CardDescription className="text-gray-600 text-lg">Sign in to access your employee portal</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="identifier" className="text-sm font-medium text-gray-700">
                  Username or Email
                </Label>
                <Input
                  id="identifier"
                  type="text"
                  placeholder="your.username or your.email@company.com"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="h-12 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-12 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500 pr-12"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-12 px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
              </div>

              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg">{error}</div>
              )}

              <Button
                type="submit"
                className="w-full h-12 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>

            <div className="text-center">
              <Button variant="link" className="text-sm text-gray-600 hover:text-indigo-600">
                Forgot your password?
              </Button>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Demo accounts: john.doe@company.com, jane.manager@company.com, hr.admin@company.com,
                it.support@company.com
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
