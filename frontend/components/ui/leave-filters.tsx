import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Filter, X, Search } from 'lucide-react';
import type { LeaveType, LeaveFilterParams } from '@/lib/types';

interface LeaveFiltersProps {
  filters: LeaveFilterParams;
  onFiltersChange: (filters: LeaveFilterParams) => void;
  onClearFilters: () => void;
  leaveTypes: LeaveType[];
  loading?: boolean;
  isExpanded?: boolean;
  onToggleExpanded?: () => void;
}

export function LeaveFilters({
  filters,
  onFiltersChange,
  onClearFilters,
  leaveTypes,
  loading = false,
  isExpanded = false,
  onToggleExpanded
}: LeaveFiltersProps) {
  const handleFilterChange = (key: keyof LeaveFilterParams, value: string | number | undefined) => {
    const newFilters = { ...filters, [key]: value };
    // Remove empty values
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key as keyof LeaveFilterParams] === '' || newFilters[key as keyof LeaveFilterParams] === undefined) {
        delete newFilters[key as keyof LeaveFilterParams];
      }
    });
    onFiltersChange(newFilters);
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter className="w-5 h-5" />
            Filters
            {hasActiveFilters && (
              <Badge variant="secondary" className="ml-2">
                {Object.keys(filters).length} active
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button
                variant="outline"
                size="sm"
                onClick={onClearFilters}
                disabled={loading}
              >
                <X className="w-4 h-4 mr-1" />
                Clear All
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={onToggleExpanded}
            >
              {isExpanded ? 'Hide' : 'Show'} Filters
            </Button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date Range Filters */}
            <div className="space-y-2">
              <Label htmlFor="start-date">From Date</Label>
              <Input
                id="start-date"
                type="date"
                value={filters.start_date || ''}
                onChange={(e) => handleFilterChange('start_date', e.target.value || undefined)}
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end-date">To Date</Label>
              <Input
                id="end-date"
                type="date"
                value={filters.end_date || ''}
                onChange={(e) => handleFilterChange('end_date', e.target.value || undefined)}
                disabled={loading}
                min={filters.start_date}
              />
            </div>

            {/* Status Filter */}
            <div className="space-y-2">
              <Label htmlFor="status-filter">Status</Label>
              <Select
                value={filters.status_code || 'all'}
                onValueChange={(value) => handleFilterChange('status_code', value === 'all' ? undefined : value)}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="Draft">Draft</SelectItem>
                  <SelectItem value="Submitted">Submitted</SelectItem>
                  <SelectItem value="Manager-Approved">Manager Approved</SelectItem>
                  <SelectItem value="HR-Approved">HR Approved</SelectItem>
                  <SelectItem value="Approved">Approved</SelectItem>
                  <SelectItem value="Rejected">Rejected</SelectItem>
                  <SelectItem value="Cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Leave Type Filter */}
            <div className="space-y-2">
              <Label htmlFor="leave-type-filter">Leave Type</Label>
              <Select
                value={filters.leave_type_id?.toString() || 'all'}
                onValueChange={(value) => handleFilterChange('leave_type_id', value === 'all' ? undefined : parseInt(value))}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {leaveTypes.map((type) => (
                    <SelectItem key={type.LeaveTypeID} value={type.LeaveTypeID.toString()}>
                      {type.LeaveTypeName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              <span className="text-sm text-muted-foreground">Active filters:</span>
              {filters.start_date && (
                <Badge variant="outline" className="text-xs">
                  From: {new Date(filters.start_date).toLocaleDateString()}
                </Badge>
              )}
              {filters.end_date && (
                <Badge variant="outline" className="text-xs">
                  To: {new Date(filters.end_date).toLocaleDateString()}
                </Badge>
              )}
              {filters.status_code && (
                <Badge variant="outline" className="text-xs">
                  Status: {filters.status_code}
                </Badge>
              )}
              {filters.leave_type_id && (
                <Badge variant="outline" className="text-xs">
                  Type: {leaveTypes.find(t => t.LeaveTypeID === filters.leave_type_id)?.LeaveTypeName || 'Unknown'}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
} 