"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Building2, Eye, EyeOff, Loader2 } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { ProtectedRoute } from "@/components/ProtectedRoute"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login, isLoading } = useAuth()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Clear any existing errors
    setError(null)
    
    // Basic validation
    if (!username.trim()) {
      setError("Please enter your username or email")
      return
    }
    
    if (!password.trim()) {
      setError("Please enter your password")
      return
    }
    
    console.log("🚀 Login form submitted with:", { username, password: "***" })
    
    const success = await login({ username, password })
    console.log("📋 Login result:", success ? "SUCCESS" : "FAILED")
    
    if (!success) {
      // The error message is already set by the useAuth hook
      // We don't need to set a generic error here
    }
  }

  return (
    <ProtectedRoute requireAuth={false}>
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
                    onChange={(e) => {
                      setUsername(e.target.value)
                      // Clear error when user starts typing
                      if (error) {
                        setError(null)
                      }
                    }}
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
                      onChange={(e) => {
                        setPassword(e.target.value)
                        // Clear error when user starts typing
                        if (error) {
                          setError(null)
                        }
                      }}
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
                  <div className="p-4 text-sm bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    </div>
                  </div>
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

           
              
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
