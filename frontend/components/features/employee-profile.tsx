"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PasswordChangeForm } from "@/components/ui/password-change-form"
import ProfilePictureUpload from "@/components/ui/profile-picture-upload"
import { 
  formatPasswordChangeDate, 
  formatFullName, 
  formatAddress, 
  formatPhoneNumber, 
  formatDate, 
  formatEmploymentDuration, 
  formatGender,
  getInitials,
  calculateAge
} from "@/lib/utils"
import {
  User,
  MapPin,
  Calendar,
  Building2,
  Briefcase,
  GraduationCap,
  Award,
  Edit3,
  Save,
  X,
  Shield,
  Clock,
  DollarSign,
  Heart,
  Users,
  Star,
} from "lucide-react"
import useUserInfo from "@/hooks/use-user-info"
import { useProfilePicture } from "@/hooks/use-profile-picture"

interface UserInfo {
  email: string
  name: string
  department: string
  type: string
  reportsTo?: string
  managerName?: string
  employeeId?: string
  position?: string
  joinDate?: string
  passwordChangedAt?: string
  emergencyContacts?: EmergencyContact[]
  // New comprehensive fields
  employeeCode?: string
  firstName?: string
  middleName?: string
  lastName?: string
  dateOfBirth?: string
  genderCode?: string
  genderName?: string
  maritalStatus?: string
  personalEmail?: string
  personalPhone?: string
  workPhone?: string
  address1?: string
  address2?: string
  city?: string
  state?: string
  country?: string
  postalCode?: string
  hireDate?: string
  terminationDate?: string
  employmentDuration?: number
  designation?: {
    designationId: number
    designationName: string
  }
  employmentType?: {
    employmentTypeCode: string
    employmentTypeName: string
  }
  workMode?: {
    workModeCode: string
    workModeName: string
  }
  team?: {
    teamId: number
    teamName: string
    teamCode: string
  }
  departmentInfo?: {
    departmentId: number
    departmentName: string
    departmentCode: string
  }
  location?: {
    locationId: number
    locationName: string
    city: string
    state: string
    country: string
  }
  manager?: {
    employeeId: number
    employeeCode: string
    name: string
    designation: string
  }
}

interface EmergencyContact {
  ContactID: number
  EmployeeID: number
  ContactName: string
  Relationship: string
  Phone1: string
  Phone2?: string
  Email?: string
  Address?: string
  IsPrimary: boolean
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
}

interface EmployeeProfileProps {
  userInfo: UserInfo
}

