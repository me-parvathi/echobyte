"use client"

import { useState, useEffect } from "react"
import { CheckCircle, XCircle, AlertCircle } from "lucide-react"

interface PasswordStrengthProps {
  password: string
}

interface StrengthRequirement {
  label: string
  test: (password: string) => boolean
  icon: React.ReactNode
}

export function PasswordStrength({ password }: PasswordStrengthProps) {
  const [strength, setStrength] = useState<'weak' | 'medium' | 'strong'>('weak')

  const requirements: StrengthRequirement[] = [
    {
      label: "At least 8 characters",
      test: (pwd) => pwd.length >= 8,
      icon: <CheckCircle className="w-4 h-4" />
    },
    {
      label: "At least one uppercase letter",
      test: (pwd) => /[A-Z]/.test(pwd),
      icon: <CheckCircle className="w-4 h-4" />
    },
    {
      label: "At least one lowercase letter",
      test: (pwd) => /[a-z]/.test(pwd),
      icon: <CheckCircle className="w-4 h-4" />
    },
    {
      label: "At least one number",
      test: (pwd) => /\d/.test(pwd),
      icon: <CheckCircle className="w-4 h-4" />
    }
  ]

  useEffect(() => {
    const validRequirements = requirements.filter(req => req.test(password))
    const percentage = (validRequirements.length / requirements.length) * 100

    if (percentage === 100) {
      setStrength('strong')
    } else if (percentage >= 50) {
      setStrength('medium')
    } else {
      setStrength('weak')
    }
  }, [password])

  const getStrengthColor = () => {
    switch (strength) {
      case 'weak':
        return 'text-red-600'
      case 'medium':
        return 'text-yellow-600'
      case 'strong':
        return 'text-green-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStrengthText = () => {
    switch (strength) {
      case 'weak':
        return 'Weak'
      case 'medium':
        return 'Medium'
      case 'strong':
        return 'Strong'
      default:
        return 'Weak'
    }
  }

  const getProgressColor = () => {
    switch (strength) {
      case 'weak':
        return 'bg-red-500'
      case 'medium':
        return 'bg-yellow-500'
      case 'strong':
        return 'bg-green-500'
      default:
        return 'bg-gray-300'
    }
  }

  const getProgressWidth = () => {
    const validRequirements = requirements.filter(req => req.test(password))
    return (validRequirements.length / requirements.length) * 100
  }

  if (!password) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Password Strength</span>
        <span className={`text-sm font-medium ${getStrengthColor()}`}>
          {getStrengthText()}
        </span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor()}`}
          style={{ width: `${getProgressWidth()}%` }}
        />
      </div>

      <div className="space-y-2">
        {requirements.map((requirement, index) => {
          const isMet = requirement.test(password)
          return (
            <div key={index} className="flex items-center gap-2">
              <span className={`${isMet ? 'text-green-600' : 'text-gray-400'}`}>
                {isMet ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <XCircle className="w-4 h-4" />
                )}
              </span>
              <span className={`text-sm ${isMet ? 'text-green-600' : 'text-gray-500'}`}>
                {requirement.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
} 