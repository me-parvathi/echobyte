"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { FileText, Video, ImageIcon, Download, Eye, Search, BookOpen, Clock, CheckCircle, Play } from "lucide-react"

export default function InductionMaterials() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")

  const materials = [
    {
      id: 1,
      title: "Employee Handbook 2024",
      type: "pdf",
      category: "policies",
      size: "2.4 MB",
      lastUpdated: "2024-01-15",
      description: "Complete guide to company policies, procedures, and benefits",
      readTime: "45 min",
      completed: true,
      mandatory: true,
    },
    {
      id: 2,
      title: "Code of Conduct",
      type: "pdf",
      category: "policies",
      size: "1.2 MB",
      lastUpdated: "2024-02-01",
      description: "Professional standards and ethical guidelines",
      readTime: "20 min",
      completed: true,
      mandatory: true,
    },
    {
      id: 3,
      title: "Welcome to Our Company",
      type: "video",
      category: "orientation",
      size: "156 MB",
      duration: "15:30",
      lastUpdated: "2024-03-10",
      description: "CEO welcome message and company overview",
      completed: false,
      mandatory: true,
    },
    {
      id: 4,
      title: "IT Security Training",
      type: "video",
      category: "training",
      size: "89 MB",
      duration: "12:45",
      lastUpdated: "2024-02-20",
      description: "Cybersecurity best practices and password policies",
      completed: false,
      mandatory: true,
    },
    {
      id: 5,
      title: "Office Layout & Facilities",
      type: "image",
      category: "facilities",
      size: "5.6 MB",
      lastUpdated: "2024-01-30",
      description: "Interactive office map and facility locations",
      completed: true,
      mandatory: false,
    },
    {
      id: 6,
      title: "Emergency Procedures",
      type: "pdf",
      category: "safety",
      size: "800 KB",
      lastUpdated: "2024-03-01",
      description: "Fire safety, evacuation routes, and emergency contacts",
      readTime: "10 min",
      completed: false,
      mandatory: true,
    },
    {
      id: 7,
      title: "Benefits Overview Presentation",
      type: "pdf",
      category: "benefits",
      size: "3.1 MB",
      lastUpdated: "2024-01-20",
      description: "Health insurance, retirement plans, and perks",
      readTime: "25 min",
      completed: true,
      mandatory: false,
    },
    {
      id: 8,
      title: "Company Culture & Values",
      type: "video",
      category: "culture",
      size: "124 MB",
      duration: "18:20",
      lastUpdated: "2024-02-15",
      description: "Our mission, values, and workplace culture",
      completed: false,
      mandatory: false,
    },
  ]

  const categories = [
    { id: "all", label: "All Materials", count: materials.length },
    { id: "policies", label: "Policies", count: materials.filter((m) => m.category === "policies").length },
    { id: "orientation", label: "Orientation", count: materials.filter((m) => m.category === "orientation").length },
    { id: "training", label: "Training", count: materials.filter((m) => m.category === "training").length },
    { id: "safety", label: "Safety", count: materials.filter((m) => m.category === "safety").length },
    { id: "benefits", label: "Benefits", count: materials.filter((m) => m.category === "benefits").length },
    { id: "culture", label: "Culture", count: materials.filter((m) => m.category === "culture").length },
    { id: "facilities", label: "Facilities", count: materials.filter((m) => m.category === "facilities").length },
  ]

  const filteredMaterials = materials.filter((material) => {
    const matchesSearch =
      material.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      material.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || material.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const getFileIcon = (type: string) => {
    switch (type) {
      case "pdf":
        return <FileText className="w-5 h-5 text-red-600" />
      case "video":
        return <Video className="w-5 h-5 text-blue-600" />
      case "image":
        return <ImageIcon className="w-5 h-5 text-green-600" />
      default:
        return <FileText className="w-5 h-5 text-gray-600" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "pdf":
        return "bg-red-100 text-red-800"
      case "video":
        return "bg-blue-100 text-blue-800"
      case "image":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const completedCount = materials.filter((m) => m.completed).length
  const mandatoryCount = materials.filter((m) => m.mandatory).length
  const mandatoryCompleted = materials.filter((m) => m.mandatory && m.completed).length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Induction Materials</h2>
        <p className="text-gray-600">Company policies, procedures, and orientation materials</p>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-xl">
                <BookOpen className="w-6 h-6 text-blue-600" />
              </div>
              <Badge className="bg-blue-100 text-blue-800">
                {completedCount}/{materials.length}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Materials Completed</p>
              <p className="text-2xl font-bold text-gray-900">{completedCount}</p>
              <p className="text-xs text-gray-500">Out of {materials.length} total</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-orange-50 rounded-xl">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <Badge className="bg-orange-100 text-orange-800">
                {mandatoryCompleted}/{mandatoryCount}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Mandatory Items</p>
              <p className="text-2xl font-bold text-gray-900">{mandatoryCompleted}</p>
              <p className="text-xs text-gray-500">Completed mandatory items</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-50 rounded-xl">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <Badge className="bg-green-100 text-green-800">
                {Math.round((completedCount / materials.length) * 100)}%
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-600">Overall Progress</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(completedCount / materials.length) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">Keep up the great work!</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Categories */}
      <Card className="border-0 shadow-sm">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search materials..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-11"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className={selectedCategory === category.id ? "" : "bg-transparent"}
              >
                {category.label} ({category.count})
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Materials List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredMaterials.map((material) => (
          <Card key={material.id} className="border-0 shadow-sm hover:shadow-lg transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getFileIcon(material.type)}
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{material.title}</h3>
                      {material.mandatory && <Badge className="bg-red-100 text-red-800 text-xs">Required</Badge>}
                    </div>
                    <Badge className={`${getTypeColor(material.type)} text-xs`}>{material.type.toUpperCase()}</Badge>
                  </div>
                </div>

                {material.completed ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <Clock className="w-5 h-5 text-orange-600" />
                )}
              </div>

              <p className="text-sm text-gray-600 mb-4">{material.description}</p>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <div className="flex items-center gap-4">
                  <span>Size: {material.size}</span>
                  {material.readTime && <span>Read time: {material.readTime}</span>}
                  {material.duration && <span>Duration: {material.duration}</span>}
                </div>
                <span>Updated: {material.lastUpdated}</span>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                  <Eye className="w-4 h-4 mr-1" />
                  {material.type === "video" ? "Watch" : "View"}
                </Button>
                <Button size="sm" variant="outline" className="bg-transparent">
                  <Download className="w-4 h-4" />
                </Button>
                {material.type === "video" && !material.completed && (
                  <Button
                    size="sm"
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    <Play className="w-4 h-4 mr-1" />
                    Play
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredMaterials.length === 0 && (
        <Card className="border-0 shadow-sm">
          <CardContent className="p-12 text-center">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No materials found</h3>
            <p className="text-gray-600">Try adjusting your search or category filter</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