export default function EmployeeProfile({ userInfo }: EmployeeProfileProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedInfo, setEditedInfo] = useState(userInfo)
  const [showPasswordChange, setShowPasswordChange] = useState(false)
  const { refetch } = useUserInfo()
  
  // Get employee ID for profile picture fetching
  const employeeId = userInfo.employeeId ? parseInt(userInfo.employeeId) : 
                    userInfo.employeeCode ? parseInt(userInfo.employeeCode) : 1
  
  console.log('User info for profile picture:', {
    employeeId: userInfo.employeeId,
    employeeCode: userInfo.employeeCode,
    resolvedEmployeeId: employeeId
  })
  
  // Fetch profile picture
  const { pictureUrl: currentPictureUrl, updatePictureUrl } = useProfilePicture(employeeId)

  const getRoleColor = (type: string) => {
    switch (type) {
      case "employee":
        return "from-orange-500 to-amber-500"
      case "manager":
        return "from-emerald-500 to-teal-500"
      case "hr":
        return "from-purple-500 to-pink-500"
      case "it":
        return "from-blue-500 to-cyan-500"
      default:
        return "from-gray-500 to-gray-600"
    }
  }

  const handleSave = () => {
    // Here you would typically save to a backend
    console.log("Saving profile:", editedInfo)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedInfo(userInfo)
    setIsEditing(false)
  }

  const formatEmergencyContact = (contacts: EmergencyContact[] | undefined): string => {
    if (!contacts || contacts.length === 0) {
      return "No emergency contacts found"
    }
    
    // Find the primary contact first, then fall back to the first contact
    const primaryContact = contacts.find(contact => contact.IsPrimary) || contacts[0]
    
    return `${primaryContact.ContactName} (${primaryContact.Relationship}) - ${primaryContact.Phone1}`
  }

  // Real data from backend
  const profileData = {
    personalInfo: {
      fullName: formatFullName(userInfo.firstName, userInfo.middleName, userInfo.lastName),
      email: userInfo.email,
      phone: formatPhoneNumber(userInfo.personalPhone || userInfo.workPhone),
      address: formatAddress(userInfo.address1, userInfo.address2, userInfo.city, userInfo.state, userInfo.country, userInfo.postalCode),
      dateOfBirth: formatDate(userInfo.dateOfBirth),
      age: calculateAge(userInfo.dateOfBirth),
      gender: formatGender(userInfo.genderCode, userInfo.genderName),
      maritalStatus: userInfo.maritalStatus || "Not specified",
      personalEmail: userInfo.personalEmail || "Not provided"
    },
    workInfo: {
      employeeId: userInfo.employeeCode || userInfo.employeeId || "Not assigned",
      position: userInfo.designation?.designationName || userInfo.position || "Not assigned",
      department: userInfo.departmentInfo?.departmentName || userInfo.department || "Not assigned",
      team: userInfo.team?.teamName || "Not assigned",
      joinDate: formatDate(userInfo.hireDate || userInfo.joinDate),
      employmentDuration: formatEmploymentDuration(userInfo.employmentDuration),
      reportsTo: userInfo.manager?.name || userInfo.managerName || userInfo.reportsTo || "Not assigned",
      workLocation: userInfo.location?.locationName || "Not assigned",
      employmentType: userInfo.employmentType?.employmentTypeName || "Not assigned",
      workMode: userInfo.workMode?.workModeName || "Not assigned",
      workSchedule: "Monday - Friday, 9:00 AM - 5:00 PM" // This would come from backend if available
    },
    skills: [
      { name: "JavaScript", level: 90 },
      { name: "React", level: 85 },
      { name: "Node.js", level: 80 },
      { name: "TypeScript", level: 75 },
      { name: "Python", level: 70 },
    ],
    education: [
      {
        degree: "Bachelor of Science in Computer Science",
        institution: "University of California, Berkeley",
        year: "2018",
        gpa: "3.8/4.0",
      },
      {
        degree: "Master of Science in Software Engineering",
        institution: "Stanford University",
        year: "2020",
        gpa: "3.9/4.0",
      },
    ],
    certifications: [
      { name: "AWS Certified Developer", issuer: "Amazon", date: "2023" },
      { name: "React Developer Certification", issuer: "Meta", date: "2022" },
      { name: "Scrum Master Certified", issuer: "Scrum Alliance", date: "2021" },
    ],
    benefits: {
      healthInsurance: "Premium Health Plan",
      dentalInsurance: "Dental Plus",
      visionInsurance: "Vision Care",
      retirement: "401(k) with 6% match",
      paidTimeOff: "25 days annually",
      sickLeave: "10 days annually",
    },
    performance: {
      currentRating: 4.5,
      lastReview: "2023-12-01",
      nextReview: "2024-06-01",
      goals: ["Complete React certification", "Lead a major project", "Mentor junior developers"],
    },
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header Section */}
      <Card className="border-0 shadow-xl bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 text-white">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Avatar className="w-24 h-24 ring-4 ring-white/20">
                {currentPictureUrl && (
                  <AvatarImage src={currentPictureUrl} alt={userInfo.name} />
                )}
                <AvatarFallback className="bg-white/20 text-white text-2xl font-bold">
                  {getInitials(userInfo.name)}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-3xl font-bold mb-2">{userInfo.name}</h1>
                <p className="text-orange-100 text-lg mb-3">{profileData.workInfo.position}</p>
                <div className="flex items-center gap-4">
                  <Badge className="bg-white/20 text-white border-white/30 hover:bg-white/30">
                    {userInfo.type.charAt(0).toUpperCase() + userInfo.type.slice(1)}
                  </Badge>
                  <Badge className="bg-white/20 text-white border-white/30 hover:bg-white/30">
                    {profileData.workInfo.department}
                  </Badge>
                  <Badge className="bg-white/20 text-white border-white/30 hover:bg-white/30">
                    ID: {profileData.workInfo.employeeId}
                  </Badge>
                </div>
              </div>
            </div>
            <Button
              onClick={() => setIsEditing(!isEditing)}
              variant="secondary"
              className="bg-white/20 text-white border-white/30 hover:bg-white/30"
            >
              {isEditing ? <X className="w-4 h-4 mr-2" /> : <Edit3 className="w-4 h-4 mr-2" />}
              {isEditing ? "Cancel" : "Edit Profile"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="personal" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6 bg-white dark:bg-gray-800 shadow-lg">
          <TabsTrigger value="personal" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            Personal
          </TabsTrigger>
          <TabsTrigger value="work" className="flex items-center gap-2">
            <Briefcase className="w-4 h-4" />
            Work Info
          </TabsTrigger>
          <TabsTrigger value="skills" className="flex items-center gap-2">
            <Star className="w-4 h-4" />
            Skills
          </TabsTrigger>
          <TabsTrigger value="education" className="flex items-center gap-2">
            <GraduationCap className="w-4 h-4" />
            Education
          </TabsTrigger>
          <TabsTrigger value="benefits" className="flex items-center gap-2">
            <Heart className="w-4 h-4" />
            Benefits
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2">
            <Award className="w-4 h-4" />
            Performance
          </TabsTrigger>
        </TabsList>

        {/* Personal Information Tab */}
        <TabsContent value="personal">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5 text-orange-600" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    {isEditing ? (
                      <Input
                        id="fullName"
                        value={editedInfo.name}
                        onChange={(e) => setEditedInfo({ ...editedInfo, name: e.target.value })}
                      />
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {profileData.personalInfo.fullName}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    {isEditing ? (
                      <Input
                        id="email"
                        type="email"
                        value={editedInfo.email}
                        onChange={(e) => setEditedInfo({ ...editedInfo, email: e.target.value })}
                      />
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.personalInfo.email}</p>
                    )}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Phone</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.personalInfo.phone}</p>
                  </div>
                  <div>
                    <Label>Date of Birth</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {profileData.personalInfo.dateOfBirth}
                      {profileData.personalInfo.age && ` (${profileData.personalInfo.age} years old)`}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Gender</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.personalInfo.gender}</p>
                  </div>
                  <div>
                    <Label>Marital Status</Label>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.personalInfo.maritalStatus}</p>
                  </div>
                </div>
                <div>
                  <Label>Address</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{profileData.personalInfo.address}</p>
                </div>
                <div>
                  <Label>Emergency Contact</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {formatEmergencyContact(userInfo.emergencyContacts)}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-600" />
                  Account Security
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div>
                    <p className="font-medium text-green-800 dark:text-green-400">Two-Factor Authentication</p>
                    <p className="text-sm text-green-600 dark:text-green-500">Enabled</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div>
                    <p className="font-medium text-blue-800 dark:text-blue-400">Last Password Change</p>
                    <p className="text-sm text-blue-600 dark:text-blue-500">
                      {formatPasswordChangeDate(userInfo.passwordChangedAt)}
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setShowPasswordChange(true)}
                  >
                    Change
                  </Button>
                </div>
                
              </CardContent>
            </Card>

            {/* Profile Picture Upload */}
            <ProfilePictureUpload
              employeeId={employeeId}
              uploadedById={employeeId}
              currentPictureUrl={currentPictureUrl}
              employeeName={userInfo.name}
              onPictureUpdate={(pictureUrl) => {
                updatePictureUrl(pictureUrl)
                console.log("Profile picture updated:", pictureUrl)
              }}
            />
          </div>
        </TabsContent>

        {/* Work Information Tab */}
        <TabsContent value="work">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-blue-600" />
                Work Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Building2 className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-medium">Employee ID</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.employeeId}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <Briefcase className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="font-medium">Position</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.position}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <Users className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="font-medium">Department</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.department}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <Calendar className="w-5 h-5 text-orange-600" />
                    <div>
                      <p className="font-medium">Join Date</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.joinDate}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
                    <User className="w-5 h-5 text-teal-600" />
                    <div>
                      <p className="font-medium">Reports To</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.reportsTo}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
                    <MapPin className="w-5 h-5 text-pink-600" />
                    <div>
                      <p className="font-medium">Work Location</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.workLocation}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                    <Clock className="w-5 h-5 text-indigo-600" />
                    <div>
                      <p className="font-medium">Employment Type</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.employmentType}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <Clock className="w-5 h-5 text-yellow-600" />
                    <div>
                      <p className="font-medium">Work Mode</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.workMode}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-cyan-50 dark:bg-cyan-900/20 rounded-lg">
                    <Calendar className="w-5 h-5 text-cyan-600" />
                    <div>
                      <p className="font-medium">Employment Duration</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.workInfo.employmentDuration}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Skills Tab */}
        <TabsContent value="skills">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-600" />
                  Technical Skills
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {profileData.skills.map((skill, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">{skill.name}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">{skill.level}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-orange-500 to-amber-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${skill.level}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-purple-600" />
                  Certifications
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {profileData.certifications.map((cert, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <Award className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{cert.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {cert.issuer} • {cert.date}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Education Tab */}
        <TabsContent value="education">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-blue-600" />
                Education History
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {profileData.education.map((edu, index) => (
                <div key={index} className="flex items-start gap-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                    <GraduationCap className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{edu.degree}</h3>
                    <p className="text-blue-600 dark:text-blue-400 font-medium">{edu.institution}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <Badge variant="outline">Class of {edu.year}</Badge>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400">
                        GPA: {edu.gpa}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Benefits Tab */}
        <TabsContent value="benefits">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-red-600" />
                Benefits & Compensation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg mb-4">Health & Wellness</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <Heart className="w-5 h-5 text-red-600" />
                      <div>
                        <p className="font-medium">Health Insurance</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {profileData.benefits.healthInsurance}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <Heart className="w-5 h-5 text-blue-600" />
                      <div>
                        <p className="font-medium">Dental Insurance</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {profileData.benefits.dentalInsurance}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <Heart className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium">Vision Insurance</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {profileData.benefits.visionInsurance}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-lg mb-4">Time Off & Retirement</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <DollarSign className="w-5 h-5 text-purple-600" />
                      <div>
                        <p className="font-medium">Retirement Plan</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.benefits.retirement}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <Calendar className="w-5 h-5 text-orange-600" />
                      <div>
                        <p className="font-medium">Paid Time Off</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.benefits.paidTimeOff}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
                      <Heart className="w-5 h-5 text-teal-600" />
                      <div>
                        <p className="font-medium">Sick Leave</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{profileData.benefits.sickLeave}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-yellow-600" />
                  Performance Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full text-white text-2xl font-bold mb-4">
                    {profileData.performance.currentRating}
                  </div>
                  <p className="text-lg font-semibold">Current Rating</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Out of 5.0</p>
                </div>
                <Separator />
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Last Review</span>
                    <span className="text-gray-600 dark:text-gray-400">{profileData.performance.lastReview}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Next Review</span>
                    <span className="text-gray-600 dark:text-gray-400">{profileData.performance.nextReview}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-blue-600" />
                  Current Goals
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {profileData.performance.goals.map((goal, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="flex-1">{goal}</span>
                      <Badge variant="outline" className="text-xs">
                        In Progress
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Save/Cancel Buttons for Edit Mode */}
      {isEditing && (
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={handleCancel}>
            <X className="w-4 h-4 mr-2" />
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      )}
      
      {/* Password Change Modal */}
      {showPasswordChange && (
        <PasswordChangeForm 
          onClose={() => setShowPasswordChange(false)}
          onSuccess={() => {
            // Refresh user info to get updated password change date
            refetch()
          }}
        />
      )}
    </div>
  )
}
