import { api } from './api';
import { 
  TimesheetBatchResponse, 
  Timesheet, 
  TimesheetDetail, 
  DailyEntryFormData, 
  WeeklyTimesheetFormData,
  BulkSaveResponse,
  TimesheetSubmissionResponse
} from './types';

export class TimesheetApiService {
  // Get current employee's timesheet batch data
  static async getMyTimesheetBatch(
    weekStartDate?: string, 
    includeHistory: boolean = true, 
    historyLimit: number = 10
  ): Promise<TimesheetBatchResponse> {
    const params = new URLSearchParams();
    if (weekStartDate) params.append('week_start_date', weekStartDate);
    params.append('include_history', includeHistory.toString());
    params.append('history_limit', historyLimit.toString());
    
    return api.get<TimesheetBatchResponse>(`/timesheets/my/batch?${params.toString()}`);
  }

  // Get timesheet history with pagination
  static async getMyTimesheetHistory(
    skip: number = 0, 
    limit: number = 10
  ): Promise<{ items: Timesheet[]; total_count: number; page: number; size: number; has_next: boolean; has_previous: boolean }> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    return api.get(`/timesheets/my/timesheets?${params.toString()}`);
  }

  // Get specific daily entry
  static async getMyDailyEntry(workDate: string): Promise<TimesheetDetail | null> {
    try {
      return await api.get<TimesheetDetail>(`/timesheets/my/daily/${workDate}`);
    } catch (error) {
      if (error instanceof Error && error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  // Create or update daily entry
  static async createMyDailyEntry(dailyData: DailyEntryFormData): Promise<TimesheetDetail> {
    return api.post<TimesheetDetail>('/timesheets/my/daily', dailyData);
  }

  // Create weekly timesheet
  static async createMyWeeklyTimesheet(weeklyData: WeeklyTimesheetFormData): Promise<Timesheet> {
    return api.post<Timesheet>('/timesheets/my/weekly', weeklyData);
  }

  // Update timesheet
  static async updateMyTimesheet(timesheetId: number, updateData: Partial<Timesheet>): Promise<Timesheet> {
    return api.put<Timesheet>(`/timesheets/my/timesheet/${timesheetId}`, updateData);
  }

  // Submit timesheet
  static async submitMyTimesheet(timesheetId: number): Promise<TimesheetSubmissionResponse> {
    return api.post<TimesheetSubmissionResponse>(`/timesheets/my/timesheet/${timesheetId}/submit`);
  }

  // Bulk save daily entries
  static async bulkSaveDailyEntries(entries: DailyEntryFormData[]): Promise<BulkSaveResponse> {
    const promises = entries.map(entry => this.createMyDailyEntry(entry));
    const results = await Promise.allSettled(promises);
    
    const savedEntries: TimesheetDetail[] = [];
    const errors: string[] = [];
    
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        savedEntries.push(result.value);
      } else {
        errors.push(`Failed to save entry for ${entries[index].WorkDate}: ${result.reason}`);
      }
    });
    
    return {
      success: errors.length === 0,
      saved_entries: savedEntries,
      errors: errors
    };
  }

  // Get timesheet status (for polling)
  static async getTimesheetStatus(timesheetId: number): Promise<Timesheet['StatusCode']> {
    const timesheet = await api.get<Timesheet>(`/timesheets/my/timesheet/${timesheetId}`);
    return timesheet.StatusCode;
  }
} 