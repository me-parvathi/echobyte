import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"
import { formatDistanceToNow } from "date-fns"
import { MessageSquare, User } from "lucide-react"
import { TicketActivity, EmployeeInfo } from "@/lib/types"

interface TicketCommentProps {
  comment: TicketActivity
  className?: string
}

export function TicketComment({ comment, className = "" }: TicketCommentProps) {
  const isComment = comment.ActivityType === 'Comment'
  
  if (!isComment) return null

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

  return (
    <Card className={`mb-4 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs">
              {getInitials(comment.performed_by?.FirstName + ' ' + comment.performed_by?.LastName)}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MessageSquare className="h-3 w-3" />
                <span className="font-medium">
                  {comment.performed_by?.FirstName} {comment.performed_by?.LastName}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">
                {formatDate(comment.PerformedAt)}
              </span>
            </div>
            
            <div className="text-sm text-foreground whitespace-pre-wrap">
              {comment.ActivityDetails}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 