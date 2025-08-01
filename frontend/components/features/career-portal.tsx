"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Briefcase,
  MapPin,
  Clock,
  DollarSign,
  Users,
  Search,
  Filter,
  BookmarkPlus,
  ExternalLink,
  TrendingUp,
} from "lucide-react"

export default function CareerPortal() {
  const [searchTerm, setSearchTerm] = useState("")
  const [departmentFilter, setDepartmentFilter] = useState("All Departments")
  const [locationFilter, setLocationFilter] = useState("All Locations")

  const jobOpenings = [
    {
      id: 1,
      title: "Senior Frontend Developer",
      department: "Engineering",
      location: "New York, NY",
      type: "Full-time",
      level: "Senior",
      salary: "$90,000 - $120,000",
      posted: "2 days ago",
      applicants: 12,
      description:
        "Join our engineering team to build cutting-edge web applications using React, TypeScript, and modern development practices.",
      requirements: ["5+ years React experience", "TypeScript proficiency", "Team leadership skills"],
      benefits: ["Health insurance", "401k matching", "Flexible hours", "Remote work options"],
      urgent: false,
    },
    {
      id: 2,
      title: "Product Marketing Manager",
      department: "Marketing",
      location: "San Francisco, CA",
      type: "Full-time",
      level: "Mid-level",
      salary: "$75,000 - $95,000",
      posted: "1 week ago",
      applicants: 8,
      description: "Drive product marketing strategy and go-to-market execution for our flagship products.",
      requirements: ["3+ years product marketing", "B2B SaaS experience", "Analytics skills"],
      benefits: ["Health insurance", "Stock options", "Professional development", "Gym membership"],
      urgent: true,
    },
    {
      id: 3,
      title: "HR Business Partner",
      department: "Human Resources",
      location: "Chicago, IL",
      type: "Full-time",
      level: "Senior",
      salary: "$70,000 - $85,000",
      posted: "3 days ago",
      applicants: 15,
      description: "Partner with business leaders to drive HR strategy and support organizational growth.",
      requirements: ["5+ years HR experience", "Business partnering experience", "Change management"],
      benefits: ["Comprehensive health coverage", "Retirement planning", "Learning stipend"],
      urgent: false,
    },
    {
      id: 4,
      title: "DevOps Engineer",
      department: "Engineering",
      location: "Austin, TX",
      type: "Full-time",
      level: "Mid-level",
      salary: "$80,000 - $100,000",
      posted: "5 days ago",
      applicants: 6,
      description: "Build and maintain our cloud infrastructure and deployment pipelines.",
      requirements: ["AWS/Azure experience", "Kubernetes knowledge", "CI/CD expertise"],
      benefits: ["Health insurance", "Flexible PTO", "Home office stipend", "Conference budget"],
      urgent: true,
    },
    {
      id: 5,
      title: "UX Designer",
      department: "Design",
      location: "Remote",
      type: "Full-time",
      level: "Mid-level",
      salary: "$65,000 - $80,000",
      posted: "1 week ago",
      applicants: 20,
      description: "Create intuitive and engaging user experiences for our web and mobile applications.",
      requirements: ["3+ years UX design", "Figma proficiency", "User research experience"],
      benefits: ["Remote work", "Design tool subscriptions", "Health insurance", "Flexible schedule"],
      urgent: false,
    },
    {
      id: 6,
      title: "Data Analyst",
      department: "Analytics",
      location: "Boston, MA",
      type: "Full-time",
      level: "Junior",
      salary: "$55,000 - $70,000",
      posted: "4 days ago",
      applicants: 25,
      description: "Analyze business data to provide insights and support data-driven decision making.",
      requirements: ["SQL proficiency", "Python/R knowledge", "Statistics background"],
      benefits: ["Health insurance", "Learning opportunities", "Mentorship program", "Flexible hours"],
      urgent: false,
    },
  ]

  const departments = ["Engineering", "Marketing", "Human Resources", "Design", "Analytics", "Sales", "Operations"]
  const locations = ["New York, NY", "San Francisco, CA", "Chicago, IL", "Austin, TX", "Boston, MA", "Remote"]

  const filteredJobs = jobOpenings.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.department.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDepartment = departmentFilter === "All Departments" || job.department === departmentFilter
    const matchesLocation = locationFilter === "All Locations" || job.location === locationFilter

    return matchesSearch && matchesDepartment && matchesLocation
  })

  const getLevelColor = (level: string) => {
    switch (level) {
      case "Junior":
        return "bg-green-100 text-green-800"
      case "Mid-level":
        return "bg-blue-100 text-blue-800"
      case "Senior":
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Career Portal</h2>
        <p className="text-gray-600">Explore internal job opportunities and advance your career</p>
      </div>

      {/* Search and Filters */}
      <Card className="border-0 shadow-sm">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-11"
              />
            </div>

            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Departments" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Departments">All Departments</SelectItem>
                {departments.map((dept) => (
                  <SelectItem key={dept} value={dept}>
                    {dept}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={locationFilter} onValueChange={setLocationFilter}>
              <SelectTrigger className="h-11">
                <SelectValue placeholder="All Locations" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All Locations">All Locations</SelectItem>
                {locations.map((location) => (
                  <SelectItem key={location} value={location}>
                    {location}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" className="h-11 bg-transparent">
              <Filter className="w-4 h-4 mr-2" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Job Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-xl">
                <Briefcase className="w-6 h-6 text-blue-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Open Positions</p>
              <p className="text-2xl font-bold text-gray-900">{filteredJobs.length}</p>
              <p className="text-xs text-gray-500">Across all departments</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-50 rounded-xl">
                <Users className="w-6 h-6 text-green-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Internal Hires</p>
              <p className="text-2xl font-bold text-gray-900">23</p>
              <p className="text-xs text-gray-500">This quarter</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-xl">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Avg. Time to Fill</p>
              <p className="text-2xl font-bold text-gray-900">18 days</p>
              <p className="text-xs text-gray-500">Internal positions</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Job Listings */}
      <div className="space-y-6">
        {filteredJobs.map((job) => (
          <Card key={job.id} className="border-0 shadow-sm hover:shadow-lg transition-all duration-200">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{job.title}</h3>
                    {job.urgent && <Badge className="bg-red-100 text-red-800">Urgent</Badge>}
                    <Badge className={getLevelColor(job.level)}>{job.level}</Badge>
                  </div>

                  <div className="flex items-center gap-6 text-sm text-gray-600 mb-3">
                    <div className="flex items-center gap-1">
                      <Briefcase className="w-4 h-4" />
                      {job.department}
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {job.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {job.type}
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      {job.salary}
                    </div>
                  </div>

                  <p className="text-gray-700 mb-4">{job.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {job.requirements.map((req, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                            {req}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Benefits</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {job.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-green-600 rounded-full" />
                            {benefit}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-3 ml-6">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Posted {job.posted}</p>
                    <p className="text-sm text-gray-500">{job.applicants} applicants</p>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="bg-transparent">
                      <BookmarkPlus className="w-4 h-4 mr-1" />
                      Save
                    </Button>
                    <Button
                      size="sm"
                      className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      Apply Now
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredJobs.length === 0 && (
        <Card className="border-0 shadow-sm">
          <CardContent className="p-12 text-center">
            <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
