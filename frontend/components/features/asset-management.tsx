"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
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
} from "lucide-react"

export default function AssetManagement() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [showAddForm, setShowAddForm] = useState(false)

  const assets = [
    {
      id: "AST-001",
      name: "Dell Laptop XPS 13",
      category: "laptop",
      serialNumber: "DL123456789",
      assignedTo: "John Doe",
      department: "Engineering",
      status: "active",
      condition: "good",
      purchaseDate: "2023-01-15",
      warrantyExpiry: "2026-01-15",
      location: "Office Floor 2",
      specifications: "Intel i7, 16GB RAM, 512GB SSD",
      lastMaintenance: "2024-06-15",
    },
    {
      id: "AST-002",
      name: "iPhone 14 Pro",
      category: "mobile",
      serialNumber: "IP987654321",
      assignedTo: "Jane Smith",
      department: "Marketing",
      status: "active",
      condition: "excellent",
      purchaseDate: "2023-09-20",
      warrantyExpiry: "2024-09-20",
      location: "Office Floor 1",
      specifications: "128GB, Space Black",
      lastMaintenance: "N/A",
    },
    {
      id: "AST-003",
      name: "HP LaserJet Pro",
      category: "printer",
      serialNumber: "HP555666777",
      assignedTo: "Shared Resource",
      department: "General",
      status: "maintenance",
      condition: "fair",
      purchaseDate: "2022-03-10",
      warrantyExpiry: "2025-03-10",
      location: "Office Floor 1 - Print Room",
      specifications: "Monochrome, Network Enabled",
      lastMaintenance: "2024-12-10",
    },
    {
      id: "AST-004",
      name: 'External Monitor 27"',
      category: "monitor",
      serialNumber: "MON789123456",
      assignedTo: "Mike Wilson",
      department: "IT Support",
      status: "active",
      condition: "good",
      purchaseDate: "2023-05-22",
      warrantyExpiry: "2026-05-22",
      location: "Office Floor 3",
      specifications: "4K, USB-C, Height Adjustable",
      lastMaintenance: "N/A",
    },
    {
      id: "AST-005",
      name: "Surface Pro 9",
      category: "tablet",
      serialNumber: "SP456789123",
      assignedTo: "Sarah Johnson",
      department: "Human Resources",
      status: "retired",
      condition: "poor",
      purchaseDate: "2021-11-30",
      warrantyExpiry: "2022-11-30",
      location: "Storage Room",
      specifications: "Intel i5, 8GB RAM, 256GB SSD",
      lastMaintenance: "2024-01-15",
    },
  ]

  const categories = [
    { value: "laptop", label: "Laptops", icon: Laptop, count: assets.filter((a) => a.category === "laptop").length },
    {
      value: "mobile",
      label: "Mobile Devices",
      icon: Smartphone,
      count: assets.filter((a) => a.category === "mobile").length,
    },
    {
      value: "monitor",
      label: "Monitors",
      icon: Monitor,
      count: assets.filter((a) => a.category === "monitor").length,
    },
    {
      value: "printer",
      label: "Printers",
      icon: Printer,
      count: assets.filter((a) => a.category === "printer").length,
    },
    { value: "tablet", label: "Tablets", icon: HardDrive, count: assets.filter((a) => a.category === "tablet").length },
  ]

  const filteredAssets = assets.filter((asset) => {
    const matchesSearch =
      asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.assignedTo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.serialNumber.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === "all" || asset.status === statusFilter
    const matchesCategory = categoryFilter === "all" || asset.category === categoryFilter

    return matchesSearch && matchesStatus && matchesCategory
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "maintenance":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />
      case "retired":
        return <XCircle className="w-4 h-4 text-red-600" />
      default:
        return <CheckCircle className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800"
      case "maintenance":
        return "bg-yellow-100 text-yellow-800"
      case "retired":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case "excellent":
        return "bg-green-100 text-green-800"
      case "good":
        return "bg-blue-100 text-blue-800"
      case "fair":
        return "bg-yellow-100 text-yellow-800"
      case "poor":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getCategoryIcon = (category: string) => {
    const categoryData = categories.find((c) => c.value === category)
    if (categoryData) {
      const Icon = categoryData.icon
      return <Icon className="w-5 h-5 text-blue-600" />
    }
    return <Monitor className="w-5 h-5 text-gray-600" />
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Asset Management</h2>
          <p className="text-gray-600">Track and manage company assets and equipment</p>
        </div>
        <Button
          onClick={() => setShowAddForm(true)}
          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Asset
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-green-500 to-emerald-600 text-white border-0">
                {assets.filter((a) => a.status === "active").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Active Assets</p>
              <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                {assets.filter((a) => a.status === "active").length}
              </p>
              <p className="text-xs text-gray-500">Currently in use</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white border-0">
                {assets.filter((a) => a.status === "maintenance").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">In Maintenance</p>
              <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                {assets.filter((a) => a.status === "maintenance").length}
              </p>
              <p className="text-xs text-gray-500">Under repair</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-red-400 to-rose-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <XCircle className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-red-500 to-rose-600 text-white border-0">
                {assets.filter((a) => a.status === "retired").length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Retired Assets</p>
              <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                {assets.filter((a) => a.status === "retired").length}
              </p>
              <p className="text-xs text-gray-500">End of life</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Monitor className="w-6 h-6 text-white" />
              </div>
              <Badge className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white border-0">{assets.length}</Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Total Assets</p>
              <p className="text-2xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                {assets.length}
              </p>
              <p className="text-xs text-gray-500">All tracked items</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="border-0 shadow-sm">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-11"
              />
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="retired">Retired</SelectItem>
              </SelectContent>
            </Select>

            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
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
        </CardContent>
      </Card>

      {/* Assets List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredAssets.map((asset) => (
          <Card
            key={asset.id}
            className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm hover:scale-105 group"
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                    {getCategoryIcon(asset.category)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">
                      {asset.name}
                    </h3>
                    <p className="text-sm text-gray-600 font-mono">{asset.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(asset.status)}
                  <Badge className={`${getStatusColor(asset.status)} border-0 shadow-sm`}>{asset.status}</Badge>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Assigned to:</span>
                  <span className="font-medium">{asset.assignedTo}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Department:</span>
                  <span>{asset.department}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Location:</span>
                  <span>{asset.location}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Condition:</span>
                  <Badge className={getConditionColor(asset.condition)}>{asset.condition}</Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Serial:</span>
                  <span className="font-mono text-xs">{asset.serialNumber}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
                <Button size="sm" variant="outline" className="bg-transparent">
                  <QrCode className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="text-red-600 border-red-200 hover:bg-red-50 bg-transparent"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAssets.length === 0 && (
        <Card className="border-0 shadow-sm">
          <CardContent className="p-12 text-center">
            <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
