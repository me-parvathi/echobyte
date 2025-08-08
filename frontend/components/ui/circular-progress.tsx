"use client"

import type React from "react"

interface CircularProgressProps {
  value: number
  max: number
  size?: number
  strokeWidth?: number
  className?: string
  children?: React.ReactNode
}

export function CircularProgress({
  value,
  max,
  size = 80,
  strokeWidth = 6,
  className = "",
  children,
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const percentage = (value / max) * 100
  const strokeDasharray = `${circumference} ${circumference}`
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getGradientId = () => `gradient-${Math.random().toString(36).substr(2, 9)}`
  const gradientId = getGradientId()

  const getColors = () => {
    if (percentage >= 90) return { from: "#ef4444", to: "#dc2626" } // red
    if (percentage >= 75) return { from: "#f97316", to: "#ea580c" } // orange
    if (percentage >= 50) return { from: "#f59e0b", to: "#d97706" } // amber
    return { from: "#10b981", to: "#059669" } // emerald
  }

  const colors = getColors()

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg className="transform -rotate-90 drop-shadow-sm" width={size} height={size}>
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors.from} />
            <stop offset="100%" stopColor={colors.to} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#f1f5f9"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="drop-shadow-sm"
        />

        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out filter drop-shadow-sm"
          style={{
            filter: "drop-shadow(0 0 4px rgba(249, 115, 22, 0.3))",
          }}
        />
      </svg>

      <div className="absolute inset-0 flex items-center justify-center">
        {children || (
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900">{value}</div>
            <div className="text-xs text-gray-500 -mt-1">of {max}h</div>
          </div>
        )}
      </div>
    </div>
  )
}
