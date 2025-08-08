import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Asset } from "@/lib/types"
import { format } from "date-fns"

interface AssetReturnModalProps {
  asset: Asset | null
  isOpen: boolean
  onClose: () => void
  onReturn: (assetId: number, returnData: any) => Promise<void>
  loading?: boolean
}

export function AssetReturnModal({
  asset,
  isOpen,
  onClose,
  onReturn,
  loading = false
}: AssetReturnModalProps) {
  const [formData, setFormData] = useState({
    ConditionAtReturn: "",
    Notes: ""
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || !asset) return

    const returnData = {
      ReturnedAt: new Date().toISOString(),
      ConditionAtReturn: formData.ConditionAtReturn || undefined,
      Notes: formData.Notes || undefined
    }

    await onReturn(asset.AssetID, returnData)
    
    // Reset form
    setFormData({
      ConditionAtReturn: "",
      Notes: ""
    })
    setErrors({})
  }

  const handleClose = () => {
    setFormData({
      ConditionAtReturn: "",
      Notes: ""
    })
    setErrors({})
    onClose()
  }

  if (!asset) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Return Asset</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Asset Information */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Asset Details</h3>
            <div className="space-y-1 text-sm">
              <div><span className="font-medium">Asset Tag:</span> {asset.AssetTag}</div>
              <div><span className="font-medium">Model:</span> {asset.Model || 'N/A'}</div>
              <div><span className="font-medium">Type:</span> {asset.asset_type?.AssetTypeName || 'N/A'}</div>
              {asset.current_assignment && (
                <div><span className="font-medium">Assigned to:</span> {
                  asset.current_assignment.employee 
                    ? `${asset.current_assignment.employee.FirstName} ${asset.current_assignment.employee.LastName}`
                    : 'Unknown'
                }</div>
              )}
            </div>
          </div>

          {/* Return Form */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="condition">Condition at Return</Label>
              <Select
                value={formData.ConditionAtReturn}
                onValueChange={(value) => setFormData(prev => ({ ...prev, ConditionAtReturn: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select condition" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Excellent">Excellent - Like new</SelectItem>
                  <SelectItem value="Good">Good - Minor wear</SelectItem>
                  <SelectItem value="Fair">Fair - Some wear</SelectItem>
                  <SelectItem value="Poor">Poor - Significant wear</SelectItem>
                  <SelectItem value="Damaged">Damaged - Needs repair</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Return Notes</Label>
              <Textarea
                id="notes"
                value={formData.Notes}
                onChange={(e) => setFormData(prev => ({ ...prev, Notes: e.target.value }))}
                placeholder="Any notes about the return condition or issues..."
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
            >
              {loading ? "Returning..." : "Return Asset"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
} 