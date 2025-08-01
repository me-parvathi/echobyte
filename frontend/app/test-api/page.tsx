"use client"

import { TestApi } from "@/components/test-api"
export default function TestApiPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">API Infrastructure Test</h1>
      <div className="space-y-6">
        <TestApi />
        
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">Test Instructions:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Click "Test API" to make a request</li>
            <li>• Check browser console for detailed logs</li>
            <li>• Verify environment variables are loaded</li>
            <li>• Test error handling by temporarily changing API URL</li>
          </ul>
        </div>
      </div>
    </div>
  )
}