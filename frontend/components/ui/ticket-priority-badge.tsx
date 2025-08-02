import { Badge } from "@/components/ui/badge"
import { AlertTriangle, AlertCircle, Clock } from "lucide-react"

interface TicketPriorityBadgeProps {
  priority: string
  className?: string
}

export function TicketPriorityBadge({ priority, className = "" }: TicketPriorityBadgeProps) {
  const getPriorityConfig = (priorityCode: string) => {
    switch (priorityCode.toLowerCase()) {
      case 'high':
      case 'critical':
        return {
          label: 'High',
          variant: 'destructive' as const,
          icon: AlertTriangle,
          className: 'bg-red-100 text-red-800 border-red-200'
        }
      case 'medium':
        return {
          label: 'Medium',
          variant: 'secondary' as const,
          icon: AlertCircle,
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200'
        }
      case 'low':
        return {
          label: 'Low',
          variant: 'outline' as const,
          icon: Clock,
          className: 'bg-green-100 text-green-800 border-green-200'
        }
      default:
        return {
          label: priority,
          variant: 'outline' as const,
          icon: Clock,
          className: 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }
  }

  const config = getPriorityConfig(priority)
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