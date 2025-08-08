"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, Eye, EyeOff, Filter, MessageSquare, Calendar, User } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useFeedback } from "@/hooks/use-feedback"
import { EmployeeFeedback, FeedbackFilterParams } from "@/lib/types"

export default function FeedbackViewer() {
  const { 
    feedback, 
    feedbackTypes, 
    departments,
    loading, 
    error, 
    getFeedback, 
    getFeedbackTypes, 
    getDepartments,
    markAsRead,
    clearError 
  } = useFeedback()

  const [filters, setFilters] = useState<FeedbackFilterParams>({
    feedback_type_code: undefined,
    target_manager_id: undefined,
    target_department_id: undefined,
    is_read: undefined
  })

  const [selectedFeedback, setSelectedFeedback] = useState<EmployeeFeedback | null>(null)

  // Load data on component mount
  useEffect(() => {
    getFeedbackTypes()
    getDepartments()
    getFeedback()
  }, [])

  const handleFilterChange = (key: keyof FeedbackFilterParams, value: string | number | boolean | undefined) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    getFeedback(newFilters)
  }

  const handleMarkAsRead = async (feedbackId: number) => {
    const success = await markAsRead(feedbackId)
    if (success) {
      // Refresh the feedback list
      getFeedback(filters)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getFeedbackTypeName = (typeCode: string) => {
    const type = feedbackTypes.find(t => t.FeedbackTypeCode === typeCode)
    return type?.FeedbackTypeName || typeCode
  }

  const getDepartmentName = (deptId: number) => {
    const dept = departments.find(d => d.DepartmentID === deptId)
    return dept?.DepartmentName || 'Unknown'
  }

  return (
    <div className="space-y-6">
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-green-500" />
            <CardTitle>Feedback Viewer</CardTitle>
          </div>
          <CardDescription>View and manage feedback from employees</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <Label>Feedback Type</Label>
              <Select 
                value={filters.feedback_type_code || "all"} 
                onValueChange={(value) => handleFilterChange('feedback_type_code', value === "all" ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All types</SelectItem>
                  {Array.isArray(feedbackTypes) && feedbackTypes.map((type) => (
                    <SelectItem key={type.FeedbackTypeCode} value={type.FeedbackTypeCode}>
                      {type.FeedbackTypeName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Department</Label>
              <Select 
                value={filters.target_department_id?.toString() || "all"} 
                onValueChange={(value) => handleFilterChange('target_department_id', value === "all" ? undefined : parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All departments" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All departments</SelectItem>
                  {Array.isArray(departments) && departments.map((dept) => (
                    <SelectItem key={dept.DepartmentID} value={dept.DepartmentID.toString()}>
                      {dept.DepartmentName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Read Status</Label>
              <Select 
                value={filters.is_read?.toString() || "all"} 
                onValueChange={(value) => handleFilterChange('is_read', value === "all" ? undefined : value === 'true')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All feedback" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All feedback</SelectItem>
                  <SelectItem value="false">Unread</SelectItem>
                  <SelectItem value="true">Read</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setFilters({})
                  getFeedback()
                }}
                className="w-full"
              >
                <Filter className="h-4 w-4 mr-2" />
                Clear Filters
              </Button>
            </div>
          </div>

          {/* Feedback List */}
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-600">Loading feedback...</p>
            </div>
          ) : feedback.length === 0 ? (
            <div className="text-center py-8">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No feedback found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Array.isArray(feedback) && feedback.map((item) => (
                <Card key={item.FeedbackID} className={`${!item.IsRead ? 'border-l-4 border-l-blue-500 bg-blue-50' : ''}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={item.IsRead ? "secondary" : "default"}>
                            {item.IsRead ? "Read" : "New"}
                          </Badge>
                          <Badge variant="outline">
                            {getFeedbackTypeName(item.FeedbackTypeCode)}
                          </Badge>
                          {item.Category && (
                            <Badge variant="outline">
                              {item.Category}
                            </Badge>
                          )}
                        </div>
                        
                        {item.Subject && (
                          <h3 className="font-semibold text-lg mb-2">{item.Subject}</h3>
                        )}
                        
                        <p className="text-gray-700 mb-3 line-clamp-3">{item.FeedbackText}</p>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            {formatDate(item.FeedbackAt)}
                          </div>
                          {item.target_manager && (
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {item.target_manager.FirstName} {item.target_manager.LastName}
                            </div>
                          )}
                          {item.target_department && (
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {item.target_department.DepartmentName}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {!item.IsRead && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleMarkAsRead(item.FeedbackID)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            Mark Read
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSelectedFeedback(item)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feedback Detail Modal */}
      {selectedFeedback && (
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Feedback Details</CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedFeedback(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant={selectedFeedback.IsRead ? "secondary" : "default"}>
                  {selectedFeedback.IsRead ? "Read" : "New"}
                </Badge>
                <Badge variant="outline">
                  {getFeedbackTypeName(selectedFeedback.FeedbackTypeCode)}
                </Badge>
                {selectedFeedback.Category && (
                  <Badge variant="outline">
                    {selectedFeedback.Category}
                  </Badge>
                )}
              </div>
              
              {selectedFeedback.Subject && (
                <div>
                  <Label className="text-sm font-medium">Subject</Label>
                  <p className="text-lg font-semibold">{selectedFeedback.Subject}</p>
                </div>
              )}
              
              <div>
                <Label className="text-sm font-medium">Feedback</Label>
                <p className="text-gray-700 whitespace-pre-wrap">{selectedFeedback.FeedbackText}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label className="text-xs text-gray-500">Submitted</Label>
                  <p>{formatDate(selectedFeedback.FeedbackAt)}</p>
                </div>
                {selectedFeedback.target_manager && (
                  <div>
                    <Label className="text-xs text-gray-500">Target Manager</Label>
                    <p>{selectedFeedback.target_manager.FirstName} {selectedFeedback.target_manager.LastName}</p>
                  </div>
                )}
                {selectedFeedback.target_department && (
                  <div>
                    <Label className="text-xs text-gray-500">Target Department</Label>
                    <p>{selectedFeedback.target_department.DepartmentName}</p>
                  </div>
                )}
                {selectedFeedback.read_by && (
                  <div>
                    <Label className="text-xs text-gray-500">Read By</Label>
                    <p>{selectedFeedback.read_by.FirstName} {selectedFeedback.read_by.LastName}</p>
                  </div>
                )}
                {selectedFeedback.ReadAt && (
                  <div>
                    <Label className="text-xs text-gray-500">Read At</Label>
                    <p>{formatDate(selectedFeedback.ReadAt)}</p>
                  </div>
                )}
              </div>
              
              {!selectedFeedback.IsRead && (
                <Button
                  onClick={() => {
                    handleMarkAsRead(selectedFeedback.FeedbackID)
                    setSelectedFeedback(null)
                  }}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Mark as Read
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 