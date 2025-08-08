import { Asset, AssetStatus, ASSET_STATUS_TRANSITIONS } from './types'

/**
 * Check if a status transition is allowed
 */
export function isStatusTransitionAllowed(fromStatus: string, toStatus: string): boolean {
  const allowedTransitions = ASSET_STATUS_TRANSITIONS[fromStatus] || []
  return allowedTransitions.includes(toStatus)
}

/**
 * Get all allowed transitions for a given status
 */
export function getAllowedTransitions(currentStatus: string): string[] {
  return ASSET_STATUS_TRANSITIONS[currentStatus] || []
}

/**
 * Check if asset can be assigned
 */
export function canAssignAsset(asset: Asset): boolean {
  return ['Available', 'In-Stock'].includes(asset.AssetStatusCode)
}

/**
 * Check if asset can be returned
 */
export function canReturnAsset(asset: Asset): boolean {
  return asset.AssetStatusCode === 'Assigned' && asset.current_assignment
}

/**
 * Check if asset can be retired (must go through decommissioning first)
 */
export function canRetireAsset(asset: Asset): boolean {
  return asset.AssetStatusCode === 'Decommissioning'
}

/**
 * Check if asset can be decommissioned
 */
export function canDecommissionAsset(asset: Asset): boolean {
  return ['In-Stock', 'Available', 'Assigned', 'Maintenance'].includes(asset.AssetStatusCode)
}

/**
 * Check if asset can be put into maintenance
 */
export function canPutInMaintenance(asset: Asset): boolean {
  return ['In-Stock', 'Available', 'Assigned'].includes(asset.AssetStatusCode)
}

/**
 * Check if asset can be made available
 */
export function canMakeAvailable(asset: Asset): boolean {
  return ['In-Stock', 'Maintenance'].includes(asset.AssetStatusCode)
}

/**
 * Validate asset data for creation
 */
