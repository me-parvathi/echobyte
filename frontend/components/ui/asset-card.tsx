import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AssetStatusBadge } from "@/components/ui/asset-status-badge"
import { 
  Monitor, 
  Laptop, 
  Smartphone, 
  HardDrive, 
  Printer,
  Edit,
  Trash2,
  QrCode,
  User,
  MapPin,
  Calendar,
  Shield
} from "lucide-react"
import { Asset } from "@/lib/types"
import { format } from "date-fns"

interface AssetCardProps {
  asset: Asset
  onEdit?: (asset: Asset) => void
  onDelete?: (asset: Asset) => void
  onAssign?: (asset: Asset) => void
  onReturn?: (asset: Asset) => void
  showActions?: boolean
}

const assetTypeIcons = {
  'Laptop': Laptop,
  'Monitor': Monitor,
  'Mobile Phone': Smartphone,
  'Keyboard': HardDrive,
  'Mouse': HardDrive,
  'Docking Station': HardDrive,
  'Headset': HardDrive,
  'Printer': Printer,
}

export function AssetCard({ 
  asset, 
  onEdit, 
  onDelete, 
  onAssign, 
  onReturn, 
  showActions = true 
}: AssetCardProps) {
  const Icon = assetTypeIcons[asset.asset_type?.AssetTypeName as keyof typeof assetTypeIcons] || Monitor

  const isAssigned = asset.AssetStatusCode === 'Assigned'
  const hasWarranty = asset.WarrantyEndDate && new Date(asset.WarrantyEndDate) > new Date()
  const warrantyExpired = asset.WarrantyEndDate && new Date(asset.WarrantyEndDate) <= new Date()
  const warrantyExpiringSoon = asset.WarrantyEndDate && 
    new Date(asset.WarrantyEndDate) > new Date() && 
    new Date(asset.WarrantyEndDate) <= new Date(Date.now() + 4 * 30 * 24 * 60 * 60 * 1000) // 4 months

  return (
    <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
              <Icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                {asset.Model || asset.AssetTag}
              </h3>
              <p className="text-sm text-gray-600 font-mono">{asset.AssetTag}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <AssetStatusBadge status={asset.AssetStatusCode} />
          </div>
        </div>

        {/* Asset Details */}
        <div className="space-y-3 mb-4">
          {asset.SerialNumber && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Serial:</span>
              <span className="font-mono text-xs">{asset.SerialNumber}</span>
            </div>
          )}
          
          {asset.Vendor && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Vendor:</span>
              <span>{asset.Vendor}</span>
            </div>
          )}

          {asset.location && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                Location:
              </span>
              <span>{asset.location.LocationName}</span>
            </div>
          )}

          {asset.PurchaseDate && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                Purchased:
              </span>
              <span>{format(new Date(asset.PurchaseDate), 'MMM yyyy')}</span>
            </div>
          )}

          {asset.current_assignment && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 flex items-center gap-1">
                <User className="w-3 h-3" />
                Assigned to:
              </span>
              <span>
                {asset.current_assignment.employee 
                  ? `${asset.current_assignment.employee.FirstName} ${asset.current_assignment.employee.LastName}`
                  : 'Unknown'
                }
              </span>
            </div>
          )}

          {/* Warranty Status */}
          {asset.WarrantyEndDate && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 flex items-center gap-1">
                <Shield className="w-3 h-3" />
                Warranty:
              </span>
              <div className="text-right">
                <div className="text-xs text-gray-500">
                  {format(new Date(asset.WarrantyEndDate), 'MMM yyyy')}
                </div>
                              <Badge 
                variant="outline" 
                className={cn(
                  warrantyExpired
                    ? "bg-red-100 text-red-800 border-red-200" 
                    : warrantyExpiringSoon 
                      ? "bg-orange-100 text-orange-800 border-orange-200"
                      : hasWarranty 
                        ? "bg-green-100 text-green-800 border-green-200"
                        : "bg-gray-100 text-gray-800 border-gray-200"
                )}
              >
                {warrantyExpired ? 'Expired' : warrantyExpiringSoon ? 'Expiring Soon' : hasWarranty ? 'Active' : 'No Warranty'}
              </Badge>
              </div>
            </div>
          )}

          {/* Contract Status */}
          {asset.IsUnderContract && asset.ContractExpiryDate && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Contract:</span>
              <span>{format(new Date(asset.ContractExpiryDate), 'MMM yyyy')}</span>
            </div>
          )}
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex gap-2">
            {onEdit && (
              <Button size="sm" variant="outline" className="flex-1 bg-transparent" onClick={() => onEdit(asset)}>
                <Edit className="w-4 h-4 mr-1" />
                Edit
              </Button>
            )}
            
            {!isAssigned && onAssign && (
              <Button size="sm" variant="outline" className="flex-1 bg-transparent" onClick={() => onAssign(asset)}>
                <User className="w-4 h-4 mr-1" />
                Assign
              </Button>
            )}
            
            {isAssigned && onReturn && (
              <Button size="sm" variant="outline" className="flex-1 bg-transparent" onClick={() => onReturn(asset)}>
                <User className="w-4 h-4 mr-1" />
                Return
              </Button>
            )}
            
            <Button size="sm" variant="outline" className="bg-transparent">
              <QrCode className="w-4 h-4" />
            </Button>
            
            {onDelete && (
              <Button
                size="sm"
                variant="outline"
                className="text-red-600 border-red-200 hover:bg-red-50 bg-transparent"
                onClick={() => onDelete(asset)}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

import { cn } from "@/lib/utils" 