// frontend/components/test-api.tsx
"use client"

import { useApi } from "@/hooks/use-api"
import { api } from "@/lib/api"

export function TestApi() {
  const { data, loading, error, refetch } = useApi('/health', { immediate: false })

  const handleTest = async () => {
    console.log('�� Testing direct API call...')
    console.log('Environment:', {
      NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
      NODE_ENV: process.env.NODE_ENV
    })
    
    try {
      console.log('📡 Making direct API call to /health...')
      const result = await api.get('/health')
      console.log('✅ Direct API call successful:', result)
    } catch (err) {
      console.error('❌ Direct API call failed:', err)
    }
  }

  const handleTestWithHook = () => {
    console.log('🔄 Testing with useApi hook...')
    refetch()
  }

  const handleTestDifferentEndpoints = async () => {
    console.log('🧪 Testing different endpoints...')
    
    const endpoints = [
      '/health',
      '/info', 
      '/health',
      '/'
    ]
    
    for (const endpoint of endpoints) {
      try {
        console.log(`�� Testing ${endpoint}...`)
        const result = await api.get(endpoint)
        console.log(`✅ ${endpoint} successful:`, result)
      } catch (err) {
        console.log(`❌ ${endpoint} failed:`, err)
      }
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <button 
          onClick={handleTest} 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test Direct API Call
        </button>
        <button 
          onClick={handleTestWithHook} 
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Test with Hook
        </button>
        <button 
          onClick={handleTestDifferentEndpoints} 
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
        >
          Test All Endpoints
        </button>
      </div>
      
      <div className="text-sm space-y-2">
        <div>
          <strong>Environment:</strong> {process.env.NEXT_PUBLIC_API_BASE || 'Not set'}
        </div>
        <div>
          <strong>Hook Status:</strong> {loading ? 'Loading...' : error ? 'Error' : data ? 'Success' : 'Ready'}
        </div>
        {error && (
          <div className="text-red-600 bg-red-50 p-3 rounded">
            <strong>Hook Error:</strong> {error.message}
          </div>
        )}
        {data && (
          <div className="text-green-600 bg-green-50 p-3 rounded">
            <strong>Hook Success:</strong> <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  )
}