import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

export interface Course {
  CourseID: number
  CourseCode: string
  Title: string
  Difficulty: string
  EstimatedHours: number
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string
  modules: CourseModule[]
}

export interface CourseModule {
  ModuleID: number
  CourseID: number
  ModuleSeq: number
  Title: string
  VideoURL: string
  VideoType: string
}

export interface Enrollment {
  EmployeeCourseID: number
  EmployeeID: number
  CourseID: number
  Status: 'In-Progress' | 'Completed' | 'Dropped'
  EnrolledAt: string
  CompletedAt?: string
  course?: Course
}

export interface ModuleProgress {
  EmpCourseID: number
  ModuleID: number
  CompletedAt: string
  TimeSpentMinutes?: number
  module?: CourseModule
}

export interface Quiz {
  QuizID: number
  CourseID?: number
  Title: string
  QuestionCount: number
  TimeLimitMin: number
  PassingPct: number
  IsActive: boolean
  questions?: QuizQuestion[]
}

export interface QuizQuestion {
  QuestionID: number
  QuizID: number
  QuestionSeq: number
  QuestionText: string
  Explanation?: string
  IsActive: boolean
  CreatedAt: string
  options: QuizOption[]
}

export interface QuizOption {
  OptionID: number
  QuestionID: number
  OptionSeq: number
  OptionText: string
  IsCorrect: boolean
}

export interface QuizAttempt {
  AttemptID: number
  EmployeeID: number
  QuizID: number
  StartedAt: string
  CompletedAt?: string
  ScorePct?: number
  IsPassed?: boolean
  quiz?: Quiz
}

export interface Badge {
  BadgeID: number
  BadgeCode: string
  Name: string
  Description?: string
  IconURL?: string
  IsActive: boolean
  CreatedAt: string
  CourseID?: number
  QuizID?: number
}

export interface EmployeeBadge {
  EmployeeBadgeID: number
  EmployeeID: number
  BadgeID: number
  EarnedAt: string
  badge?: Badge
}

export interface CourseProgress {
  course: Course
  enrollment: Enrollment
  completed_modules: number
  total_modules: number
  progress_percentage: number
  total_time_spent_minutes: number
  estimated_time_remaining_minutes: number
}

export interface EmployeeProgressSummary {
  total_enrollments: number
  completed_courses: number
  in_progress_courses: number
  total_badges_earned: number
  total_time_spent_hours: number
  recent_activity: Array<{
    type: string
    module_title: string
    completed_at: string
    time_spent: number
  }>
}

