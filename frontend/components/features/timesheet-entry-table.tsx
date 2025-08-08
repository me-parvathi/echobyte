"use client";

import React, { ChangeEvent, useCallback, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  convertToDailyEntryFormData,
  isWeekComplete,
} from "@/lib/timesheet-utils";
import { DailyEntryFormData, TimesheetDetail } from "@/lib/types";
import { useSaveDailyEntry, useBulkSaveEntries } from "@/hooks/use-timesheet";
import { useCreateWeeklyTimesheet } from "@/hooks/use-weekly-timesheet";
import { useToast } from "@/hooks/use-toast";
import { useProjects } from "@/hooks/use-projects";

// ---------- TEMP FALLBACK NAME→ID MAP (edit IDs to match your DB) ----------
const FALLBACK_NAME_TO_ID: Record<string, number> = {
  "Project Alpha": 101,
  "Project Beta": 102,
  "Project Gamma": 103,
  // add more if needed
};

// ---------- Helpers ----------
function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}
function isEmptyDay(e: {
  hours: string;
  project: string;
  description: string;
  overtime: boolean;
}) {
  const hrsNum = Number(e.hours);
  return (!hrsNum || hrsNum <= 0) && !e.description?.trim() && !e.overtime;
}

// ---------- Types ----------
export interface WeekDayInfo {
  key: string;
  label: string;
  date: string;
  fullDate: string;
  dateObj: Date;
  isToday: boolean;
  isSelected?: boolean;
}

export interface TimeEntriesState {
  [key: string]: {
    hours: string; // keep as string
    project: string; // keep the NAME like "Project Alpha"
    description: string;
    overtime: boolean;
  };
}

interface TimesheetEntryTableProps {
  weekDays: WeekDayInfo[];
  timeEntries: TimeEntriesState;
  setTimeEntries: React.Dispatch<React.SetStateAction<TimeEntriesState>>;
  projects: string[]; // keep passing just names
  selectedWeekStart: Date;
  isWithinSubmissionRange: boolean;
}

