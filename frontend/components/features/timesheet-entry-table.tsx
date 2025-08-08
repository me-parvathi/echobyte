"use client"

import React, { ChangeEvent, useCallback, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { convertToDailyEntryFormData, isWeekComplete } from "@/lib/timesheet-utils"
import { DailyEntryFormData } from "@/lib/types"
import { useSaveDailyEntry, useBulkSaveEntries } from "@/hooks/use-timesheet"
import { useCreateWeeklyTimesheet } from "@/hooks/use-weekly-timesheet"
import { useToast } from "@/hooks/use-toast"

// Types --------------------------------------------------
export interface WeekDayInfo {
  key: string
  label: string
  date: string // day of month
  fullDate: string // yyyy-MM-dd
  dateObj: Date
  isToday: boolean
  isSelected?: boolean
}

export interface TimeEntriesState {
  [key: string]: {
    hours: string
    project: string
    description: string
    overtime: boolean
  }
}

interface TimesheetEntryTableProps {
  weekDays: WeekDayInfo[]
  timeEntries: TimeEntriesState
  setTimeEntries: React.Dispatch<React.SetStateAction<TimeEntriesState>>
  projects: string[]
  selectedWeekStart: Date
  isWithinSubmissionRange: boolean
}

// Component ----------------------------------------------
const TimesheetEntryTable: React.FC<TimesheetEntryTableProps> = ({
  weekDays,
  timeEntries,
  setTimeEntries,
  projects,
  selectedWeekStart,
  isWithinSubmissionRange,
}) => {
  const { toast } = useToast()
  const { saveEntry, loading: savingDay } = useSaveDailyEntry()
  const { bulkSave, loading: savingWeek } = useBulkSaveEntries()
  const {
    createWeeklyTimesheet,
    loading: creatingWeekly,
  } = useCreateWeeklyTimesheet()

  const isProcessing = savingDay || savingWeek || creatingWeekly

  // Handlers ---------------------------------------------
  const handleInputChange = useCallback(
    (dayKey: string, field: keyof TimeEntriesState[keyof TimeEntriesState], value: string | boolean) => {
      setTimeEntries(prev => ({
        ...prev,
        [dayKey]: {
          ...prev[dayKey],
          [field]: value,
        },
      }))
    },
    [setTimeEntries],
  )

  const handleSaveDay = useCallback(
    async (day: WeekDayInfo) => {
      const entry = timeEntries[day.key]
      const formData: DailyEntryFormData = convertToDailyEntryFormData(
        day.key,
        entry.hours,
        entry.project,
        entry.description,
        entry.overtime,
        day.dateObj,
      )

      try {
        await saveEntry(formData)
        toast.toast({
          title: `Saved ${day.label}`,
          description: `${entry.hours || 0} hours saved as draft`,
        })
      } catch (err) {
        toast.toast({
          title: `Failed to save ${day.label}`,
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        })
      }
    },
    [saveEntry, timeEntries, toast],
  )

  const handleSaveWeek = useCallback(async () => {
    const entries: DailyEntryFormData[] = weekDays.map(day => {
      const entry = timeEntries[day.key]
      return convertToDailyEntryFormData(
        day.key,
        entry.hours,
        entry.project,
        entry.description,
        entry.overtime,
        day.dateObj,
      )
    })

    // Allow saving even if week incomplete, but warn.
    const weekComplete = isWeekComplete(entries)

    try {
      // Prefer backend weekly endpoint for creating timesheet with details
      await createWeeklyTimesheet({
        WeekStartDate: weekDays[0].fullDate,
        WeekEndDate: weekDays[weekDays.length - 1].fullDate,
        details: entries,
      })

      if (isWithinSubmissionRange) {
        toast.toast({
          title: weekComplete ? "Weekly timesheet saved" : "Draft saved",
          description: weekComplete
            ? "You can now submit this timesheet for approval."
            : "Fill the remaining days before submitting.",
        })
      } else {
        toast.toast({
          title: "Draft saved",
          description: "This week is outside the submission range. You can edit and save as draft only.",
        })
      }
    } catch (err) {
      toast.toast({
        title: "Failed to save week",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      })
    }
  }, [weekDays, timeEntries, createWeeklyTimesheet, toast, isWithinSubmissionRange])

  // UI ----------------------------------------------------
  const renderRows = useMemo(
    () =>
      weekDays.map(day => {
        const entry = timeEntries[day.key]
        return (
          <tr key={day.key} className="border-b last:border-0">
            <td className="py-2 px-3 whitespace-nowrap font-medium">
              {day.label}
              {day.isToday && <Badge className="ml-2">Today</Badge>}
            </td>
            <td className="py-2 px-3">
              <Input
                type="number"
                min={0}
                max={24}
                step={0.25}
                value={entry.hours}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  handleInputChange(day.key, "hours", e.target.value)
                }
                className="w-24"
              />
            </td>
            <td className="py-2 px-3">
              <select
                value={entry.project}
                onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                  handleInputChange(day.key, "project", e.target.value)
                }
                className="border rounded px-2 py-1 w-40 text-sm"
              >
                <option value="">Select</option>
                {projects.map(p => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </td>
            <td className="py-2 px-3 w-full">
              <Textarea
                value={entry.description}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
                  handleInputChange(day.key, "description", e.target.value)
                }
                placeholder="Work description"
                rows={2}
              />
            </td>
            <td className="py-2 px-3 text-center">
              <Checkbox
                checked={entry.overtime}
                onCheckedChange={(checked: boolean) => handleInputChange(day.key, "overtime", !!checked)}
              />
            </td>
            <td className="py-2 px-3 text-right">
              <Button
                size="sm"
                onClick={() => handleSaveDay(day)}
                disabled={isProcessing}
              >
                Save
              </Button>
            </td>
          </tr>
        )
      }),
    [weekDays, timeEntries, projects, handleInputChange, handleSaveDay, isProcessing],
  )

  return (
    <div className="border rounded-lg overflow-hidden bg-white shadow">
      <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold">Daily Entries</h3>
          {!isWithinSubmissionRange && (
            <Badge variant="secondary" className="text-xs">
              Outside submission range - Draft only
            </Badge>
          )}
        </div>
        <Button onClick={handleSaveWeek} disabled={isProcessing}>
          {isProcessing ? "Saving..." : "Save Week"}
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left">Day</th>
              <th className="px-3 py-2 text-left">Hours</th>
              <th className="px-3 py-2 text-left">Project</th>
              <th className="px-3 py-2 text-left">Description</th>
              <th className="px-3 py-2 text-center">OT</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>{renderRows}</tbody>
        </table>
      </div>
    </div>
  )
}

export default React.memo(TimesheetEntryTable)
