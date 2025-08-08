"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ChevronLeft, ChevronRight, Calendar } from "lucide-react"
import { getAvailableWeeks } from "@/lib/timesheet-utils"

interface WeekSelectorProps {
  selectedWeekStart: Date
  onWeekChange: (weekStart: Date) => void
  className?: string
}

export default function WeekSelector({ selectedWeekStart, onWeekChange, className = "" }: WeekSelectorProps) {
  const availableWeeks = getAvailableWeeks()
  const currentIndex = availableWeeks.findIndex(week => 
    week.startDate.getTime() === selectedWeekStart.getTime()
  )

  const handlePreviousWeek = () => {
    if (currentIndex > 0) {
      onWeekChange(availableWeeks[currentIndex - 1].startDate)
    }
  }

  const handleNextWeek = () => {
    if (currentIndex < availableWeeks.length - 1) {
      onWeekChange(availableWeeks[currentIndex + 1].startDate)
    }
  }

  const handleWeekSelect = (weekStart: Date) => {
    onWeekChange(weekStart)
  }

  if (availableWeeks.length === 0) {
    return (
      <div className={`flex items-center justify-center p-4 text-gray-500 ${className}`}>
        <Calendar className="w-4 h-4 mr-2" />
        <span>No available weeks</span>
      </div>
    )
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Button
        variant="outline"
        size="sm"
        onClick={handlePreviousWeek}
        disabled={currentIndex <= 0}
        className="px-2"
      >
        <ChevronLeft className="w-4 h-4" />
      </Button>

      <div className="flex items-center gap-2">
        <Calendar className="w-4 h-4 text-gray-600" />
        <span className="font-medium text-sm">
          {availableWeeks[currentIndex]?.label || "Select Week"}
        </span>
        {availableWeeks[currentIndex]?.isCurrent && (
          <Badge variant="secondary" className="text-xs">
            Current
          </Badge>
        )}
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={handleNextWeek}
        disabled={currentIndex >= availableWeeks.length - 1}
        className="px-2"
      >
        <ChevronRight className="w-4 h-4" />
      </Button>

      {/* Week dropdown for quick selection */}
      <div className="relative">
        <select
          value={selectedWeekStart.toISOString()}
          onChange={(e) => handleWeekSelect(new Date(e.target.value))}
          className="border rounded px-2 py-1 text-sm bg-white"
        >
          {availableWeeks.map((week, index) => (
            <option key={week.startDate.toISOString()} value={week.startDate.toISOString()}>
              {week.label} {week.isCurrent ? "(Current)" : ""}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
} 