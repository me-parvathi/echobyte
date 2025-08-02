"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AssetCard } from "@/components/ui/asset-card"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { ErrorMessage } from "@/components/ui/error-message"
import { useAssets } from "@/hooks/use-assets"
import { useToast } from "@/hooks/use-toast"
import { sortAssets, getAssetStatusInfo } from "@/lib/asset-utils"
import {
  ArrowUpDown,
  SortAsc,
  SortDesc,
  Filter,
  Download,
  RefreshCw,
  Grid3X3,
  List,
  Search,
  X
} from "lucide-react"
import { Asset, AssetSortOptions } from "@/lib/types"

export default function AssetSortPage() {
  const { toast } = useToast()
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = useState("")
  const [sortBy, setSortBy] = useState<keyof Asset>('AssetTag')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [locationFilter, setLocationFilter] = useState<string>('all')
  const [showFilters, setShowFilters] = useState(false)

  const {
    assets,
    loading,
    error,
    refetch,
    assetTypes,
    assetStatuses,
    locations,
    statistics,
    hasError
  } = useAssets({
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      })
    }
  })

  // Client-side filtering and sorting
  const filteredAndSortedAssets = assets
    .filter(asset => {
      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase()
        const matchesSearch = 
          asset.AssetTag.toLowerCase().includes(searchLower) ||
          (asset.Model?.toLowerCase().includes(searchLower)) ||
          (asset.Vendor?.toLowerCase().includes(searchLower)) ||
          (asset.SerialNumber?.toLowerCase().includes(searchLower)) ||
          (asset.Notes?.toLowerCase().includes(searchLower))
        
        if (!matchesSearch) return false
      }

      // Status filter
      if (statusFilter !== 'all' && asset.AssetStatusCode !== statusFilter) {
        return false
      }

      // Type filter
      if (typeFilter !== 'all' && asset.asset_type?.AssetTypeID.toString() !== typeFilter) {
        return false
      }

      // Location filter
      if (locationFilter !== 'all' && asset.location?.LocationID.toString() !== locationFilter) {
        return false
      }

      return true
    })
    .sort((a, b) => {
      let aValue: any = a[sortBy]
      let bValue: any = b[sortBy]

      // Handle date fields
      if (sortBy === 'PurchaseDate' || sortBy === 'WarrantyEndDate' || sortBy === 'ContractExpiryDate') {
        aValue = aValue ? new Date(aValue).getTime() : 0
        bValue = bValue ? new Date(bValue).getTime() : 0
      }

      // Handle string fields
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue?.toLowerCase() || ''
      }

      // Handle null/undefined values
      if (aValue == null) aValue = sortOrder === 'asc' ? Infinity : -Infinity
      if (bValue == null) bValue = sortOrder === 'asc' ? Infinity : -Infinity

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

  const handleSort = (field: keyof Asset) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('asc')
    }
  }

  const clearFilters = () => {
    setSearchTerm("")
    setStatusFilter('all')
    setTypeFilter('all')
    setLocationFilter('all')
  }

  const exportData = () => {
    const csvContent = [
      ['Asset Tag', 'Model', 'Vendor', 'Status', 'Type', 'Location', 'Purchase Date', 'Warranty End', 'Serial Number'],
      ...filteredAndSortedAssets.map(asset => [
        asset.AssetTag,
        asset.Model || '',
        asset.Vendor || '',
        asset.AssetStatusCode,
        asset.asset_type?.AssetTypeName || '',
        asset.location?.LocationName || '',
        asset.PurchaseDate || '',
        asset.WarrantyEndDate || '',
        asset.SerialNumber || ''
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assets-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)

    toast({
      title: "Export Successful",
      description: `Exported ${filteredAndSortedAssets.length} assets to CSV`,
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading assets..." />
      </div>
    )
  }

  if (hasError) {
    return (
      <ErrorMessage
        title="Error loading assets"
        message={error?.message || "An unexpected error occurred"}
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Asset Sorting & Filtering</h1>
          <p className="text-gray-600">Advanced asset management with client-side sorting</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={refetch}
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button
            variant="outline"
            onClick={exportData}
            disabled={filteredAndSortedAssets.length === 0}
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{filteredAndSortedAssets.length}</div>
              <div className="text-sm text-gray-600">Filtered Assets</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{assets.length}</div>
              <div className="text-sm text-gray-600">Total Assets</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{statistics.assigned_assets}</div>
              <div className="text-sm text-gray-600">Assigned</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-2xl font-bold">{statistics.available_assets}</div>
              <div className="text-sm text-gray-600">Available</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search assets by tag, model, vendor, serial number, or notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Quick Filters */}
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="w-4 h-4 mr-2" />
                {showFilters ? 'Hide' : 'Show'} Filters
              </Button>
              
              {(searchTerm || statusFilter !== 'all' || typeFilter !== 'all' || locationFilter !== 'all') && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                >
                  <X className="w-4 h-4 mr-2" />
                  Clear Filters
                </Button>
              )}
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      {assetStatuses.map((status) => (
                        <SelectItem key={status.AssetStatusCode} value={status.AssetStatusCode}>
                          {status.AssetStatusName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {assetTypes.map((type) => (
                        <SelectItem key={type.AssetTypeID} value={type.AssetTypeID.toString()}>
                          {type.AssetTypeName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Location</Label>
                  <Select value={locationFilter} onValueChange={setLocationFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Locations" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Locations</SelectItem>
                      {locations.map((location) => (
                        <SelectItem key={location.LocationID} value={location.LocationID.toString()}>
                          {location.LocationName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Sort Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Sort by:</span>
              
              {[
                { key: 'AssetTag', label: 'Asset Tag' },
                { key: 'Model', label: 'Model' },
                { key: 'Vendor', label: 'Vendor' },
                { key: 'AssetStatusCode', label: 'Status' },
                { key: 'PurchaseDate', label: 'Purchase Date' },
                { key: 'WarrantyEndDate', label: 'Warranty End' },
                { key: 'CreatedAt', label: 'Created Date' }
              ].map(({ key, label }) => (
                <Button
                  key={key}
                  variant={sortBy === key ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleSort(key as keyof Asset)}
                >
                  {label}
                  {sortBy === key && (
                    sortOrder === 'asc' ? <SortAsc className="w-3 h-3 ml-1" /> : <SortDesc className="w-3 h-3 ml-1" />
                  )}
                </Button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">View:</span>
              <Button
                variant={viewMode === 'grid' ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3X3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing {filteredAndSortedAssets.length} of {assets.length} assets
          {searchTerm && ` matching "${searchTerm}"`}
        </div>
      </div>

      {/* Assets Grid/List */}
      {filteredAndSortedAssets.length > 0 ? (
        <div className={
          viewMode === 'grid' 
            ? "grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
            : "space-y-4"
        }>
          {filteredAndSortedAssets.map((asset) => (
            <AssetCard
              key={asset.AssetID}
              asset={asset}
              showActions={false}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-gray-400 mb-4">
              <Search className="w-12 h-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your search criteria or filters
            </p>
            <Button variant="outline" onClick={clearFilters}>
              Clear All Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 