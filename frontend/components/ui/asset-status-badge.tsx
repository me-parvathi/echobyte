import { Badge } from "@/components/ui/badge"
import { CheckCircle, AlertTriangle, XCircle, Clock, Wrench, Archive } from "lucide-react"
import { cn } from "@/lib/utils"

interface AssetStatusBadgeProps {
  status: string
  className?: string
  showIcon?: boolean
}

const statusConfig = {
  'Assigned': {
    label: 'Assigned',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: CheckCircle,
    iconColor: 'text-blue-600'
  },
  'Available': {
    label: 'Available',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-600'
  },
  'In-Stock': {
    label: 'In Stock',
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: CheckCircle,
    iconColor: 'text-gray-600'
  },
  'Maintenance': {
    label: 'Maintenance',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: Wrench,
    iconColor: 'text-yellow-600'
  },
  'Decommissioning': {
    label: 'Decommissioning',
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: Clock,
    iconColor: 'text-orange-600'
  },
  'Retired': {
    label: 'Retired',
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: Archive,
    iconColor: 'text-red-600'
  }
}

export function AssetStatusBadge({ status, className, showIcon = true }: AssetStatusBadgeProps) {
  const config = statusConfig[status as keyof typeof statusConfig] || {
    label: status,
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: CheckCircle,
    iconColor: 'text-gray-600'
  }

  const Icon = config.icon

  return (
    <Badge 
      variant="outline" 
      className={cn(
        config.color,
        "border font-medium",
        className
      )}
    >
      {showIcon && <Icon className={cn("w-3 h-3 mr-1", config.iconColor)} />}
      {config.label}
    </Badge>
  )
} 