// ---------- Component ----------
const TimesheetEntryTable: React.FC<TimesheetEntryTableProps> = ({
  weekDays,
  timeEntries,
  setTimeEntries,
  projects,
  selectedWeekStart,
  isWithinSubmissionRange,
}) => {
  const { toast } = useToast();
  const { saveEntry, loading: savingDay } = useSaveDailyEntry();
  const { bulkSave, loading: savingWeek } = useBulkSaveEntries();
  const { createWeeklyTimesheet, loading: creatingWeekly } =
    useCreateWeeklyTimesheet();

  // Load real {id,name} list; we’ll prefer this map when present
  const { nameToId, loading: loadingProjectMap } = useProjects();

  const isProcessing = savingDay || savingWeek || creatingWeekly;

  // resolve a project name to an ID using server map first, then fallback map
  const getProjectId = useCallback(
    (name: string | null | undefined) => {
      if (!name) return null;
      return (
        (nameToId.get(name) as number | string | undefined) ??
        FALLBACK_NAME_TO_ID[name] ??
        null
      );
    },
    [nameToId]
  );

  // Input change handler
  const handleInputChange = useCallback(
    (
      dayKey: string,
      field: keyof TimeEntriesState[keyof TimeEntriesState],
      value: string | boolean
    ) => {
      setTimeEntries((prev) => ({
        ...prev,
        [dayKey]: {
          ...prev[dayKey],
          [field]: value,
        },
      }));
    },
    [setTimeEntries]
  );

  // Save Day (keeps name in state; maps to ID on submit)
  const handleSaveDay = useCallback(
    async (day: WeekDayInfo) => {
      const entry = timeEntries[day.key];

      const hoursNum = Number(entry.hours);
      if (Number.isNaN(hoursNum) || hoursNum < 0 || hoursNum > 24) {
        toast({
          title: `Invalid hours`,
          description: `Enter 0–24 hours for ${day.label}`,
          variant: "destructive",
        });
        return;
      }
      if (!entry.project) {
        toast({
          title: `Missing project`,
          description: `Select a project for ${day.label}`,
          variant: "destructive",
        });
        return;
      }

      const projectId = getProjectId(entry.project);
      if (projectId == null) {
        toast({
          title: "Unknown project",
          description: `“${entry.project}” isn't mapped to a ProjectId yet.`,
          variant: "destructive",
        });
        return;
      }

      const formData: DailyEntryFormData = convertToDailyEntryFormData(
        day.key,
        String(hoursNum),
        String(projectId),
        entry.description,
        entry.overtime,
        day.dateObj
      );

      try {
        const saved: TimesheetDetail = await saveEntry(formData as any);

        // reflect instantly in UI
        setTimeEntries((prev) => ({
          ...prev,
          [day.key]: {
            hours: String((saved as any).Hours ?? hoursNum ?? "0"),
            project:
              (saved as any).ProjectName ??
              (saved as any).ProjectId ??
              entry.project,
            description: (saved as any).Description ?? entry.description ?? "",
            overtime: Boolean(
              (saved as any).IsOvertime ??
                (saved as any).Overtime ??
                entry.overtime ??
                false
            ),
          },
        }));

        toast({
          title: `Saved ${day.label}`,
          description: `${
            (saved as any).Hours ?? hoursNum ?? 0
          } hours saved as draft`,
        });
      } catch (err: any) {
        toast({
          title: `Failed to save ${day.label}`,
          description: err?.message || "Validation error",
          variant: "destructive",
        });
      }
    },
    [saveEntry, timeEntries, setTimeEntries, toast, getProjectId]
  );

  // Save Week (filters empties + maps every project name to id)
  const handleSaveWeek = useCallback(async () => {
    const raw = weekDays.map((day) => ({ day, entry: timeEntries[day.key] }));
    const nonEmpty = raw.filter(({ entry }) => !isEmptyDay(entry));

    if (nonEmpty.length === 0) {
      toast({
        title: "Nothing to save",
        description: "Add hours or notes for at least one day.",
      });
      return;
    }

    const bad: string[] = [];
    for (const { day, entry } of nonEmpty) {
      const hoursNum = Number(entry.hours);
      if (Number.isNaN(hoursNum) || hoursNum < 0 || hoursNum > 24) {
        bad.push(`${day.label}: hours must be 0–24`);
      }
      const pid = getProjectId(entry.project);
      if (pid == null) {
        bad.push(`${day.label}: unknown project “${entry.project}”`);
      }
    }
    if (bad.length) {
      toast({
        title: "Fix validation errors",
        description: bad.slice(0, 4).join(" • "),
        variant: "destructive",
      });
      return;
    }

    const details: DailyEntryFormData[] = nonEmpty.map(({ day, entry }) => {
      const pid = getProjectId(entry.project)!;
      return convertToDailyEntryFormData(
        day.key,
        String(Number(entry.hours)),
        String(pid),
        entry.description,
        entry.overtime,
        day.dateObj
      );
    });

    try {
      const payload = {
        WeekStartDate: toIsoDate(weekDays[0].dateObj),
        WeekEndDate: toIsoDate(weekDays[weekDays.length - 1].dateObj),
        details,
      };

      await createWeeklyTimesheet(payload as any);

      const weekComplete = isWeekComplete(details as any);
      toast({
        title: weekComplete ? "Weekly timesheet saved" : "Draft saved",
        description: weekComplete
          ? "You can now submit this timesheet for approval."
          : "Fill the remaining days before submitting.",
      });
    } catch (err: any) {
      toast({
        title: "Failed to save week",
        description: err?.message || "Validation error from server",
        variant: "destructive",
      });
    }
  }, [weekDays, timeEntries, createWeeklyTimesheet, toast, getProjectId]);

  // ---------- UI ----------
  const renderRows = useMemo(
    () =>
      weekDays.map((day) => {
        const entry = timeEntries[day.key];
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
                {projects.map((name) => (
                  <option key={name} value={name}>
                    {name}
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
                onCheckedChange={(checked: boolean) =>
                  handleInputChange(day.key, "overtime", !!checked)
                }
              />
            </td>
            <td className="py-2 px-3 text-right">
              <Button
                size="sm"
                onClick={() => handleSaveDay(day)}
                disabled={isProcessing || loadingProjectMap}
              >
                {loadingProjectMap ? "Loading..." : "Save"}
              </Button>
            </td>
          </tr>
        );
      }),
    [
      weekDays,
      timeEntries,
      projects,
      handleInputChange,
      handleSaveDay,
      isProcessing,
      loadingProjectMap,
    ]
  );

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
        <Button
          onClick={handleSaveWeek}
          disabled={isProcessing || loadingProjectMap}
        >
          {isProcessing || loadingProjectMap ? "Saving..." : "Save Week"}
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
  );
};

export default React.memo(TimesheetEntryTable);
