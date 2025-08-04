"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Award, BookOpen, Clock, Star, Trophy, Play, CheckCircle, Lock, Target, TrendingUp, CheckCircle2, Info } from "lucide-react"
import { useLearning, type Course, type Enrollment, type Quiz, type QuizAttempt, type EmployeeBadge } from "@/hooks/use-learning"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { 
  LearningStatsSkeleton, 
  LearningTracksSkeleton, 
  QuizSectionSkeleton, 
  BadgesSectionSkeleton 
} from "@/components/ui/learning-skeleton"
import { api } from "@/lib/api"

export default function LearningModules() {
  const [selectedTrack, setSelectedTrack] = useState("all")
  const [courses, setCourses] = useState<Course[]>([])
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const [moduleProgress, setModuleProgress] = useState<any[]>([])
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [quizAttempts, setQuizAttempts] = useState<QuizAttempt[]>([])
  const [earnedBadges, setEarnedBadges] = useState<EmployeeBadge[]>([])
  const [progressSummary, setProgressSummary] = useState<any>(null)
  
  // Progressive loading states
  const [loadingCourses, setLoadingCourses] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState(true)
  const [loadingQuizzes, setLoadingQuizzes] = useState(true)
  const [loadingBadges, setLoadingBadges] = useState(true)
  
  const { 
    error, 
    getCourses, 
    getEnrollments, 
    getModuleProgress,
    enrollInCourse, 
    getQuizzes, 
    getQuizAttempts, 
    getEmployeeBadges,
    getProgressSummary
  } = useLearning()
  
  const { toast } = useToast()
  const router = useRouter()

  // Priority 1: Core content (courses and enrollments)
  useEffect(() => {
    const fetchCoreContent = async () => {
      try {
        const [coursesData, enrollmentsData] = await Promise.all([
          getCourses({ is_active: true }),
          getEnrollments()
        ])

        const courses = (coursesData as any)?.courses || []
        setCourses(courses)
        setEnrollments((enrollmentsData as any) || [])
      } catch (err) {
        console.error('Failed to fetch core content:', err)
        toast({
          title: "Error",
          description: "Failed to load courses and enrollments",
          variant: "destructive"
        })
      } finally {
        setLoadingCourses(false)
      }
    }

    fetchCoreContent()
  }, [])

  // Priority 2: Progress data (module progress and summary)
  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        const [moduleProgressData, summaryData] = await Promise.all([
          getModuleProgress(),
          getProgressSummary()
        ])

        setModuleProgress((moduleProgressData as any) || [])
        setProgressSummary(summaryData as any)
      } catch (err) {
        console.error('Failed to fetch progress data:', err)
        toast({
          title: "Error",
          description: "Failed to load progress data",
          variant: "destructive"
        })
      } finally {
        setLoadingProgress(false)
      }
    }

    // Start fetching progress data after core content loads
    if (!loadingCourses) {
      fetchProgressData()
    }
  }, [loadingCourses])

  // Priority 3: Secondary content (quizzes and attempts)
  useEffect(() => {
    const fetchQuizData = async () => {
      try {
        const [quizzesData, attemptsData] = await Promise.all([
          getQuizzes(undefined, true),
          getQuizAttempts()
        ])

        setQuizzes((quizzesData as any) || [])
        setQuizAttempts((attemptsData as any) || [])
      } catch (err) {
        console.error('Failed to fetch quiz data:', err)
        toast({
          title: "Error",
          description: "Failed to load quiz data",
          variant: "destructive"
        })
      } finally {
        setLoadingQuizzes(false)
      }
    }

    // Start fetching quiz data after progress data loads
    if (!loadingProgress) {
      fetchQuizData()
    }
  }, [loadingProgress])

  // Priority 4: Achievements (employee badges)
  useEffect(() => {
    const fetchBadgeData = async () => {
      try {
        const badgesData = await getEmployeeBadges()
        setEarnedBadges((badgesData as any) || [])
      } catch (err) {
        console.error('Failed to fetch badge data:', err)
        toast({
          title: "Error",
          description: "Failed to load badge data",
          variant: "destructive"
        })
      } finally {
        setLoadingBadges(false)
      }
    }

    // Start fetching badge data after quiz data loads
    if (!loadingQuizzes) {
      fetchBadgeData()
    }
  }, [loadingQuizzes])

  // Transform courses into learning tracks format
  const learningTracks = courses.map(course => {
    const enrollment = enrollments.find(e => e.CourseID === course.CourseID)
    const totalModules = course.modules?.length || 0
    
    // Calculate completed modules based on actual module progress
    let completedModules = 0
    if (enrollment && course.modules) {
      // Count modules that have progress records
      completedModules = course.modules.filter(module => 
        moduleProgress.some(progress => progress.ModuleID === module.ModuleID)
      ).length
    }
    
    // Get color scheme based on course difficulty
    const getColorScheme = (difficulty: string) => {
      switch (difficulty.toLowerCase()) {
        case 'beginner':
          return {
            color: "bg-green-600",
            bgColor: "bg-green-50",
            textColor: "text-green-600"
          }
        case 'intermediate':
          return {
            color: "bg-blue-600",
            bgColor: "bg-blue-50",
            textColor: "text-blue-600"
          }
        case 'advanced':
          return {
            color: "bg-purple-600",
            bgColor: "bg-purple-50",
            textColor: "text-purple-600"
          }
        default:
          return {
            color: "bg-gray-600",
            bgColor: "bg-gray-50",
            textColor: "text-gray-600"
          }
      }
    }

    const colorScheme = getColorScheme(course.Difficulty)
    
    // Generate badge name based on course title
    const courseName = course.Title.split(' ')[0]
    const badgeName = `${course.Difficulty} ${courseName} Expert`
    
    return {
      id: course.CourseID.toString(),
      title: course.Title,
      description: `Master ${course.Title.toLowerCase()} concepts and practices`,
      modules: totalModules,
      completedModules: completedModules,
      estimatedTime: `${course.EstimatedHours} hours`,
      difficulty: course.Difficulty,
      badge: badgeName,
      ...colorScheme,
      enrollment,
      course
    }
  })

  // Transform quizzes into the expected format
  const azureQuizzes = quizzes.map(quiz => {
    const attempts = quizAttempts.filter(a => a.QuizID === quiz.QuizID)
    const lastAttempt = attempts.length > 0 ? attempts[0] : null
    
    let status = 'available'
    if (lastAttempt?.IsPassed) {
      status = 'passed'
    } else if (lastAttempt && !lastAttempt.IsPassed) {
      status = 'failed'
    } else if (attempts.length >= 2) {
      status = 'locked'
    }

    return {
      id: quiz.QuizID,
      title: quiz.Title,
      questions: quiz.QuestionCount,
      timeLimit: quiz.TimeLimitMin,
      difficulty: 'Intermediate', // Default difficulty since Quiz type doesn't have Difficulty
      lastAttempt: lastAttempt?.ScorePct ? `${Math.round(lastAttempt.ScorePct)}%` : null,
      attempts: attempts.length,
      maxAttempts: 2, // Based on backend implementation
      status,
      quiz
    }
  })

  // Transform badges into the expected format
  const transformedBadges = earnedBadges.map(badge => ({
    id: badge.EmployeeBadgeID,
    name: badge.badge?.Name || 'Unknown Badge',
    description: badge.badge?.Description || 'Achievement unlocked',
    earnedDate: new Date(badge.EarnedAt).toLocaleDateString(),
    color: "bg-blue-600", // Default color
    badge
  }))

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Beginner":
        return "bg-green-100 text-green-800"
      case "Intermediate":
        return "bg-yellow-100 text-yellow-800"
      case "Advanced":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getQuizStatusColor = (status: string) => {
    switch (status) {
      case "passed":
        return "bg-green-100 text-green-800"
      case "failed":
        return "bg-red-100 text-red-800"
      case "available":
        return "bg-blue-100 text-blue-800"
      case "locked":
        return "bg-gray-100 text-gray-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getQuizStatusIcon = (status: string) => {
    switch (status) {
      case "passed":
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case "failed":
        return <Target className="w-4 h-4 text-red-600" />
      case "available":
        return <Play className="w-4 h-4 text-blue-600" />
      case "locked":
        return <Lock className="w-4 h-4 text-gray-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-600" />
    }
  }

  const handleEnrollInCourse = async (courseId: number) => {
    try {
      await enrollInCourse(courseId)
      toast({
        title: "Success",
        description: "Successfully enrolled in course",
      })
      // Refresh enrollments and module progress
      const [newEnrollments, newModuleProgress] = await Promise.all([
        getEnrollments(),
        getModuleProgress()
      ])
      setEnrollments((newEnrollments as any) || [])
      setModuleProgress((newModuleProgress as any) || [])
      // Navigate to course detail page
      router.push(`/dashboard/learning/${courseId}`)
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to enroll in course",
        variant: "destructive"
      })
    }
  }

  const handleCourseAction = async (course: Course, enrollment: Enrollment | undefined) => {
    if (!enrollment) {
      // Not enrolled - enroll first, then navigate
      await handleEnrollInCourse(course.CourseID)
    } else {
      // Already enrolled - navigate directly to course detail
      router.push(`/dashboard/learning/${course.CourseID}`)
    }
  }

  const debugLearningHours = async () => {
    try {
      const response = await api.get('/learning/employee/progress-summary/debug') as any
      console.log('Learning Hours Debug:', response)
      toast({
        title: "Debug Info",
        description: `Check console for detailed breakdown. Total: ${response.total_time_hours}h`,
      })
    } catch (error) {
      console.error('Failed to get debug info:', error)
      toast({
        title: "Error",
        description: "Failed to get debug info",
        variant: "destructive"
      })
    }
  }

  // Show skeletons if any section is still loading
  const showSkeletons = loadingCourses || loadingProgress || loadingQuizzes || loadingBadges

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Learning & Development</h2>
        <p className="text-gray-600">Enhance your skills and earn certifications</p>
      </div>

      {/* Learning Stats */}
      {showSkeletons ? (
        <LearningStatsSkeleton />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-50 rounded-xl">
                  <BookOpen className="w-6 h-6 text-blue-600" />
                </div>
                <TrendingUp className="w-4 h-4 text-gray-400" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Courses Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progressSummary?.completed_courses || 0}
                </p>
                <p className="text-xs text-gray-500">This year</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-50 rounded-xl">
                  <Award className="w-6 h-6 text-green-600" />
                </div>
                <TrendingUp className="w-4 h-4 text-gray-400" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Badges Earned</p>
                <p className="text-2xl font-bold text-gray-900">{earnedBadges.length}</p>
                <p className="text-xs text-gray-500">Total achievements</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-50 rounded-xl">
                  <Clock className="w-6 h-6 text-purple-600" />
                </div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-gray-400" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={debugLearningHours}
                    className="h-6 w-6 p-0"
                    title="Debug Learning Hours"
                  >
                    <Info className="w-3 h-3 text-gray-400" />
                  </Button>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Learning Hours</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progressSummary?.total_time_spent_hours 
                    ? (progressSummary.total_time_spent_hours).toFixed(1)
                    : '0.0'
                  }
                </p>
                <p className="text-xs text-gray-500">Total time invested</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-50 rounded-xl">
                  <Trophy className="w-6 h-6 text-orange-600" />
                </div>
                <TrendingUp className="w-4 h-4 text-gray-400" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-600">Active Enrollments</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progressSummary?.in_progress_courses || 0}
                </p>
                <p className="text-xs text-gray-500">Currently learning</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Learning Tracks */}
      {showSkeletons ? (
        <LearningTracksSkeleton />
      ) : (
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Learning Tracks</CardTitle>
            <CardDescription>Structured learning paths to build expertise</CardDescription>
          </CardHeader>
          <CardContent>
            {learningTracks.length === 0 ? (
              <div className="text-center py-8">
                <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No courses available at the moment</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {learningTracks.map((track) => (
                  <Card key={track.id} className="border border-gray-200 hover:shadow-md transition-shadow duration-200">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className={`p-3 ${track.bgColor} rounded-xl`}>
                          <BookOpen className={`w-6 h-6 ${track.textColor}`} />
                        </div>
                        <Badge className={getDifficultyColor(track.difficulty)}>{track.difficulty}</Badge>
                      </div>

                      <h3 className="font-semibold text-gray-900 mb-2">{track.title}</h3>
                      <p className="text-sm text-gray-600 mb-4">{track.description}</p>

                      <div className="space-y-3 mb-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Progress</span>
                          <span className="font-medium">
                            {track.completedModules}/{track.modules} modules
                          </span>
                        </div>
                        <Progress value={(track.completedModules / track.modules) * 100} className="h-2" />
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {track.estimatedTime}
                        </div>
                        <div className="flex items-center gap-1">
                          <Award className="w-4 h-4" />
                          {track.badge}
                        </div>
                      </div>

                      <Button 
                        className="w-full" 
                        variant={track.completedModules > 0 ? "default" : "outline"}
                        onClick={() => handleCourseAction(track.course, track.enrollment)}
                      >
                        {track.completedModules === track.modules ? (
                          <>
                            <Trophy className="w-4 h-4 mr-2" />
                            View Course
                          </>
                        ) : track.completedModules > 0 ? (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Continue Learning
                          </>
                        ) : track.enrollment ? (
                          <>
                            <BookOpen className="w-4 h-4 mr-2" />
                            Start Learning
                          </>
                        ) : (
                          <>
                            <BookOpen className="w-4 h-4 mr-2" />
                            Enroll & Start
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Azure Certification Quizzes */}
      {showSkeletons ? (
        <QuizSectionSkeleton />
      ) : (
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Azure 104 Certification Quizzes</CardTitle>
            <CardDescription>Randomized, time-bound quizzes for DevOps compliance</CardDescription>
          </CardHeader>
          <CardContent>
            {azureQuizzes.length === 0 ? (
              <div className="text-center py-8">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No quizzes available at the moment</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {azureQuizzes.map((quiz) => (
                  <Card key={quiz.id} className="border border-gray-200 hover:shadow-md transition-shadow duration-200">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {getQuizStatusIcon(quiz.status)}
                          <div>
                            <h3 className="font-semibold text-gray-900">{quiz.title}</h3>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                              <span>{quiz.questions} questions</span>
                              <span>{quiz.timeLimit} minutes</span>
                            </div>
                          </div>
                        </div>
                        <Badge className={getDifficultyColor(quiz.difficulty)}>{quiz.difficulty}</Badge>
                      </div>

                      <div className="space-y-3 mb-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Attempts</span>
                          <span className="font-medium">
                            {quiz.attempts}/{quiz.maxAttempts}
                          </span>
                        </div>

                        {quiz.lastAttempt && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Last Score</span>
                            <span
                              className={`font-medium ${
                                Number.parseInt(quiz.lastAttempt) >= 80 ? "text-green-600" : "text-red-600"
                              }`}
                            >
                              {quiz.lastAttempt}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between mb-4">
                        <Badge className={getQuizStatusColor(quiz.status)}>
                          {quiz.status === "available" ? "Ready" : quiz.status}
                        </Badge>
                        {quiz.status === "passed" && (
                          <div className="flex items-center gap-1 text-green-600">
                            <Star className="w-4 h-4 fill-current" />
                            <span className="text-sm font-medium">Passed</span>
                          </div>
                        )}
                      </div>

                      <Button
                        className="w-full"
                        disabled={
                          quiz.status === "locked" || (quiz.status === "failed" && quiz.attempts >= quiz.maxAttempts)
                        }
                        variant={quiz.status === "passed" ? "outline" : "default"}
                        onClick={() => {
                          if (quiz.status !== "locked" && !(quiz.status === "failed" && quiz.attempts >= quiz.maxAttempts)) {
                            router.push(`/dashboard/learning/quiz/${quiz.id}`)
                          }
                        }}
                      >
                        {quiz.status === "locked" ? (
                          <>
                            <Lock className="w-4 h-4 mr-2" />
                            Locked
                          </>
                        ) : quiz.status === "passed" ? (
                          <>
                            <Trophy className="w-4 h-4 mr-2" />
                            Retake Quiz
                          </>
                        ) : quiz.attempts >= quiz.maxAttempts ? (
                          <>
                            <Target className="w-4 h-4 mr-2" />
                            Max Attempts Reached
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            {quiz.attempts > 0 ? "Retake Quiz" : "Start Quiz"}
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Earned Badges */}
      {showSkeletons ? (
        <BadgesSectionSkeleton />
      ) : (
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Your Achievements</CardTitle>
            <CardDescription>Badges and certifications you've earned</CardDescription>
          </CardHeader>
          <CardContent>
            {transformedBadges.length === 0 ? (
              <div className="text-center py-8">
                <Award className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No badges earned yet. Start learning to earn achievements!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {transformedBadges.map((badge) => (
                  <Card key={badge.id} className="border border-gray-200 hover:shadow-md transition-shadow duration-200">
                    <CardContent className="p-6 text-center">
                      <div
                        className={`w-16 h-16 ${badge.color} rounded-full flex items-center justify-center mx-auto mb-4`}
                      >
                        <Award className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-2">{badge.name}</h3>
                      <p className="text-sm text-gray-600 mb-3">{badge.description}</p>
                      <p className="text-xs text-gray-500">Earned on {badge.earnedDate}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
