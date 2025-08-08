import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MessageSquare, X } from "lucide-react"
import { LeaveApplication, Comment, CommentCreate } from "@/lib/types"
import { LeaveComment } from "./leave-comment"
import { useLeaveApproval } from "@/hooks/use-leave-approval"
import { useToast } from "@/hooks/use-toast"
import { getCurrentUserInfo } from "@/lib/utils"

interface LeaveCommentsDialogProps {
  leaveApplication: LeaveApplication
  isOpen: boolean
  onClose: () => void
}

export function LeaveCommentsDialog({
  leaveApplication,
  isOpen,
  onClose
}: LeaveCommentsDialogProps) {
  const [comments, setComments] = useState<Comment[]>([])
  const [loadingComments, setLoadingComments] = useState(false)
  const [submittingComment, setSubmittingComment] = useState(false)
  const [newComment, setNewComment] = useState("")

  const { toast } = useToast()
  const {
    getComments,
    addComment,
    updateComment,
    deleteComment
  } = useLeaveApproval()

  const currentUser = getCurrentUserInfo()

  // Load comments when dialog opens
  useEffect(() => {
    if (isOpen && leaveApplication.LeaveApplicationID) {
      loadComments()
    }
  }, [isOpen, leaveApplication.LeaveApplicationID])

  const loadComments = async () => {
    setLoadingComments(true)
    try {
      const result = await getComments(leaveApplication.LeaveApplicationID)
      // Sort comments by creation date (newest first)
      const sortedComments = result.comments.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      setComments(sortedComments)
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

  const handleAddComment = async () => {
    if (!newComment.trim()) return

    setSubmittingComment(true)
    try {
      const newCommentData = await addComment(leaveApplication.LeaveApplicationID, {
        comment_text: newComment.trim(),
        commenter_role: "Employee"
      })

      setComments(prev => [newCommentData, ...prev].sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ))
      setNewComment("")
      
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
      setComments(prev => prev.map(c => c.comment_id === commentId ? updatedComment : c).sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ))
      
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Leave Application Comments</h2>
            <Button variant="ghost" onClick={onClose} size="sm">
              <X className="h-4 w-4" />
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
                <div>
                  <Label className="text-sm font-medium">Status</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {leaveApplication.StatusCode}
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

          {/* Comments Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Comments ({comments.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Comment */}
              <div className="space-y-2">
                <Label>Add Comment</Label>
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Add a comment to your leave application..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="flex-1"
                    rows={3}
                  />
                  <Button 
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || submittingComment}
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
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-500">Loading comments...</p>
                  </div>
                ) : comments.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No comments yet</p>
                    <p className="text-sm mt-2">Be the first to add a comment to this leave application</p>
                  </div>
                ) : (
                  comments.map((comment) => (
                    <LeaveComment
                      key={comment.comment_id}
                      comment={comment}
                      onEdit={handleEditComment}
                      onDelete={handleDeleteComment}
                      canEdit={comment.commenter_id === currentUser?.employeeId}
                      canDelete={comment.commenter_id === currentUser?.employeeId}
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