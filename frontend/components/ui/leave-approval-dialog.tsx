import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MessageSquare, AlertTriangle, CheckCircle, XCircle } from "lucide-react"
import { LeaveApplication, LeaveConflict, Comment, CommentCreate } from "@/lib/types"
import { LeaveComment } from "./leave-comment"
import { useLeaveApproval } from "@/hooks/use-leave-approval"
import { useToast } from "@/hooks/use-toast"

interface LeaveApprovalDialogProps {
  leaveApplication: LeaveApplication
  isOpen: boolean
  onClose: () => void
  onApprovalComplete: (updatedApplication: LeaveApplication) => void
  userInfo: {
    employeeId: number
    name: string
    type: string
  }
  isManager?: boolean
  isHR?: boolean
}

export function LeaveApprovalDialog({
  leaveApplication,
  isOpen,
  onClose,
  onApprovalComplete,
  userInfo,
  isManager = false,
  isHR = false
}: LeaveApprovalDialogProps) {
  const [approvalComment, setApprovalComment] = useState("")
  const [regularComment, setRegularComment] = useState("")
  const [comments, setComments] = useState<Comment[]>([])
  const [loadingComments, setLoadingComments] = useState(false)
  const [submittingComment, setSubmittingComment] = useState(false)
  const [conflict, setConflict] = useState<LeaveConflict | null>(null)
  const [showConflictWarning, setShowConflictWarning] = useState(false)

  const { toast } = useToast()
  const {
    loading,
    error,
    approveAsManager,
    approveAsHR,
    checkLeaveConflicts,
    getComments,
    addComment,
    updateComment,
    deleteComment
  } = useLeaveApproval()

  // Load comments when dialog opens
  useEffect(() => {
    if (isOpen && leaveApplication.LeaveApplicationID) {
      loadComments()
    }
  }, [isOpen, leaveApplication.LeaveApplicationID])

  // Check for conflicts when dialog opens (for managers)
  useEffect(() => {
    if (isOpen && isManager && userInfo.employeeId) {
      checkConflicts()
    }
  }, [isOpen, isManager, userInfo.employeeId])

  const loadComments = async () => {
    setLoadingComments(true)
    try {
      const result = await getComments(leaveApplication.LeaveApplicationID)
      setComments(result.comments)
    } catch (error) {
      console.error('Failed to load comments:', error)
      toast({
        title: "Error",
        description: "Failed to load comments",
        variant: "destructive"
      })
    } finally {
      setLoadingComments(false)
    }
  }

  const checkConflicts = async () => {
    try {
      const conflictResult = await checkLeaveConflicts(
        leaveApplication.StartDate,
        leaveApplication.EndDate,
        userInfo.employeeId
      )
      setConflict(conflictResult)
      if (conflictResult.has_conflict) {
        setShowConflictWarning(true)
      }
    } catch (error) {
      console.error('Failed to check conflicts:', error)
    }
  }

  const handleApproval = async (action: "approve" | "reject") => {
    if (!userInfo.employeeId) {
      toast({
        title: "Error",
        description: "User information not available",
        variant: "destructive"
      })
      return
    }

    try {
      let result: LeaveApplication

      if (isManager) {
        result = await approveAsManager(leaveApplication.LeaveApplicationID, {
          approval_status: action === "approve" ? "Approved" : "Rejected",
          comments: approvalComment,
          manager_id: userInfo.employeeId
        })
      } else if (isHR) {
        result = await approveAsHR(leaveApplication.LeaveApplicationID, {
          approval_status: action === "approve" ? "Approved" : "Rejected",
          comments: approvalComment,
          hr_approver_id: userInfo.employeeId
        })
      } else {
        throw new Error("User is not authorized to approve leaves")
      }

      toast({
        title: "Success",
        description: `Leave application ${action}d successfully`,
      })

      onApprovalComplete(result)
      onClose()
    } catch (error) {
      console.error('Approval failed:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to process approval",
        variant: "destructive"
      })
    }
  }

  const handleAddComment = async () => {
    if (!regularComment.trim()) return

    setSubmittingComment(true)
    try {
      const newComment = await addComment(leaveApplication.LeaveApplicationID, {
        comment_text: regularComment.trim(),
        commenter_role: isManager ? "Manager" : isHR ? "HR" : "Employee"
      })

      setComments(prev => [newComment, ...prev])
      setRegularComment("")
      
      toast({
        title: "Success",
        description: "Comment added successfully",
      })
    } catch (error) {
      console.error('Failed to add comment:', error)
      toast({
        title: "Error",
        description: "Failed to add comment",
        variant: "destructive"
      })
    } finally {
      setSubmittingComment(false)
    }
  }

  const handleEditComment = async (commentId: number, newText: string) => {
    try {
      const updatedComment = await updateComment(commentId, { comment_text: newText })
      setComments(prev => prev.map(c => c.comment_id === commentId ? updatedComment : c))
      
      toast({
        title: "Success",
        description: "Comment updated successfully",
      })
    } catch (error) {
      console.error('Failed to update comment:', error)
      toast({
        title: "Error",
        description: "Failed to update comment",
        variant: "destructive"
      })
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    try {
      await deleteComment(commentId)
      setComments(prev => prev.filter(c => c.comment_id !== commentId))
      
      toast({
        title: "Success",
        description: "Comment deleted successfully",
      })
    } catch (error) {
      console.error('Failed to delete comment:', error)
      toast({
        title: "Error",
        description: "Failed to delete comment",
        variant: "destructive"
      })
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Submitted":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
      case "Manager-Approved":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
      case "HR-Approved":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
      case "Rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400"
    }
  }

  const canApprove = () => {
    if (isManager) {
      return leaveApplication.StatusCode === "Submitted"
    }
    if (isHR) {
      return leaveApplication.StatusCode === "Manager-Approved"
    }
    return false
  }

  const canReject = () => {
    if (isManager) {
      return leaveApplication.StatusCode === "Submitted"
    }
    if (isHR) {
      return leaveApplication.StatusCode === "Manager-Approved"
    }
    return false
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Leave Approval</h2>
            <Button variant="ghost" onClick={onClose} size="sm">
              ✕
            </Button>
          </div>

          {/* Leave Application Details */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Leave Application #{leaveApplication.LeaveApplicationID}</span>
                <Badge className={getStatusColor(leaveApplication.StatusCode)}>
                  {leaveApplication.StatusCode}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Employee</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {leaveApplication.employee?.FirstName} {leaveApplication.employee?.LastName}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Leave Type</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {leaveApplication.leave_type?.LeaveTypeName}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Duration</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(leaveApplication.StartDate).toLocaleDateString()} - {new Date(leaveApplication.EndDate).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Days</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {leaveApplication.NumberOfDays} days
                  </p>
                </div>
              </div>
              
              {leaveApplication.Reason && (
                <div>
                  <Label className="text-sm font-medium">Reason</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                    {leaveApplication.Reason}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Conflict Warning */}
          {showConflictWarning && conflict?.has_conflict && (
            <Alert className="mb-6 border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/20">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-800 dark:text-orange-200">
                <strong>Warning:</strong> Multiple employees under your management have overlapping leave dates:
                <ul className="mt-2 space-y-1">
                  {conflict.conflicting_employees?.map((emp, index) => (
                    <li key={index} className="text-sm">
                      • {emp.employee_name} ({emp.leave_type}) - {emp.leave_dates.join(', ')}
                    </li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* Approval Section */}
          {(canApprove() || canReject()) && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  {isManager ? "Manager Approval" : "HR Approval"}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="approval-comment">Approval Comments (Optional)</Label>
                  <Textarea
                    id="approval-comment"
                    placeholder="Add comments for the employee..."
                    value={approvalComment}
                    onChange={(e) => setApprovalComment(e.target.value)}
                    className="mt-1"
                    rows={3}
                  />
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleApproval("approve")}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {loading ? "Processing..." : "Approve"}
                  </Button>
                  <Button
                    onClick={() => handleApproval("reject")}
                    disabled={loading}
                    variant="destructive"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    {loading ? "Processing..." : "Reject"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comments Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Comments
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Comment */}
              <div className="space-y-2">
                <Label>Add Comment</Label>
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Add a comment..."
                    value={regularComment}
                    onChange={(e) => setRegularComment(e.target.value)}
                    className="flex-1"
                    rows={3}
                  />
                  <Button 
                    onClick={handleAddComment}
                    disabled={!regularComment.trim() || submittingComment}
                  >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    {submittingComment ? 'Adding...' : 'Add'}
                  </Button>
                </div>
              </div>

              <Separator />

              {/* Comments List */}
              <div className="space-y-4">
                {loadingComments ? (
                  <div className="text-center py-4 text-gray-500">Loading comments...</div>
                ) : comments.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">No comments yet</div>
                ) : (
                  comments.map((comment) => (
                    <LeaveComment
                      key={comment.comment_id}
                      comment={comment}
                      onEdit={handleEditComment}
                      onDelete={handleDeleteComment}
                      canEdit={comment.commenter_id === userInfo.employeeId}
                      canDelete={comment.commenter_id === userInfo.employeeId}
                    />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
} 