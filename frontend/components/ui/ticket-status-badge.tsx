import { Badge } from "@/components/ui/badge"
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  XCircle, 
  ArrowUpRight,
  Play,
  MessageSquare
} from "lucide-react"

interface TicketStatusBadgeProps {
  status: string
  className?: string
}

export function TicketStatusBadge({ status, className = "" }: TicketStatusBadgeProps) {
  const getStatusConfig = (statusCode: string) => {
    switch (statusCode.toLowerCase()) {
      case 'open':
        return {
          label: 'Open',
          variant: 'default' as const,
          icon: Clock,
          className: 'bg-blue-100 text-blue-800 border-blue-200'
        }
      case 'in_progress':
      case 'in-progress':
        return {
          label: 'In Progress',
          variant: 'secondary' as const,
          icon: Play,
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200'
        }
      case 'resolved':
        return {
          label: 'Resolved',
          variant: 'secondary' as const,
          icon: CheckCircle,
          className: 'bg-green-100 text-green-800 border-green-200'
        }
      case 'closed':
        return {
          label: 'Closed',
          variant: 'secondary' as const,
          icon: CheckCircle,
          className: 'bg-gray-100 text-gray-800 border-gray-200'
        }
      case 'escalated':
        return {
          label: 'Escalated',
          variant: 'destructive' as const,
          icon: ArrowUpRight,
          className: 'bg-orange-100 text-orange-800 border-orange-200'
        }
      case 'cancelled':
        return {
          label: 'Cancelled',
          variant: 'destructive' as const,
          icon: XCircle,
          className: 'bg-red-100 text-red-800 border-red-200'
        }
      case 'pending_vendor':
        return {
          label: 'Pending Vendor',
          variant: 'outline' as const,
          icon: AlertTriangle,
          className: 'bg-purple-100 text-purple-800 border-purple-200'
        }
      case 'pending_user':
        return {
          label: 'Pending User',
          variant: 'outline' as const,
          icon: MessageSquare,
          className: 'bg-indigo-100 text-indigo-800 border-indigo-200'
        }
      default:
        return {
          label: status,
          variant: 'outline' as const,
          icon: Clock,
          className: 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }
  }

  const config = getStatusConfig(status)
  const IconComponent = config.icon

  return (
    <Badge 
      variant={config.variant} 
      className={`flex items-center gap-1 ${config.className} ${className}`}
    >
      <IconComponent className="h-3 w-3" />
      {config.label}
    </Badge>
  )
} 