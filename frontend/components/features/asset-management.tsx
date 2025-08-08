"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AssetCard } from "@/components/ui/asset-card"
import { AssetStatusBadge } from "@/components/ui/asset-status-badge"
import { AssetForm } from "@/components/ui/asset-form"
import { AssetAssignmentModal } from "@/components/ui/asset-assignment-modal"
import { AssetReturnModal } from "@/components/ui/asset-return-modal"
import { useAssets } from "@/hooks/use-assets"
import { useToast } from "@/hooks/use-toast"
import { 
  canAssignAsset, 
  canReturnAsset, 
  canRetireAsset, 
  canDecommissionAsset,
  canPutInMaintenance,
  canMakeAvailable,
  getAllowedTransitions
} from "@/lib/asset-utils"
import {
  Monitor,
  Laptop,
  Smartphone,
  HardDrive,
  Printer,
  Search,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle,
  XCircle,
  QrCode,
  Download,
  Loader2,
  RefreshCw,
  Filter,
  SortAsc,
  SortDesc,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Shield,
  User,
  MapPin,
  Settings,
  ArrowRight,
  Clock,
  Wrench,
  Archive
} from "lucide-react"
import { Asset, AssetCreate, AssetUpdate, AssetAssignmentCreate, EmployeeInfo } from "@/lib/types"