export function useLearning() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Get all courses
  const getCourses = async (params?: {
    skip?: number
    limit?: number
    is_active?: boolean
    difficulty?: string
    search?: string
  }) => {
    setLoading(true)
    setError(null)
    try {
      const queryParams = new URLSearchParams()
      if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString())
      if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString())
      if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
      if (params?.difficulty) queryParams.append('difficulty', params.difficulty)
      if (params?.search) queryParams.append('search', params.search)
      
      const endpoint = `/learning/courses${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch courses')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get user enrollments
  const getEnrollments = async (status?: string) => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = status ? `/learning/enrollments?status=${status}` : '/learning/enrollments'
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch enrollments')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Enroll in a course
  const enrollInCourse = async (courseId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/learning/enrollments', {
        CourseID: courseId
      })
      return response
    } catch (err) {
      setError('Failed to enroll in course')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get module progress
  const getModuleProgress = async (courseId?: number) => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = courseId ? `/learning/employeeModuleProgress?course_id=${courseId}` : '/learning/employeeModuleProgress'
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch module progress')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Mark module as completed
  const markModuleCompleted = async (moduleId: number, timeSpentMinutes?: number) => {
    console.log(`DEBUG: Frontend markModuleCompleted called - ModuleID: ${moduleId}, TimeSpent: ${timeSpentMinutes}`)
    setLoading(true)
    setError(null)
    try {
      const requestData = {
        progress: { ModuleID: moduleId },
        completion: { time_spent_minutes: timeSpentMinutes }
      }
      console.log('DEBUG: Sending request data:', requestData)
      
      const response = await api.post('/learning/employeeModuleProgress', requestData)
      console.log('DEBUG: Module completion response:', response)
      return response
    } catch (err) {
      console.error('DEBUG: Module completion error:', err)
      setError('Failed to mark module as completed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get course progress
  const getCourseProgress = async (courseId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/courses/${courseId}/progress`)
      return response
    } catch (err) {
      setError('Failed to fetch course progress')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get employee progress summary
  const getProgressSummary = async () => {
    setLoading(true)
    setError(null)
    try {
      // The backend will automatically use the current user's EmployeeID
      const response = await api.get('/learning/employee/progress-summary')
      return response
    } catch (err) {
      setError('Failed to fetch progress summary')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quizzes
  const getQuizzes = async (courseId?: number, isActive?: boolean) => {
    setLoading(true)
    setError(null)
    try {
      const queryParams = new URLSearchParams()
      if (courseId !== undefined) queryParams.append('course_id', courseId.toString())
      if (isActive !== undefined) queryParams.append('is_active', isActive.toString())
      
      const endpoint = `/learning/quizzes${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch quizzes')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quiz by ID
  const getQuiz = async (quizId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/quizzes/${quizId}`)
      return response
    } catch (err) {
      setError('Failed to fetch quiz')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quiz attempts
  const getQuizAttempts = async (quizId?: number) => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = quizId ? `/learning/quizAttempts?quiz_id=${quizId}` : '/learning/quizAttempts'
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch quiz attempts')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Start quiz attempt
  const startQuizAttempt = async (quizId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/learning/quizAttempts', {
        QuizID: quizId
      })
      return response
    } catch (err) {
      setError('Failed to start quiz attempt')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Submit quiz attempt
  const submitQuizAttempt = async (attemptId: number, responses: Array<{
    QuestionID: number
    OptionID: number
  }>) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.put(`/learning/quizAttempts/${attemptId}`, {
        responses
      })
      return response
    } catch (err) {
      setError('Failed to submit quiz attempt')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get badges
  const getBadges = async (isActive?: boolean) => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = isActive !== undefined ? `/learning/badges?is_active=${isActive}` : '/learning/badges'
      const response = await api.get(endpoint)
      return response
    } catch (err) {
      setError('Failed to fetch badges')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get employee badges
  const getEmployeeBadges = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get('/learning/employeeBadges')
      return response
    } catch (err) {
      setError('Failed to fetch employee badges')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get course badges
  const getCourseBadges = async (courseId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/courses/${courseId}/badges`)
      return response
    } catch (err) {
      setError('Failed to fetch course badges')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quiz badges
  const getQuizBadges = async (quizId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/quizzes/${quizId}/badges`)
      return response
    } catch (err) {
      setError('Failed to fetch quiz badges')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get available badges for course
  const getAvailableBadgesForCourse = async (courseId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/courses/${courseId}/available-badges`)
      return response
    } catch (err) {
      setError('Failed to fetch available badges for course')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get employee course badges
  const getEmployeeCourseBadges = async (employeeId: number, courseId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/employees/${employeeId}/course-badges/${courseId}`)
      return response
    } catch (err) {
      setError('Failed to fetch employee course badges')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get random quiz questions
  const getRandomQuizQuestions = async (quizId: number, questionCount: number = 5) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/quizzes/${quizId}/random-questions?question_count=${questionCount}`)
      return response
    } catch (err) {
      setError('Failed to fetch quiz questions')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quiz cooldown information
  const getQuizCooldownInfo = async (quizId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/quizzes/${quizId}/cooldown-info`)
      return response
    } catch (err) {
      setError('Failed to fetch quiz cooldown information')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Get quiz results with detailed answers and explanations
  const getQuizResults = async (attemptId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/learning/quizAttempts/${attemptId}/results`)
      return response
    } catch (err) {
      setError('Failed to fetch quiz results')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    getCourses,
    getEnrollments,
    enrollInCourse,
    getModuleProgress,
    markModuleCompleted,
    getCourseProgress,
    getProgressSummary,
    getQuizzes,
    getQuiz,
    getQuizAttempts,
    startQuizAttempt,
    submitQuizAttempt,
    getBadges,
    getEmployeeBadges,
    getCourseBadges,
    getQuizBadges,
    getAvailableBadgesForCourse,
    getEmployeeCourseBadges,
    getRandomQuizQuestions,
    getQuizCooldownInfo,
    getQuizResults
  }
} 