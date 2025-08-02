import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Asset, AssetCreate, AssetUpdate, AssetType, AssetStatus, Location } from "@/lib/types"
import { validateAssetCreate, validateAssetUpdate, isStatusTransitionAllowed, getAllowedTransitions } from "@/lib/asset-utils"
import { format } from "date-fns"

interface AssetFormProps {
  asset?: Asset
  assetTypes: AssetType[]
  assetStatuses: AssetStatus[]
  locations: Location[]
  onSubmit: (data: AssetCreate | AssetUpdate) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

export function AssetForm({ 
  asset, 
  assetTypes, 
  assetStatuses, 
  locations, 
  onSubmit, 
  onCancel, 
  loading = false 
}: AssetFormProps) {
  const [formData, setFormData] = useState({
    AssetTag: asset?.AssetTag || "",
    AssetTypeID: asset?.AssetTypeID || 0,
    SerialNumber: asset?.SerialNumber || "",
    MACAddress: asset?.MACAddress || "",
    Model: asset?.Model || "",
    Vendor: asset?.Vendor || "",
    PurchaseDate: asset?.PurchaseDate ? format(new Date(asset.PurchaseDate), 'yyyy-MM-dd') : "",
    WarrantyEndDate: asset?.WarrantyEndDate ? format(new Date(asset.WarrantyEndDate), 'yyyy-MM-dd') : "",
    IsUnderContract: asset?.IsUnderContract || false,
    ContractStartDate: asset?.ContractStartDate ? format(new Date(asset.ContractStartDate), 'yyyy-MM-dd') : "",
    ContractExpiryDate: asset?.ContractExpiryDate ? format(new Date(asset.ContractExpiryDate), 'yyyy-MM-dd') : "",
    LocationID: asset?.LocationID || 0,
    Notes: asset?.Notes || "",
    AssetStatusCode: asset?.AssetStatusCode || "In-Stock",
    IsActive: asset?.IsActive ?? true,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Get allowed status transitions for current asset
  const allowedTransitions = asset ? getAllowedTransitions(asset.AssetStatusCode) : assetStatuses.map(s => s.AssetStatusCode)

  const validateForm = () => {
    const validation = asset ? validateAssetUpdate(formData) : validateAssetCreate(formData)
    
    if (!validation.isValid) {
      const newErrors: Record<string, string> = {}
      validation.errors.forEach(error => {
        // Map validation errors to form fields
        if (error.includes('Asset tag')) newErrors.AssetTag = error
        else if (error.includes('Asset type')) newErrors.AssetTypeID = error
        else if (error.includes('Asset status')) newErrors.AssetStatusCode = error
        else if (error.includes('Active status')) newErrors.IsActive = error
        else if (error.includes('Contract start date')) newErrors.ContractStartDate = error
        else if (error.includes('Contract expiry date')) newErrors.ContractExpiryDate = error
        else if (error.includes('Serial number')) newErrors.SerialNumber = error
        else if (error.includes('MAC address')) newErrors.MACAddress = error
        else newErrors.general = error
      })
      setErrors(newErrors)
      return false
    }

    // Additional validation for status transitions
    if (asset && formData.AssetStatusCode !== asset.AssetStatusCode) {
      if (!isStatusTransitionAllowed(asset.AssetStatusCode, formData.AssetStatusCode)) {
        setErrors({
          AssetStatusCode: `Cannot transition from ${asset.AssetStatusCode} to ${formData.AssetStatusCode}. Allowed transitions: ${allowedTransitions.join(', ')}`
        })
        return false
      }
    }

    setErrors({})
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    const submitData = {
      ...formData,
      AssetTypeID: formData.AssetTypeID || undefined,
      LocationID: formData.LocationID || undefined,
      PurchaseDate: formData.PurchaseDate || undefined,
      WarrantyEndDate: formData.WarrantyEndDate || undefined,
      ContractStartDate: formData.IsUnderContract ? formData.ContractStartDate : undefined,
      ContractExpiryDate: formData.IsUnderContract ? formData.ContractExpiryDate : undefined,
    }

    await onSubmit(submitData)
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }))
    }
  }

  const handleStatusChange = (newStatus: string) => {
    if (asset && !isStatusTransitionAllowed(asset.AssetStatusCode, newStatus)) {
      setErrors({
        AssetStatusCode: `Cannot transition from ${asset.AssetStatusCode} to ${newStatus}. Allowed transitions: ${allowedTransitions.join(', ')}`
      })
      return
    }
    handleInputChange("AssetStatusCode", newStatus)
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>{asset ? "Edit Asset" : "Create New Asset"}</CardTitle>
        {asset && (
          <p className="text-sm text-gray-600">
            Current status: {asset.AssetStatusCode}. 
            Allowed transitions: {allowedTransitions.join(', ')}
          </p>
        )}
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Required Fields Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Required Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="assetTag">Asset Tag *</Label>
                <Input
                  id="assetTag"
                  value={formData.AssetTag}
                  onChange={(e) => handleInputChange("AssetTag", e.target.value)}
                  placeholder="e.g., AST-2024-001"
                  className={errors.AssetTag ? "border-red-500" : ""}
                  required
                />
                {errors.AssetTag && <p className="text-red-500 text-sm">{errors.AssetTag}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="assetType">Asset Type *</Label>
                <Select
                  value={formData.AssetTypeID.toString()}
                  onValueChange={(value) => handleInputChange("AssetTypeID", parseInt(value))}
                >
                  <SelectTrigger className={errors.AssetTypeID ? "border-red-500" : ""}>
                    <SelectValue placeholder="Select asset type" />
                  </SelectTrigger>
                  <SelectContent>
                    {assetTypes.map((type) => (
                      <SelectItem key={type.AssetTypeID} value={type.AssetTypeID.toString()}>
                        {type.AssetTypeName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.AssetTypeID && <p className="text-red-500 text-sm">{errors.AssetTypeID}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status *</Label>
                <Select
                  value={formData.AssetStatusCode}
                  onValueChange={handleStatusChange}
                >
                  <SelectTrigger className={errors.AssetStatusCode ? "border-red-500" : ""}>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    {assetStatuses
                      .filter(status => !asset || allowedTransitions.includes(status.AssetStatusCode))
                      .map((status) => (
                        <SelectItem key={status.AssetStatusCode} value={status.AssetStatusCode}>
                          {status.AssetStatusName}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                {errors.AssetStatusCode && <p className="text-red-500 text-sm">{errors.AssetStatusCode}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="isActive">Active Status *</Label>
                <Select
                  value={formData.IsActive.toString()}
                  onValueChange={(value) => handleInputChange("IsActive", value === "true")}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Active</SelectItem>
                    <SelectItem value="false">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Optional Fields Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Asset Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="serialNumber">Serial Number</Label>
                <Input
                  id="serialNumber"
                  value={formData.SerialNumber}
                  onChange={(e) => handleInputChange("SerialNumber", e.target.value)}
                  placeholder="Enter serial number"
                  maxLength={100}
                />
                {errors.SerialNumber && <p className="text-red-500 text-sm">{errors.SerialNumber}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="macAddress">MAC Address</Label>
                <Input
                  id="macAddress"
                  value={formData.MACAddress}
                  onChange={(e) => handleInputChange("MACAddress", e.target.value)}
                  placeholder="Enter MAC address"
                  maxLength={100}
                />
                {errors.MACAddress && <p className="text-red-500 text-sm">{errors.MACAddress}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">Model</Label>
                <Input
                  id="model"
                  value={formData.Model}
                  onChange={(e) => handleInputChange("Model", e.target.value)}
                  placeholder="Enter model"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="vendor">Vendor</Label>
                <Input
                  id="vendor"
                  value={formData.Vendor}
                  onChange={(e) => handleInputChange("Vendor", e.target.value)}
                  placeholder="Enter vendor"
                />
              </div>
            </div>
          </div>

          {/* Dates Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Dates</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="purchaseDate">Purchase Date</Label>
                <Input
                  id="purchaseDate"
                  type="date"
                  value={formData.PurchaseDate}
                  onChange={(e) => handleInputChange("PurchaseDate", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="warrantyEndDate">Warranty End Date</Label>
                <Input
                  id="warrantyEndDate"
                  type="date"
                  value={formData.WarrantyEndDate}
                  onChange={(e) => handleInputChange("WarrantyEndDate", e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Contract Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Contract Information</h3>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="isUnderContract"
                checked={formData.IsUnderContract}
                onCheckedChange={(checked) => handleInputChange("IsUnderContract", checked)}
              />
              <Label htmlFor="isUnderContract">Under Contract</Label>
            </div>

            {formData.IsUnderContract && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="contractStartDate">Contract Start Date *</Label>
                  <Input
                    id="contractStartDate"
                    type="date"
                    value={formData.ContractStartDate}
                    onChange={(e) => handleInputChange("ContractStartDate", e.target.value)}
                    className={errors.ContractStartDate ? "border-red-500" : ""}
                    required={formData.IsUnderContract}
                  />
                  {errors.ContractStartDate && <p className="text-red-500 text-sm">{errors.ContractStartDate}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="contractExpiryDate">Contract Expiry Date *</Label>
                  <Input
                    id="contractExpiryDate"
                    type="date"
                    value={formData.ContractExpiryDate}
                    onChange={(e) => handleInputChange("ContractExpiryDate", e.target.value)}
                    className={errors.ContractExpiryDate ? "border-red-500" : ""}
                    required={formData.IsUnderContract}
                  />
                  {errors.ContractExpiryDate && <p className="text-red-500 text-sm">{errors.ContractExpiryDate}</p>}
                </div>
              </div>
            )}
          </div>

          {/* Location */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Location</h3>
            
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Select
                value={formData.LocationID.toString()}
                onValueChange={(value) => handleInputChange("LocationID", parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  {locations.map((location) => (
                    <SelectItem key={location.LocationID} value={location.LocationID.toString()}>
                      {location.LocationName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Additional Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.Notes}
                onChange={(e) => handleInputChange("Notes", e.target.value)}
                placeholder="Enter any additional notes..."
                rows={3}
              />
            </div>
          </div>

          {/* General Errors */}
          {errors.general && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{errors.general}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : asset ? "Update Asset" : "Create Asset"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
} 