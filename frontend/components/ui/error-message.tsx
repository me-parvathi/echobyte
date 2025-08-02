import { AlertCircle } from "lucide-react"
import { Button } from "./button"

interface ErrorMessageProps {
  error: Error | string
  onRetry?: () => void
  className?: string
}

export function ErrorMessage({ error, onRetry, className = "" }: ErrorMessageProps) {
  const errorMessage = typeof error === 'string' ? error : error.message

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Something went wrong</h3>
      <p className="text-gray-600 mb-4 max-w-md">{errorMessage}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          Try Again
        </Button>
      )}
    </div>
  )
}