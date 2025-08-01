import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, AlertCircle, XCircle } from "lucide-react";
import { Timesheet } from "@/lib/types";

interface TimesheetStatusBadgeProps {
  status: Timesheet['StatusCode'];
  className?: string;
}

export function TimesheetStatusBadge({ status, className = "" }: TimesheetStatusBadgeProps) {
  const getStatusConfig = (status: Timesheet['StatusCode']) => {
    switch (status) {
      case 'Draft':
        return {
          label: 'Draft',
          icon: Clock,
          className: 'bg-gray-100 text-gray-700 border-gray-300',
          iconClassName: 'text-gray-500'
        };
      case 'Submitted':
        return {
          label: 'Submitted',
          icon: Clock,
          className: 'bg-blue-100 text-blue-700 border-blue-300',
          iconClassName: 'text-blue-500'
        };
      case 'Approved':
        return {
          label: 'Approved',
          icon: CheckCircle,
          className: 'bg-green-100 text-green-700 border-green-300',
          iconClassName: 'text-green-500'
        };
      case 'Rejected':
        return {
          label: 'Rejected',
          icon: XCircle,
          className: 'bg-red-100 text-red-700 border-red-300',
          iconClassName: 'text-red-500'
        };
      default:
        return {
          label: status,
          icon: AlertCircle,
          className: 'bg-gray-100 text-gray-700 border-gray-300',
          iconClassName: 'text-gray-500'
        };
    }
  };

  const config = getStatusConfig(status);
  const IconComponent = config.icon;

  return (
    <Badge 
      variant="outline" 
      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium ${config.className} ${className}`}
    >
      <IconComponent className={`w-3 h-3 ${config.iconClassName}`} />
      {config.label}
    </Badge>
  );
} 