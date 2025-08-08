import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"
import { formatDistanceToNow } from "date-fns"
import { MessageSquare, User, Edit, Trash2 } from "lucide-react"
import { Comment } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { Textarea } from "@/components/ui/textarea"

interface LeaveCommentProps {
  comment: Comment
  className?: string
  onEdit?: (commentId: number, newText: string) => Promise<void>
  onDelete?: (commentId: number) => Promise<void>
  canEdit?: boolean
  canDelete?: boolean
}

export function LeaveComment({ 
  comment, 
  className = "", 
  onEdit, 
  onDelete, 
  canEdit = false, 
  canDelete = false 
}: LeaveCommentProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editText, setEditText] = useState(comment.comment_text)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const getInitials = (name?: string) => {
    if (!name) return 'U'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true })
    } catch {
      return 'Unknown time'
    }
  }

  const handleEdit = async () => {
    if (!onEdit || !editText.trim()) return
    
    setIsSubmitting(true)
    try {
      await onEdit(comment.comment_id, editText.trim())
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to edit comment:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    
    if (confirm('Are you sure you want to delete this comment?')) {
      setIsSubmitting(true)
      try {
        await onDelete(comment.comment_id)
      } catch (error) {
        console.error('Failed to delete comment:', error)
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const getRoleColor = (role?: string) => {
    switch (role?.toLowerCase()) {
      case 'manager':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
      case 'hr':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
      case 'employee':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  return (
    <Card className={`mb-4 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs">
              {getInitials(comment.commenter_name)}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MessageSquare className="h-3 w-3" />
                <span className="font-medium">
                  {comment.commenter_name}
                </span>
                {comment.commenter_role && (
                  <span className={`text-xs px-2 py-1 rounded-full ${getRoleColor(comment.commenter_role)}`}>
                    {comment.commenter_role}
                  </span>
                )}
              </div>
              <span className="text-xs text-muted-foreground">
                {formatDate(comment.created_at)}
              </span>
              {comment.is_edited && (
                <span className="text-xs text-muted-foreground">(edited)</span>
              )}
            </div>
            
            {isEditing ? (
              <div className="space-y-2">
                <Textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="min-h-[80px]"
                  placeholder="Edit your comment..."
                />
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    onClick={handleEdit}
                    disabled={isSubmitting || !editText.trim()}
                  >
                    {isSubmitting ? 'Saving...' : 'Save'}
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      setIsEditing(false)
                      setEditText(comment.comment_text)
                    }}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-sm text-foreground whitespace-pre-wrap">
                {comment.comment_text}
              </div>
            )}

            {(canEdit || canDelete) && !isEditing && (
              <div className="flex gap-2 mt-2">
                {canEdit && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setIsEditing(true)}
                    className="h-6 px-2 text-xs"
                  >
                    <Edit className="h-3 w-3 mr-1" />
                    Edit
                  </Button>
                )}
                {canDelete && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleDelete}
                    disabled={isSubmitting}
                    className="h-6 px-2 text-xs text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 