export function validateAssetCreate(data: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = []

  // Required fields
  if (!data.AssetTag?.trim()) {
    errors.push('Asset tag is required')
  }

  if (!data.AssetTypeID) {
    errors.push('Asset type is required')
  }

  if (!data.AssetStatusCode) {
    errors.push('Asset status is required')
  }

  if (data.IsActive === undefined) {
    errors.push('Active status is required')
  }

  // Contract validation
  if (data.IsUnderContract) {
    if (!data.ContractStartDate) {
      errors.push('Contract start date is required when under contract')
    }
    if (!data.ContractExpiryDate) {
      errors.push('Contract expiry date is required when under contract')
    }
    if (data.ContractStartDate && data.ContractExpiryDate) {
      const startDate = new Date(data.ContractStartDate)
      const expiryDate = new Date(data.ContractExpiryDate)
      if (expiryDate <= startDate) {
        errors.push('Contract expiry date must be after start date')
      }
    }
  }

  // Serial number and MAC address validation
  if (data.SerialNumber && data.SerialNumber.length > 100) {
    errors.push('Serial number must be 100 characters or less')
  }

  if (data.MACAddress && data.MACAddress.length > 100) {
    errors.push('MAC address must be 100 characters or less')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Validate asset data for update
 */
export function validateAssetUpdate(data: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = []

  // Contract validation
  if (data.IsUnderContract) {
    if (!data.ContractStartDate) {
      errors.push('Contract start date is required when under contract')
    }
    if (!data.ContractExpiryDate) {
      errors.push('Contract expiry date is required when under contract')
    }
    if (data.ContractStartDate && data.ContractExpiryDate) {
      const startDate = new Date(data.ContractStartDate)
      const expiryDate = new Date(data.ContractExpiryDate)
      if (expiryDate <= startDate) {
        errors.push('Contract expiry date must be after start date')
      }
    }
  }

  // Serial number and MAC address validation
  if (data.SerialNumber && data.SerialNumber.length > 100) {
    errors.push('Serial number must be 100 characters or less')
  }

  if (data.MACAddress && data.MACAddress.length > 100) {
    errors.push('MAC address must be 100 characters or less')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Get asset status display information
 */
export function getAssetStatusInfo(statusCode: string): {
  label: string
  color: string
  icon: string
  description: string
} {
  const statusInfo: Record<string, { label: string; color: string; icon: string; description: string }> = {
    'In-Stock': {
      label: 'In Stock',
      color: 'bg-gray-100 text-gray-800',
      icon: 'package',
      description: 'Asset is available but not ready for assignment'
    },
    'Available': {
      label: 'Available',
      color: 'bg-green-100 text-green-800',
      icon: 'check-circle',
      description: 'Asset is ready for assignment'
    },
    'Assigned': {
      label: 'Assigned',
      color: 'bg-blue-100 text-blue-800',
      icon: 'user-check',
      description: 'Asset is currently assigned to an employee'
    },
    'Maintenance': {
      label: 'Maintenance',
      color: 'bg-yellow-100 text-yellow-800',
      icon: 'wrench',
      description: 'Asset is under repair or maintenance'
    },
    'Decommissioning': {
      label: 'Decommissioning',
      color: 'bg-orange-100 text-orange-800',
      icon: 'clock',
      description: 'Asset is being prepared for retirement'
    },
    'Retired': {
      label: 'Retired',
      color: 'bg-red-100 text-red-800',
      icon: 'archive',
      description: 'Asset has reached end of life'
    }
  }

  return statusInfo[statusCode] || {
    label: statusCode,
    color: 'bg-gray-100 text-gray-800',
    icon: 'help-circle',
    description: 'Unknown status'
  }
}

/**
 * Check if asset has warranty
 */
export function hasWarranty(asset: Asset): boolean {
  if (!asset.WarrantyEndDate) return false
  return new Date(asset.WarrantyEndDate) > new Date()
}

/**
 * Check if asset warranty is expiring soon (within 30 days)
 */
export function isWarrantyExpiringSoon(asset: Asset): boolean {
  if (!asset.WarrantyEndDate) return false
  const warrantyEnd = new Date(asset.WarrantyEndDate)
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
  return warrantyEnd <= thirtyDaysFromNow && warrantyEnd > new Date()
}

/**
 * Check if asset contract is expiring soon (within 30 days)
 */
export function isContractExpiringSoon(asset: Asset): boolean {
  if (!asset.IsUnderContract || !asset.ContractExpiryDate) return false
  const contractEnd = new Date(asset.ContractExpiryDate)
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
  return contractEnd <= thirtyDaysFromNow && contractEnd > new Date()
}

/**
 * Get asset assignment status
 */
export function getAssetAssignmentStatus(asset: Asset): {
  isAssigned: boolean
  assignedTo?: string
  assignmentDate?: string
  dueDate?: string
  isOverdue: boolean
} {
  const assignment = asset.current_assignment
  
  if (!assignment) {
    return {
      isAssigned: false,
      isOverdue: false
    }
  }

  const assignedTo = assignment.employee 
    ? `${assignment.employee.FirstName} ${assignment.employee.LastName}`
    : 'Unknown'

  const isOverdue = assignment.DueReturnDate 
    ? new Date(assignment.DueReturnDate) < new Date()
    : false

  return {
    isAssigned: true,
    assignedTo,
    assignmentDate: assignment.AssignedAt,
    dueDate: assignment.DueReturnDate,
    isOverdue
  }
}

/**
 * Format asset tag for display
 */
export function formatAssetTag(tag: string): string {
  return tag.toUpperCase()
}

/**
 * Get asset type icon
 */
export function getAssetTypeIcon(typeName: string): string {
  const iconMap: Record<string, string> = {
    'Laptop': 'laptop',
    'Monitor': 'monitor',
    'Mobile Phone': 'smartphone',
    'Keyboard': 'keyboard',
    'Mouse': 'mouse',
    'Docking Station': 'hard-drive',
    'Headset': 'headphones',
    'Printer': 'printer'
  }
  
  return iconMap[typeName] || 'package'
}

/**
 * Sort assets by various criteria
 */
export function sortAssets(assets: Asset[], sortBy: string, sortOrder: 'asc' | 'desc' = 'asc'): Asset[] {
  const sorted = [...assets].sort((a, b) => {
    let aValue: any
    let bValue: any

    switch (sortBy) {
      case 'asset_tag':
        aValue = a.AssetTag.toLowerCase()
        bValue = b.AssetTag.toLowerCase()
        break
      case 'model':
        aValue = (a.Model || '').toLowerCase()
        bValue = (b.Model || '').toLowerCase()
        break
      case 'vendor':
        aValue = (a.Vendor || '').toLowerCase()
        bValue = (b.Vendor || '').toLowerCase()
        break
      case 'purchase_date':
        aValue = a.PurchaseDate ? new Date(a.PurchaseDate).getTime() : 0
        bValue = b.PurchaseDate ? new Date(b.PurchaseDate).getTime() : 0
        break
      case 'warranty_end_date':
        aValue = a.WarrantyEndDate ? new Date(a.WarrantyEndDate).getTime() : 0
        bValue = b.WarrantyEndDate ? new Date(b.WarrantyEndDate).getTime() : 0
        break
      case 'contract_expiry_date':
        aValue = a.ContractExpiryDate ? new Date(a.ContractExpiryDate).getTime() : 0
        bValue = b.ContractExpiryDate ? new Date(b.ContractExpiryDate).getTime() : 0
        break
      case 'created_at':
        aValue = new Date(a.CreatedAt).getTime()
        bValue = new Date(b.CreatedAt).getTime()
        break
      case 'updated_at':
        aValue = new Date(a.UpdatedAt).getTime()
        bValue = new Date(b.UpdatedAt).getTime()
        break
      default:
        aValue = a.AssetTag.toLowerCase()
        bValue = b.AssetTag.toLowerCase()
    }

    if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
    if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
    return 0
  })

  return sorted
} 