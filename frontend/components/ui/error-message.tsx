interface ErrorMessageProps {
    error: Error;
    onRetry?: () => void;
  }
  
  export function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-red-600 font-medium mb-2">Something went wrong</div>
          <div className="text-gray-600 text-sm mb-4">{error.message}</div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }