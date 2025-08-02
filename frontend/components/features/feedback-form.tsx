"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, Shield, MessageSquare, User } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useFeedback } from "@/hooks/use-feedback"
import { GENERAL_FEEDBACK_CATEGORIES, EmployeeFeedbackCreate } from "@/lib/types"

export default function FeedbackForm() {
  const { 
    feedbackTypes, 
    targets, 
    currentUserManager,
    submitting, 
    error, 
    submitFeedback, 
    getFeedbackTypes, 
    getTargets,
    getCurrentUserManager,
    clearError,
    setErrorState
  } = useFeedback()

  const [formData, setFormData] = useState({
    feedbackTypeCode: "",
    category: "",
    subject: "",
    feedbackText: "",
    targetManagerID: undefined as number | undefined,
    targetDepartmentID: undefined as number | undefined
  })

  const [selectedTargets, setSelectedTargets] = useState<number[]>([])

  // Load data on component mount
  useEffect(() => {
    getFeedbackTypes()
    getTargets()
    getCurrentUserManager()
  }, [])

  // Auto-populate user's manager when available
  useEffect(() => {
    if (currentUserManager && selectedTargets.length === 0) {
      setSelectedTargets([currentUserManager.EmployeeID])
    }
  }, [currentUserManager])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    if (!formData.feedbackText.trim()) {
      return
    }

    // Only require the auto-selected manager, no additional targets needed
    if (selectedTargets.length === 0) {
      setErrorState("Please ensure your manager is selected")
      return
    }

    const feedbackData: EmployeeFeedbackCreate = {
      FeedbackTypeCode: formData.feedbackTypeCode,
      Category: formData.category,
      Subject: formData.subject,
      FeedbackText: formData.feedbackText,
      TargetManagerID: selectedTargets[0], // Primary target (manager)
      TargetDepartmentID: formData.targetDepartmentID
    }

    const success = await submitFeedback(feedbackData)
    if (success) {
      // Reset form
      setFormData({
        feedbackTypeCode: "",
        category: "",
        subject: "",
        feedbackText: "",
        targetManagerID: undefined,
        targetDepartmentID: undefined
      })
      setSelectedTargets([])
    }
  }

  const handleTargetSelect = (targetId: number) => {
    if (selectedTargets.includes(targetId)) {
      setSelectedTargets(selectedTargets.filter(id => id !== targetId))
    } else {
      // Allow only one target (the manager)
      setSelectedTargets([targetId])
    }
  }

  const getTargetById = (id: number) => {
    return targets.find(target => target.EmployeeID === id)
  }

  return (
    <div className="space-y-6">
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-blue-500" />
            <CardTitle>General Feedback Form</CardTitle>
          </div>
          <CardDescription>Share your thoughts and help us improve the workplace</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Feedback Type */}
            <div>
              <Label htmlFor="feedbackType">Feedback Type *</Label>
              <Select 
                value={formData.feedbackTypeCode} 
                onValueChange={(value) => setFormData({...formData, feedbackTypeCode: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select feedback type" />
                </SelectTrigger>
                <SelectContent>
                  {Array.isArray(feedbackTypes) && feedbackTypes.map((type) => (
                    <SelectItem key={type.FeedbackTypeCode} value={type.FeedbackTypeCode}>
                      {type.FeedbackTypeName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Category */}
            <div>
              <Label htmlFor="category">Category *</Label>
              <Select 
                value={formData.category} 
                onValueChange={(value) => setFormData({...formData, category: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {GENERAL_FEEDBACK_CATEGORIES.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Subject */}
            <div>
              <Label htmlFor="subject">Subject</Label>
              <Input
                id="subject"
                placeholder="Brief description of your feedback"
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value})}
              />
            </div>

            {/* Target Selection */}
            <div>
              <Label>Target Recipient</Label>
              
              {/* Auto-populated Manager */}
              {currentUserManager && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <User className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Your Manager (Auto-selected)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`target-${currentUserManager.EmployeeID}`}
                      checked={selectedTargets.includes(currentUserManager.EmployeeID)}
                      onChange={() => handleTargetSelect(currentUserManager.EmployeeID)}
                      className="rounded"
                    />
                    <Label htmlFor={`target-${currentUserManager.EmployeeID}`} className="flex-1 cursor-pointer">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{currentUserManager.EmployeeName}</span>
                        <div className="flex gap-1">
                          {currentUserManager.isManager && <Badge variant="secondary">Manager</Badge>}
                          {currentUserManager.isHR && <Badge variant="outline">HR</Badge>}
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {currentUserManager.DesignationName} • {currentUserManager.DepartmentName}
                      </div>
                    </Label>
                  </div>
                </div>
              )}

              {/* Selected Target Summary */}
              {selectedTargets.length > 0 && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-sm font-medium text-green-800 mb-2">
                    Selected Recipient:
                  </div>
                  <div className="space-y-1">
                    {selectedTargets.map(targetId => {
                      const target = getTargetById(targetId)
                      return target ? (
                        <div key={targetId} className="text-sm text-green-700">
                          • {target.EmployeeName} ({target.DesignationName})
                        </div>
                      ) : null
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Feedback Text */}
            <div>
              <Label htmlFor="feedback">Your Feedback *</Label>
              <Textarea
                id="feedback"
                placeholder="Share your detailed feedback here. Be specific about your concerns and suggestions..."
                value={formData.feedbackText}
                onChange={(e) => setFormData({...formData, feedbackText: e.target.value})}
                rows={6}
                className="resize-none"
              />
            </div>

            {/* Privacy Notice */}
            <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>
                <strong>Privacy Notice:</strong> Your feedback is anonymous and will be handled confidentially. 
                Only authorized HR personnel and managers will have access to this information.
              </AlertDescription>
            </Alert>

            <Button type="submit" className="w-full" disabled={submitting || !formData.feedbackText.trim() || selectedTargets.length === 0}>
              {submitting ? "Submitting..." : "Submit Feedback"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
