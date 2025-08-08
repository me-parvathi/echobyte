import { format, startOfWeek, addDays, isToday, isSameDay, isWeekend } from 'date-fns';
import { DailyEntryFormData, WeeklyTimesheetFormData, Timesheet } from './types';

// Date utilities
export function getWeekStartDate(date: Date): Date {
  return startOfWeek(date, { weekStartsOn: 1 }); // Monday
}

export function getWeekEndDate(date: Date): Date {
  return addDays(getWeekStartDate(date), 6); // Sunday
}

export function isCurrentWeek(date: Date): boolean {
  const today = new Date();
  const weekStart = getWeekStartDate(today);
  const weekEnd = getWeekEndDate(today);
  return date >= weekStart && date <= weekEnd;
}

export function isPastWeek(date: Date): boolean {
  const today = new Date();
  const weekStart = getWeekStartDate(today);
  return date < weekStart;
}

export function getWeekRange(date: Date): { start: Date; end: Date } {
  return {
    start: getWeekStartDate(date),
    end: getWeekEndDate(date)
  };
}

export function getLastNWeeks(n: number): Date[] {
  const weeks: Date[] = [];
  const today = new Date();
  
  for (let i = 0; i < n; i++) {
    const weekStart = addDays(getWeekStartDate(today), -7 * i);
    weeks.push(weekStart);
  }
  
  return weeks;
}

// Validation utilities
export function validateWorkDate(date: Date): boolean {
  // Only Monday-Friday are valid work days
  const dayOfWeek = date.getDay();
  return dayOfWeek >= 1 && dayOfWeek <= 5; // Monday = 1, Friday = 5
}

export function validateHours(hours: number): boolean {
  return hours >= 0 && hours <= 24;
}

export function validateDailyEntry(entry: DailyEntryFormData): string[] {
  const errors: string[] = [];
  
  const workDate = new Date(entry.WorkDate);
  if (!validateWorkDate(workDate)) {
    errors.push('Work date must be Monday-Friday');
  }
  
  if (!validateHours(entry.HoursWorked)) {
    errors.push('Hours must be between 0 and 24');
  }
  
  if (entry.HoursWorked > 0 && !entry.TaskDescription?.trim()) {
    errors.push('Task description is required when hours are entered');
  }
  
  return errors;
}

export function validateWeeklyTimesheet(timesheet: WeeklyTimesheetFormData): string[] {
  const errors: string[] = [];
  
  // Validate week dates
  const weekStart = new Date(timesheet.WeekStartDate);
  const weekEnd = new Date(timesheet.WeekEndDate);
  
  if (weekStart.getDay() !== 1) { // Monday
    errors.push('Week start date must be Monday');
  }
  
  if (weekEnd.getDay() !== 0) { // Sunday
    errors.push('Week end date must be Sunday');
  }
  
  // Validate all daily entries
  timesheet.details.forEach((entry, index) => {
    const entryErrors = validateDailyEntry(entry);
    entryErrors.forEach(error => {
      errors.push(`Day ${index + 1}: ${error}`);
    });
  });
  
  return errors;
}

export function isWeekComplete(entries: DailyEntryFormData[]): boolean {
  // Check if all weekdays (Monday-Friday) have entries
  const weekdays = entries.filter(entry => {
    const dayOfWeek = new Date(entry.WorkDate).getDay();
    return dayOfWeek >= 1 && dayOfWeek <= 5;
  });
  
  return weekdays.length >= 5; // At least 5 weekdays
}

export function canSubmitTimesheet(timesheet: Timesheet): boolean {
  // Can submit if status is Draft and has details
  return timesheet.StatusCode === 'Draft' && 
         Boolean(timesheet.details) && 
         timesheet.details!.length > 0;
}

// Business logic
export function calculateTotalHours(entries: DailyEntryFormData[]): number {
  return entries.reduce((total, entry) => total + entry.HoursWorked, 0);
}

export function calculateOvertimeHours(entries: DailyEntryFormData[]): number {
  const totalHours = calculateTotalHours(entries);
  return Math.max(totalHours - 40, 0);
}

export function getTimesheetStatus(timesheet: Timesheet): Timesheet['StatusCode'] {
  return timesheet.StatusCode;
}

export function isEditableWeek(date: Date): boolean {
  return isCurrentWeek(date);
}

export function isViewableWeek(date: Date): boolean {
  return isCurrentWeek(date) || isPastWeek(date);
}

// New function to check if a week is within the allowed submission range
export function isWithinSubmissionRange(date: Date): boolean {
  const today = new Date();
  const targetMonth = date.getMonth();
  const targetYear = date.getFullYear();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  
  // Must be in the same month and year
  if (targetMonth !== currentMonth || targetYear !== currentYear) {
    return false;
  }
  
  // Must not be more than 4 weeks back from current week
  const currentWeekStart = getWeekStartDate(today);
  const targetWeekStart = getWeekStartDate(date);
  const weeksDiff = Math.floor((currentWeekStart.getTime() - targetWeekStart.getTime()) / (7 * 24 * 60 * 60 * 1000));
  
  return weeksDiff >= 0 && weeksDiff <= 4;
}

// Get available weeks for selection (current week + up to 4 previous weeks in same month)
export function getAvailableWeeks(): Array<{ startDate: Date; endDate: Date; label: string; isCurrent: boolean }> {
  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  const weeks: Array<{ startDate: Date; endDate: Date; label: string; isCurrent: boolean }> = [];
  
  // Start from current week
  let weekStart = getWeekStartDate(today);
  
  for (let i = 0; i <= 4; i++) {
    const weekEnd = getWeekEndDate(weekStart);
    
    // Only include weeks in the same month
    if (weekStart.getMonth() === currentMonth && weekStart.getFullYear() === currentYear) {
      weeks.push({
        startDate: weekStart,
        endDate: weekEnd,
        label: formatWeekRange(weekStart, weekEnd),
        isCurrent: i === 0
      });
    }
    
    // Move to previous week
    weekStart = addDays(weekStart, -7);
  }
  
  return weeks.reverse(); // Return in chronological order
}

// Format utilities
export function formatDate(date: Date): string {
  return format(date, 'yyyy-MM-dd');
}

export function formatWeekRange(startDate: Date, endDate: Date): string {
  return `${format(startDate, 'MMM d')} - ${format(endDate, 'MMM d, yyyy')}`;
}

export function formatStatus(status: Timesheet['StatusCode']): string {
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
}

// Convert form data to API format
export function convertToDailyEntryFormData(
  dayKey: string, 
  hours: string, 
  project: string, 
  description: string, 
  overtime: boolean,
  date: Date
): DailyEntryFormData {
  return {
    WorkDate: formatDate(date),
    ProjectCode: project || null,
    TaskDescription: description || '',
    HoursWorked: parseFloat(hours) || 0,
    IsOvertime: overtime
  };
}

// Convert API data to form format
export function convertFromTimesheetDetail(detail: any): {
  hours: string;
  project: string;
  description: string;
  overtime: boolean;
} {
  return {
    hours: detail.HoursWorked?.toString() || '0',
    project: detail.ProjectCode || '',
    description: detail.TaskDescription || '',
    overtime: Boolean(detail.IsOvertime)
  };
} 