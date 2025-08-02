"use client"

import { useState } from "react"
import { api } from "@/lib/api"

export default function TestApiPage() {
  const [result, setResult] = useState<string>("")
  const [loading, setLoading] = useState(false)

  const testLogin = async () => {
    setLoading(true)
    setResult("Testing login...")
    
    try {
      console.log("🧪 Testing login API...")
      const response = await api.post("/api/auth/login", {
        username: "john.doe@company.com",
        password: "password123"
      })
      console.log("✅ Login test successful:", response)
      setResult(`Login successful! Token: ${response.access_token?.substring(0, 20)}...`)
    } catch (error: any) {
      console.error("❌ Login test failed:", error)
      setResult(`Login failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testUserInfo = async () => {
    setLoading(true)
    setResult("Testing user info...")
    
    try {
      console.log("🧪 Testing user info API...")
      const response = await api.get("/api/auth/me")
      console.log("✅ User info test successful:", response)
      setResult(`User info: ${JSON.stringify(response, null, 2)}`)
    } catch (error: any) {
      console.error("❌ User info test failed:", error)
      setResult(`User info failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const checkLocalStorage = () => {
    const token = localStorage.getItem("access_token")
    const userEmail = localStorage.getItem("userEmail")
    const userType = localStorage.getItem("userType")
    
    setResult(`LocalStorage:
Token: ${token ? "Present" : "Missing"}
UserEmail: ${userEmail || "Missing"}
UserType: ${userType || "Missing"}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Test Page</h1>
        
        <div className="space-y-4">
          <button
            onClick={testLogin}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Test Login
          </button>
          
          <button
            onClick={testUserInfo}
            disabled={loading}
            className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50 ml-2"
          >
            Test User Info
          </button>
          
          <button
            onClick={checkLocalStorage}
            className="px-4 py-2 bg-purple-500 text-white rounded ml-2"
          >
            Check LocalStorage
          </button>
        </div>
        
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Result:</h2>
          <pre className="bg-white p-4 rounded border text-sm overflow-auto">
            {result || "No test run yet"}
          </pre>
        </div>
      </div>
    </div>
  )
}