export default function AssetManagement() {
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null)
  const [assigningAsset, setAssigningAsset] = useState<Asset | null>(null)
  const [returningAsset, setReturningAsset] = useState<Asset | null>(null)
  const [showAssignmentModal, setShowAssignmentModal] = useState(false)
  const [employees, setEmployees] = useState<EmployeeInfo[]>([])

  // Use the custom hook for asset management
  const {
    assets,
    loading,
    error,
    refetch,
    pagination,
    filters,
    setFilters,
    createAsset,
    updateAsset,
    deleteAsset,
    assignAsset,
    returnAsset,
    assetTypes,
    assetStatuses,
    locations,
    statistics,
    statisticsLoading,
    isLoading,
    hasError
  } = useAssets({
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Assets loaded successfully",
      })
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  })

  // Handle search
  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setFilters({ search: value, skip: 0 })
  }

  // Handle status filter
  const handleStatusFilter = (value: string) => {
    setStatusFilter(value)
    setFilters({ 
      status_code: value === "all" ? undefined : value,
      skip: 0 
    })
  }

  // Handle category filter
  const handleCategoryFilter = (value: string) => {
    setCategoryFilter(value)
    setFilters({ 
      asset_type_id: value === "all" ? undefined : parseInt(value),
      skip: 0 
    })
  }

  // Handle pagination
  const handlePageChange = (direction: 'next' | 'prev') => {
    const newSkip = direction === 'next' 
      ? (filters.skip || 0) + (filters.limit || 20)
      : Math.max(0, (filters.skip || 0) - (filters.limit || 20))
    
    setFilters({ skip: newSkip })
  }

  // Handle sorting
  const handleSort = (sortBy: string) => {
    const currentSortBy = filters.sort_by
    const currentSortOrder = filters.sort_order || 'asc'
    
    if (currentSortBy === sortBy) {
      // Toggle sort order
      setFilters({ 
        sort_by: sortBy,
        sort_order: currentSortOrder === 'asc' ? 'desc' : 'asc',
        skip: 0
      })
    } else {
      // Set new sort field
      setFilters({ 
        sort_by: sortBy as any,
        sort_order: 'asc',
        skip: 0
      })
    }
  }

  // Handle asset creation
  const handleCreateAsset = async (assetData: AssetCreate | AssetUpdate) => {
    try {
      await createAsset(assetData as AssetCreate)
      setShowAddForm(false)
      toast({
        title: "Success",
        description: "Asset created successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create asset",
        variant: "destructive",
      })
    }
  }

  // Handle asset update
  const handleUpdateAsset = async (assetData: AssetUpdate) => {
    if (!editingAsset) return
    
    try {
      await updateAsset(editingAsset.AssetID, assetData)
      setEditingAsset(null)
      toast({
        title: "Success",
        description: "Asset updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update asset",
        variant: "destructive",
      })
    }
  }

  // Handle asset deletion
  const handleDeleteAsset = async (asset: Asset) => {
    if (!confirm(`Are you sure you want to delete asset ${asset.AssetTag}?`)) return
    
    try {
      await deleteAsset(asset.AssetID)
      toast({
        title: "Success",
        description: "Asset deleted successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete asset",
        variant: "destructive",
      })
    }
  }

  // Handle asset assignment
  const handleAssignAsset = async (assignmentData: AssetAssignmentCreate) => {
    try {
      await assignAsset(assignmentData)
      setShowAssignmentModal(false)
      toast({
        title: "Success",
        description: "Asset assigned successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to assign asset",
        variant: "destructive",
      })
    }
  }

  // Handle asset return
  const handleReturnAsset = async (assignmentId: number, returnData: any) => {
    try {
      await returnAsset(assignmentId, returnData)
      setReturningAsset(null)
      toast({
        title: "Success",
        description: "Asset returned successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to return asset",
        variant: "destructive",
      })
    }
  }

  // Handle direct assignment
  const handleDirectAssignment = (asset: Asset) => {
    setAssigningAsset(asset)
    setShowAssignmentModal(true)
  }

  // Get category counts for display
  const getCategoryCounts = () => {
    const counts: Record<string, number> = {}
    assets.forEach(asset => {
      const typeName = asset.asset_type?.AssetTypeName || 'Unknown'
      counts[typeName] = (counts[typeName] || 0) + 1
    })
    return counts
  }

  const categoryCounts = getCategoryCounts()

  const categories = [
    { value: "laptop", label: "Laptops", icon: Laptop, count: categoryCounts['Laptop'] || 0 },
    { value: "mobile", label: "Mobile Devices", icon: Smartphone, count: categoryCounts['Mobile Phone'] || 0 },
    { value: "monitor", label: "Monitors", icon: Monitor, count: categoryCounts['Monitor'] || 0 },
    { value: "printer", label: "Printers", icon: Printer, count: categoryCounts['Printer'] || 0 },
    { value: "other", label: "Other", icon: HardDrive, count: Object.values(categoryCounts).reduce((a, b) => a + b, 0) - (categoryCounts['Laptop'] || 0) - (categoryCounts['Mobile Phone'] || 0) - (categoryCounts['Monitor'] || 0) - (categoryCounts['Printer'] || 0) },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Asset Management</h2>
          <p className="text-gray-600">Track and manage company assets and equipment</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={refetch}
            disabled={loading}
            className="bg-transparent"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Refresh
          </Button>
          <Button
            onClick={() => setShowAddForm(true)}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Asset
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {hasError && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-800">
              <XCircle className="w-5 h-5" />
              <span className="font-medium">Error loading assets</span>
            </div>
            <p className="text-red-600 text-sm mt-1">
              {error?.message || "An unexpected error occurred"}
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={refetch}
              className="mt-2"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
                <Badge className="bg-gradient-to-r from-green-500 to-emerald-600 text-white border-0">
                  {statistics.assigned_assets}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Assigned Assets</p>
                <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                  {statistics.assigned_assets}
                </p>
                <p className="text-xs text-gray-500">Currently in use</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Wrench className="w-6 h-6 text-white" />
                </div>
                <Badge className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white border-0">
                  {statistics.in_maintenance}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">In Maintenance</p>
                <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                  {statistics.in_maintenance}
                </p>
                <p className="text-xs text-gray-500">Under repair</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-r from-orange-400 to-red-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <Badge className="bg-gradient-to-r from-orange-500 to-red-600 text-white border-0">
                  {statistics.decommissioning}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Decommissioning</p>
                <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                  {statistics.decommissioning}
                </p>
                <p className="text-xs text-gray-500">Preparing for retirement</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Monitor className="w-6 h-6 text-white" />
                </div>
                <Badge className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white border-0">
                  {statistics.total_assets}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Total Assets</p>
                <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                  {statistics.total_assets}
                </p>
                <p className="text-xs text-gray-500">All tracked items</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="border-0 shadow-sm">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 h-11"
              />
            </div>

            <Select value={statusFilter} onValueChange={handleStatusFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {assetStatuses.map((status) => (
                  <SelectItem key={status.AssetStatusCode} value={status.AssetStatusCode}>
                    {status.AssetStatusName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={categoryFilter} onValueChange={handleCategoryFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label} ({category.count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" className="h-11 bg-transparent">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>

          {/* Sort Options */}
          <div className="flex items-center gap-2 mt-4 pt-4 border-t">
            <span className="text-sm font-medium text-gray-600">Sort by:</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('created_at')}
              className="bg-transparent"
            >
              Created Date
              {filters.sort_by === 'created_at' && (
                filters.sort_order === 'desc' ? <SortDesc className="w-3 h-3 ml-1" /> : <SortAsc className="w-3 h-3 ml-1" />
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('asset_tag')}
              className="bg-transparent"
            >
              Asset Tag
              {filters.sort_by === 'asset_tag' && (
                filters.sort_order === 'desc' ? <SortDesc className="w-3 h-3 ml-1" /> : <SortAsc className="w-3 h-3 ml-1" />
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('warranty_end_date')}
              className="bg-transparent"
            >
              Warranty
              {filters.sort_by === 'warranty_end_date' && (
                filters.sort_order === 'desc' ? <SortDesc className="w-3 h-3 ml-1" /> : <SortAsc className="w-3 h-3 ml-1" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <Card className="border-0 shadow-sm">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Loading assets...</h3>
            <p className="text-gray-600">Please wait while we fetch the latest data</p>
          </CardContent>
        </Card>
      )}

      {/* Assets List */}
      {!loading && assets.length > 0 && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {assets.map((asset) => (
              <AssetCard
                key={asset.AssetID}
                asset={asset}
                onEdit={setEditingAsset}
                onDelete={handleDeleteAsset}
                onAssign={handleDirectAssignment}
                onReturn={setReturningAsset}
              />
            ))}
          </div>

          {/* Pagination */}
          {pagination.total > pagination.size && (
            <Card className="border-0 shadow-sm">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing {(filters.skip || 0) + 1} to {Math.min((filters.skip || 0) + pagination.size, pagination.total)} of {pagination.total} assets
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange('prev')}
                      disabled={!pagination.hasPrevious}
                      className="bg-transparent"
                    >
                      <ChevronLeft className="w-4 h-4 mr-1" />
                      Previous
                    </Button>
                    <span className="text-sm text-gray-600">
                      Page {Math.floor((filters.skip || 0) / pagination.size) + 1} of {Math.ceil(pagination.total / pagination.size)}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange('next')}
                      disabled={!pagination.hasNext}
                      className="bg-transparent"
                    >
                      Next
                      <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Empty State */}
      {!loading && assets.length === 0 && !hasError && (
        <Card className="border-0 shadow-sm">
          <CardContent className="p-12 text-center">
            <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
            <Button
              variant="outline"
              onClick={() => setFilters({})}
              className="mt-4"
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Asset Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <AssetForm
              assetTypes={assetTypes}
              assetStatuses={assetStatuses}
              locations={locations}
              onSubmit={handleCreateAsset}
              onCancel={() => setShowAddForm(false)}
              loading={loading}
            />
          </div>
        </div>
      )}

      {/* Edit Asset Form Modal */}
      {editingAsset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <AssetForm
              asset={editingAsset}
              assetTypes={assetTypes}
              assetStatuses={assetStatuses}
              locations={locations}
              onSubmit={handleUpdateAsset}
              onCancel={() => setEditingAsset(null)}
              loading={loading}
            />
          </div>
        </div>
      )}

      {/* Asset Assignment Modal */}
      <AssetAssignmentModal
        asset={assigningAsset}
        isOpen={showAssignmentModal}
        onClose={() => {
          setShowAssignmentModal(false)
          setAssigningAsset(null)
        }}
        onAssign={handleAssignAsset}
        loading={loading}
      />

      {/* Asset Return Modal */}
      <AssetReturnModal
        asset={returningAsset}
        isOpen={!!returningAsset}
        onClose={() => setReturningAsset(null)}
        onReturn={handleReturnAsset}
        loading={loading}
      />
    </div>
  )
}
