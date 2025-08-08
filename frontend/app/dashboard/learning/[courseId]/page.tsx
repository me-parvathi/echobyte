"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, BookOpen, Clock, Target, UserCheck, UserX, CheckCircle, Play, Lock, Award, CheckCircle2, Star } from "lucide-react"
import { useLearning, type Course, type Enrollment, type ModuleProgress, type CourseProgress, type Badge as BadgeType, type EmployeeBadge } from "@/hooks/use-learning"
import { useToast } from "@/hooks/use-toast"

export default function CourseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const courseId = parseInt(params.courseId as string)
  
  const [course, setCourse] = useState<Course | null>(null)
  const [enrollment, setEnrollment] = useState<Enrollment | null>(null)
  const [moduleProgress, setModuleProgress] = useState<ModuleProgress[]>([])
  const [courseProgress, setCourseProgress] = useState<CourseProgress | null>(null)
  const [courseBadges, setCourseBadges] = useState<BadgeType[]>([])
  const [earnedBadges, setEarnedBadges] = useState<EmployeeBadge[]>([])
  const [loading, setLoading] = useState(true)
  const [enrolling, setEnrolling] = useState(false)
  const [completingModules, setCompletingModules] = useState<Set<number>>(new Set())
  const [newlyEarnedBadges, setNewlyEarnedBadges] = useState<BadgeType[]>([])
  
  const { 
    getCourses, 
    getEnrollments, 
    enrollInCourse, 
    getModuleProgress, 
    getCourseProgress, 
    markModuleCompleted,
    getCourseBadges,
    getEmployeeBadges,
    getEmployeeCourseBadges
  } = useLearning()
  const { toast } = useToast()

  useEffect(() => {
    const fetchCourseData = async () => {
      try {
        setLoading(true)
        
        // Fetch course details, user enrollments, progress data, and badges in parallel
        const [coursesData, enrollmentsData, moduleProgressData, courseProgressData, courseBadgesData, allEarnedBadgesData] = await Promise.all([
          getCourses({ is_active: true }),
          getEnrollments(),
          getModuleProgress(courseId),
          getCourseProgress(courseId),
          getCourseBadges(courseId),
          getEmployeeBadges()
        ])

        const courses = (coursesData as any)?.courses || []
        const enrollments = (enrollmentsData as any) || []
        const moduleProgress = (moduleProgressData as any) || []
        const courseProgress = courseProgressData as any
        const courseBadges = (courseBadgesData as any) || []
        const allEarnedBadges = (allEarnedBadgesData as any) || []
        
        // Find the specific course
        const foundCourse = courses.find((c: Course) => c.CourseID === courseId)
        if (!foundCourse) {
          toast({
            title: "Error",
            description: "Course not found",
            variant: "destructive"
          })
          router.push("/dashboard/learning")
          return
        }
        
        setCourse(foundCourse)
        
        // Find enrollment for this course
        const foundEnrollment = enrollments.find((e: Enrollment) => e.CourseID === courseId)
        setEnrollment(foundEnrollment || null)
        
        // Set module progress and course progress
        setModuleProgress(moduleProgress)
        setCourseProgress(courseProgress)
        
        // Set badge data
        setCourseBadges(courseBadges)
        setEarnedBadges(allEarnedBadges)
        
      } catch (error) {
        console.error('Failed to fetch course data:', error)
        toast({
          title: "Error",
          description: "Failed to load course data",
          variant: "destructive"
        })
      } finally {
        setLoading(false)
      }
    }

    if (courseId) {
      fetchCourseData()
    }
  }, [courseId])

  const handleEnroll = async () => {
    if (!course) return
    
    try {
      setEnrolling(true)
      await enrollInCourse(course.CourseID)
      
      // Refresh enrollment data
      const enrollmentsData = await getEnrollments()
      const enrollments = (enrollmentsData as any) || []
      const foundEnrollment = enrollments.find((e: Enrollment) => e.CourseID === courseId)
      setEnrollment(foundEnrollment || null)
      
      toast({
        title: "Success",
        description: "Successfully enrolled in course",
      })
    } catch (error) {
      console.error('Failed to enroll:', error)
      toast({
        title: "Error",
        description: "Failed to enroll in course",
        variant: "destructive"
      })
    } finally {
      setEnrolling(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return "bg-green-100 text-green-800"
      case 'intermediate':
        return "bg-blue-100 text-blue-800"
      case 'advanced':
        return "bg-purple-100 text-purple-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getEnrollmentStatusColor = (status: string) => {
    switch (status) {
      case 'In-Progress':
        return "bg-yellow-100 text-yellow-800"
      case 'Completed':
        return "bg-green-100 text-green-800"
      case 'Dropped':
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getModuleStatus = (moduleId: number, moduleIndex: number) => {
    const progress = moduleProgress.find(p => p.ModuleID === moduleId)
    if (progress) return 'completed'
    if (isModuleLocked(moduleIndex)) return 'locked'
    return 'not-started'
  }

  const getModuleStatusIcon = (moduleId: number, moduleIndex: number) => {
    const status = getModuleStatus(moduleId, moduleIndex)
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'not-started':
        return <Play className="w-5 h-5 text-blue-600" />
      case 'locked':
        return <Lock className="w-5 h-5 text-gray-400" />
      default:
        return <Lock className="w-5 h-5 text-gray-400" />
    }
  }

  const getModuleStatusColor = (moduleId: number, moduleIndex: number) => {
    const status = getModuleStatus(moduleId, moduleIndex)
    switch (status) {
      case 'completed':
        return "bg-green-50 border-green-200"
      case 'not-started':
        return "bg-blue-50 border-blue-200"
      case 'locked':
        return "bg-gray-50 border-gray-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  const isModuleLocked = (moduleIndex: number) => {
    if (moduleIndex === 0) return false // First module is always unlocked
    
    // Check if all previous modules are completed
    for (let i = 0; i < moduleIndex; i++) {
      const prevModule = course?.modules?.[i]
      if (prevModule && getModuleStatus(prevModule.ModuleID) !== 'completed') {
        return true
      }
    }
    return false
  }

  // Helper functions for badge management
  const isBadgeEarned = (badgeId: number) => {
    return earnedBadges.some(earnedBadge => earnedBadge.BadgeID === badgeId)
  }

  const getEarnedBadgesForCourse = () => {
    return earnedBadges.filter(earnedBadge => 
      earnedBadge.badge?.CourseID === courseId
    )
  }

  const getBadgeProgress = (badge: BadgeType) => {
    if (!course || !courseProgress) return { progress: 0, requirement: '' }
    
    // Calculate progress based on badge type and course completion
    const totalModules = course.modules?.length || 0
    const completedModules = courseProgress.completed_modules
    
    if (badge.CourseID === courseId) {
      // Course completion badge
      const progress = totalModules > 0 ? (completedModules / totalModules) * 100 : 0
      return {
        progress: Math.min(progress, 100),
        requirement: `Complete ${totalModules} modules (${completedModules}/${totalModules})`
      }
    }
    
    return { progress: 0, requirement: 'Unknown requirement' }
  }

  const checkForNewlyEarnedBadges = (previousEarnedBadges: EmployeeBadge[], currentEarnedBadges: EmployeeBadge[]) => {
    const previousBadgeIds = new Set(previousEarnedBadges.map(b => b.BadgeID))
    const newlyEarned = currentEarnedBadges.filter(badge => !previousBadgeIds.has(badge.BadgeID))
    
    if (newlyEarned.length > 0) {
      const newBadges = newlyEarned.map(earnedBadge => 
        courseBadges.find(badge => badge.BadgeID === earnedBadge.BadgeID)
      ).filter(Boolean) as BadgeType[]
      
      setNewlyEarnedBadges(newBadges)
      
      // Show celebration toast for each new badge
      newBadges.forEach(badge => {
        toast({
          title: "🎉 Badge Earned!",
          description: `Congratulations! You've earned the "${badge.Name}" badge!`,
        })
      })
      
      // Clear newly earned badges after 5 seconds
      setTimeout(() => setNewlyEarnedBadges([]), 5000)
    }
  }

  const canCompleteModule = (moduleId: number, moduleIndex: number) => {
    const isCompleted = getModuleStatus(moduleId) === 'completed'
    const isLocked = isModuleLocked(moduleIndex)
    return !isCompleted && !isLocked
  }

  const handleMarkModuleComplete = async (moduleId: number, moduleIndex: number) => {
    console.log(`DEBUG: handleMarkModuleComplete called - ModuleID: ${moduleId}, ModuleIndex: ${moduleIndex}`)
    
    if (!canCompleteModule(moduleId, moduleIndex)) {
      console.log('DEBUG: Cannot complete module - already completed or locked')
      return
    }
    
    try {
      console.log('DEBUG: Starting module completion process')
      setCompletingModules(prev => new Set(prev).add(moduleId))
      
      // Store previous earned badges to check for new ones
      const previousEarnedBadges = [...earnedBadges]
      console.log('DEBUG: Previous earned badges count:', previousEarnedBadges.length)
      
      // Calculate estimated time spent based on course hours and module count
      let estimatedTimeMinutes = 30 // Default fallback
      if (course && course.modules && course.modules.length > 0) {
        const courseHours = parseFloat(course.EstimatedHours) || 0
        const totalModules = course.modules.length
        if (courseHours > 0 && totalModules > 0) {
          // Distribute course hours evenly across modules
          estimatedTimeMinutes = Math.round((courseHours * 60) / totalModules)
        }
      }
      
      console.log('DEBUG: Calling markModuleCompleted with estimated time:', estimatedTimeMinutes)
      await markModuleCompleted(moduleId, estimatedTimeMinutes)
      console.log('DEBUG: markModuleCompleted completed successfully')
      
      // Refresh progress data and badges
      console.log('DEBUG: Refreshing progress data and badges')
      const [moduleProgressData, courseProgressData, newEarnedBadgesData] = await Promise.all([
        getModuleProgress(courseId),
        getCourseProgress(courseId),
        getEmployeeBadges()
      ])
      
      const newEarnedBadges = (newEarnedBadgesData as any) || []
      console.log('DEBUG: New earned badges count:', newEarnedBadges.length)
      
      setModuleProgress((moduleProgressData as any) || [])
      setCourseProgress(courseProgressData as any)
      setEarnedBadges(newEarnedBadges)
      
      // Check for newly earned badges
      checkForNewlyEarnedBadges(previousEarnedBadges, newEarnedBadges)
      
      toast({
        title: "Success",
        description: "Module marked as completed!",
      })
    } catch (error) {
      console.error('Failed to mark module as completed:', error)
      toast({
        title: "Error",
        description: "Failed to mark module as completed",
        variant: "destructive"
      })
    } finally {
      setCompletingModules(prev => {
        const newSet = new Set(prev)
        newSet.delete(moduleId)
        return newSet
      })
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Course Not Found</h1>
          <Button onClick={() => router.push("/dashboard/learning")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Learning
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header with back button */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => router.push("/dashboard/learning")}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Learning
        </Button>
        
        <h1 className="text-3xl font-bold text-gray-900">{course.Title}</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Main course information */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Course Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-600">
                  {course.Description || "No description available for this course."}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Difficulty:</span>
                  <Badge className={getDifficultyColor(course.Difficulty)}>
                    {course.Difficulty}
                  </Badge>
                </div>
                
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Estimated Hours:</span>
                  <span className="font-medium">{course.EstimatedHours}</span>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900">Course Modules</h3>
                  {courseProgress && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Progress:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {courseProgress.completed_modules}/{courseProgress.total_modules} modules
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Progress Bar */}
                {courseProgress && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Course Progress</span>
                      <span>{Math.round(courseProgress.progress_percentage)}%</span>
                    </div>
                    <Progress value={courseProgress.progress_percentage} className="h-2" />
                  </div>
                )}
                
                <div className="space-y-3">
                  {course.modules && course.modules.length > 0 ? (
                    course.modules.map((module, index) => {
                      const moduleStatus = getModuleStatus(module.ModuleID, index)
                      const isCompleted = moduleStatus === 'completed'
                      const isLocked = moduleStatus === 'locked'
                      const canComplete = canCompleteModule(module.ModuleID, index)
                      const isCompleting = completingModules.has(module.ModuleID)
                      const completedAt = moduleProgress.find(p => p.ModuleID === module.ModuleID)?.CompletedAt
                      
                      return (
                        <div 
                          key={module.ModuleID} 
                          className={`flex items-center gap-3 p-4 rounded-lg border ${getModuleStatusColor(module.ModuleID, index)}`}
                        >
                          <div className="flex-shrink-0">
                            {getModuleStatusIcon(module.ModuleID, index)}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium text-gray-500">Module {module.ModuleSeq}</span>
                              {isCompleted && (
                                <Badge variant="secondary" className="text-xs">
                                  Completed
                                </Badge>
                              )}
                              {isLocked && (
                                <Badge variant="outline" className="text-xs text-gray-500">
                                  Locked
                                </Badge>
                              )}
                            </div>
                            <h4 className="font-medium text-gray-900 mb-1">{module.Title}</h4>
                            {isCompleted && completedAt && (
                              <p className="text-xs text-gray-500">
                                Completed on {new Date(completedAt).toLocaleDateString()}
                              </p>
                            )}
                            {isLocked && (
                              <p className="text-xs text-gray-500">
                                Complete previous modules to unlock
                              </p>
                            )}
                          </div>
                          <div className="flex-shrink-0 flex gap-2">
                            {canComplete && (
                              <Button 
                                variant="default" 
                                size="sm"
                                onClick={() => handleMarkModuleComplete(module.ModuleID, index)}
                                disabled={isCompleting}
                              >
                                {isCompleting ? "Completing..." : "Mark Complete"}
                              </Button>
                            )}
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => router.push(`/dashboard/learning/${courseId}/modules/${module.ModuleID}`)}
                              disabled={isLocked}
                            >
                              {isCompleted ? 'Review' : isLocked ? 'Locked' : 'Start'}
                            </Button>
                          </div>
                        </div>
                      )
                    })
                  ) : (
                    <p className="text-gray-500 italic">No modules available for this course.</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enrollment status and actions */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {enrollment ? <UserCheck className="h-5 w-5" /> : <UserX className="h-5 w-5" />}
                Enrollment Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {enrollment ? (
                <div className="space-y-4">
                  <Badge className={getEnrollmentStatusColor(enrollment.Status)}>
                    {enrollment.Status}
                  </Badge>
                  
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Enrolled:</strong> {new Date(enrollment.EnrolledAt).toLocaleDateString()}</p>
                    {enrollment.CompletedAt && (
                      <p><strong>Completed:</strong> {new Date(enrollment.CompletedAt).toLocaleDateString()}</p>
                    )}
                  </div>
                  
                  {courseProgress && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Time Spent:</span>
                        <span className="font-medium">{courseProgress.total_time_spent_minutes} minutes</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Time Remaining:</span>
                        <span className="font-medium">{courseProgress.estimated_time_remaining_minutes} minutes</span>
                      </div>
                    </div>
                  )}
                  
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => router.push(`/dashboard/learning/${courseId}/modules`)}
                  >
                    Continue Learning
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-gray-600">
                    You are not enrolled in this course yet.
                  </p>
                  
                  <Button 
                    onClick={handleEnroll}
                    disabled={enrolling}
                    className="w-full"
                  >
                    {enrolling ? "Enrolling..." : "Enroll in Course"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Course Badges Section */}
          {courseBadges.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Course Badges
                </CardTitle>
                <CardDescription>
                  Earn badges by completing course requirements
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {courseBadges.map((badge) => {
                  const isEarned = isBadgeEarned(badge.BadgeID)
                  const { progress, requirement } = getBadgeProgress(badge)
                  const isNewlyEarned = newlyEarnedBadges.some(newBadge => newBadge.BadgeID === badge.BadgeID)
                  
                  return (
                    <div
                      key={badge.BadgeID}
                      className={`p-4 rounded-lg border transition-all duration-300 ${
                        isEarned 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-gray-50 border-gray-200'
                      } ${isNewlyEarned ? 'animate-pulse ring-2 ring-green-400' : ''}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`flex-shrink-0 p-2 rounded-full ${
                          isEarned 
                            ? 'bg-green-100 text-green-600' 
                            : 'bg-gray-100 text-gray-500'
                        }`}>
                          {isEarned ? (
                            <CheckCircle2 className="w-5 h-5" />
                          ) : (
                            <Award className="w-5 h-5" />
                          )}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-gray-900 truncate">{badge.Name}</h4>
                            {isEarned && (
                              <Badge variant="secondary" className="text-xs">
                                Earned
                              </Badge>
                            )}
                            {isNewlyEarned && (
                              <Badge className="bg-green-100 text-green-800 text-xs animate-pulse">
                                <Star className="w-3 h-3 mr-1" />
                                New!
                              </Badge>
                            )}
                          </div>
                          
                          {badge.Description && (
                            <p className="text-sm text-gray-600 mb-2">{badge.Description}</p>
                          )}
                          
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs text-gray-500">
                              <span>Progress</span>
                              <span>{Math.round(progress)}%</span>
                            </div>
                            <Progress value={progress} className="h-2" />
                            <p className="text-xs text-gray-500">{requirement}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
} 