import { useState, useEffect, useRef } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Asset, AssetAssignmentCreate, EmployeeInfo } from "@/lib/types"
import { canAssignAsset } from "@/lib/asset-utils"
import { api } from "@/lib/api"

import { format, addDays } from "date-fns"

interface AssetAssignmentModalProps {
  asset: Asset | null
  isOpen: boolean
  onClose: () => void
  onAssign: (assignment: AssetAssignmentCreate) => Promise<void>
  loading?: boolean
}

export function AssetAssignmentModal({
  asset,
  isOpen,
  onClose,
  onAssign,
  loading = false
  }: AssetAssignmentModalProps) {

  const [formData, setFormData] = useState({
    EmployeeID: 0,
    DueReturnDate: "",
    ConditionAtAssign: "",
    Notes: ""
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Employee search states
  const [searchTerm, setSearchTerm] = useState("")
  const [searchResults, setSearchResults] = useState<EmployeeInfo[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeInfo | null>(null)
  const searchTimeout = useRef<NodeJS.Timeout | null>(null)

  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchTerm(value)
    setSelectedEmployee(null)
    setFormData(prev => ({ ...prev, EmployeeID: 0 }))

    // Basic debounce
    if (searchTimeout.current) clearTimeout(searchTimeout.current)
    if (value.length >= 3) {
      searchTimeout.current = setTimeout(() => {
        fetchEmployees(value)
      }, 400)
    } else {
      setSearchResults([])
    }
  }

  const fetchEmployees = async (query: string) => {
    try {
      setSearchLoading(true)
      const resp = await api.get<any>(`/api/employees?limit=20&search=${encodeURIComponent(query)}`)
      const list: EmployeeInfo[] = Array.isArray(resp.employees) ? resp.employees : resp.items || resp
      setSearchResults(list)
    } catch (err) {
      console.error("Employee search failed", err)
    } finally {
      setSearchLoading(false)
    }
  }

  const handleSelectEmployee = (emp: EmployeeInfo) => {
    setSelectedEmployee(emp)
    setSearchTerm(`${emp.FirstName} ${emp.LastName}`)
    setFormData(prev => ({ ...prev, EmployeeID: emp.EmployeeID }))
    setSearchResults([])
  }

  const canAssign = asset ? canAssignAsset(asset) : false

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.EmployeeID) {
      newErrors.EmployeeID = "Employee is required"
    }

    if (formData.DueReturnDate) {
      const dueDate = new Date(formData.DueReturnDate)
      const today = new Date()
      if (dueDate <= today) {
        newErrors.DueReturnDate = "Due date must be in the future"
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || !asset) return

    const assignment: AssetAssignmentCreate = {
      AssetID: asset.AssetID,
      EmployeeID: formData.EmployeeID,
      DueReturnDate: formData.DueReturnDate || undefined,
      ConditionAtAssign: formData.ConditionAtAssign || undefined,
      Notes: formData.Notes || undefined
    }

    await onAssign(assignment)
    
    // Reset form
    setFormData({
      EmployeeID: 0,
      DueReturnDate: "",
      ConditionAtAssign: "",
      Notes: ""
    })
    setErrors({})
  }

  const handleClose = () => {
    setFormData({
      EmployeeID: 0,
      DueReturnDate: "",
      ConditionAtAssign: "",
      Notes: ""
    })
    setErrors({})
    onClose()
  }

  const getDefaultDueDate = () => {
    // Default to 30 days from now
    return format(addDays(new Date(), 30), 'yyyy-MM-dd')
  }

  if (!asset) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Assign Asset</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Asset Information */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Asset Details</h3>
            <div className="space-y-1 text-sm">
              <div><span className="font-medium">Asset Tag:</span> {asset.AssetTag}</div>
              <div><span className="font-medium">Model:</span> {asset.Model || 'N/A'}</div>
              <div><span className="font-medium">Type:</span> {asset.asset_type?.AssetTypeName || 'N/A'}</div>
              <div><span className="font-medium">Location:</span> {asset.location?.LocationName || 'N/A'}</div>
            </div>
          </div>

          {/* Assignment Form */}
          <div className="space-y-4">
            <div className="space-y-2 relative">
              <Label htmlFor="employeeSearch">Employee *</Label>
              <Input
                id="employeeSearch"
                value={searchTerm}
                onChange={handleSearchInput}
                placeholder="Type at least 3 characters to search..."
                className={errors.EmployeeID ? "border-red-500" : ""}
              />
              {searchLoading && (
                <p className="text-xs text-gray-500 mt-1">Searching...</p>
              )}
              {searchResults.length > 0 && (
                <ul className="absolute z-10 bg-white border rounded-md w-full max-h-56 overflow-y-auto mt-1 shadow-lg divide-y">
                  {searchResults.map((emp) => (
                    <li
                      key={emp.EmployeeID}
                      className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
                      onClick={() => handleSelectEmployee(emp)}
                    >
                      {emp.FirstName} {emp.LastName} - {emp.CompanyEmail}
                    </li>
                  ))}
                </ul>
              )}
              {selectedEmployee && (
                <p className="text-sm text-gray-700 mt-1">
                  Selected: {selectedEmployee.FirstName} {selectedEmployee.LastName}
                </p>
              )}
              {errors.EmployeeID && <p className="text-red-500 text-sm">{errors.EmployeeID}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="dueDate">Due Return Date</Label>
              <Input
                id="dueDate"
                type="date"
                value={formData.DueReturnDate}
                onChange={(e) => setFormData(prev => ({ ...prev, DueReturnDate: e.target.value }))}
                min={format(new Date(), 'yyyy-MM-dd')}
                placeholder={getDefaultDueDate()}
              />
              {errors.DueReturnDate && <p className="text-red-500 text-sm">{errors.DueReturnDate}</p>}
              <p className="text-xs text-gray-500">Leave empty for no specific due date</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="condition">Condition at Assignment</Label>
              <Select
                value={formData.ConditionAtAssign}
                onValueChange={(value) => setFormData(prev => ({ ...prev, ConditionAtAssign: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select condition" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Excellent">Excellent - Like new</SelectItem>
                  <SelectItem value="Good">Good - Minor wear</SelectItem>
                  <SelectItem value="Fair">Fair - Some wear</SelectItem>
                  <SelectItem value="Poor">Poor - Significant wear</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Assignment Notes</Label>
              <Textarea
                id="notes"
                value={formData.Notes}
                onChange={(e) => setFormData(prev => ({ ...prev, Notes: e.target.value }))}
                placeholder="Any special instructions or notes for this assignment..."
                rows={3}
              />
            </div>
          </div>

          {/* Warning if asset cannot be assigned */}
          {!canAssign && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-yellow-800 text-sm">
                This asset cannot be assigned. Current status: {asset.AssetStatusCode}
              </p>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading || !canAssign}
            >
              {loading ? "Assigning..." : "Assign Asset"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
} 