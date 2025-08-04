"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useLearning } from '@/hooks/use-learning'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Clock, ChevronLeft, ChevronRight, CheckCircle, XCircle, History } from 'lucide-react'
import { toast } from 'sonner'

interface QuizAnswer {
  QuestionID: number
  OptionID: number
}

interface QuizState {
  currentQuestionIndex: number
  answers: QuizAnswer[]
  timeRemaining: number
  isSubmitted: boolean
  attemptId?: number
}

export default function QuizPage() {
  const params = useParams()
  const router = useRouter()
  const quizId = parseInt(params.quizId as string)
  
  const { 
    getRandomQuizQuestions, 
    startQuizAttempt, 
    submitQuizAttempt,
    getQuiz,
    getQuizCooldownInfo,
    getQuizAttempts,
    loading, 
    error 
  } = useLearning()

  const [quizState, setQuizState] = useState<QuizState>({
    currentQuestionIndex: 0,
    answers: [],
    timeRemaining: 0,
    isSubmitted: false
  })

  const [quizData, setQuizData] = useState<{
    quiz: any
    questions: any[]
  } | null>(null)

  const [cooldownInfo, setCooldownInfo] = useState<any>(null)
  const [isStarting, setIsStarting] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isInitializing, setIsInitializing] = useState(false) // Prevent multiple simultaneous requests
  const [attemptHistory, setAttemptHistory] = useState<any[]>([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false)
  const hasInitialized = useRef(false) // Track if initialization has been done

  // Initialize quiz
  useEffect(() => {
    // Prevent multiple initializations
    if (hasInitialized.current || !quizId) return
    
    const initializeQuiz = async () => {
      // Prevent multiple simultaneous requests
      if (isInitializing) return
      
      try {
        hasInitialized.current = true
        setIsInitializing(true)
        setIsStarting(true)
        
        // Get quiz details first
        const quiz = await getQuiz(quizId) as any
        console.log('Quiz response:', quiz)
        
        // Check cooldown info before attempting to start
        const cooldownData = await getQuizCooldownInfo(quizId) as any
        console.log('Cooldown data:', cooldownData)
        setCooldownInfo(cooldownData)
        
        if (!cooldownData.can_attempt) {
          // Show cooldown message instead of starting quiz
          setIsStarting(false)
          // Set quizData to prevent "Quiz not found" message
          setQuizData({ quiz, questions: quiz.questions || [] })
          return
        }
        
        // Only start quiz attempt if cooldown check passes
        const attemptResponse = await startQuizAttempt(quizId) as any
        const attemptId = attemptResponse.AttemptID
        
        // Get random questions - use a subset of available questions
        const totalQuestions = quiz.QuestionCount || 10
        // Configuration: Show 5 questions out of total available (adjust as needed)
        const QUESTIONS_TO_SHOW = 5
        const questionsToShow = Math.min(QUESTIONS_TO_SHOW, totalQuestions)
        const questions = await getRandomQuizQuestions(quizId, questionsToShow) as any[]
        
        setQuizData({ quiz, questions })
        setQuizState(prev => ({
          ...prev,
          attemptId,
          timeRemaining: quiz.TimeLimitMin * 60 // Convert to seconds
        }))
        
      } catch (err: any) {
        console.error('Failed to initialize quiz:', err)
        
        // Handle specific error types
        if (err?.response?.status === 429) {
          // Cooldown error - don't redirect, just show message
          toast.error(err.response.data?.detail || 'Quiz is currently on cooldown')
        } else {
          // Other errors - redirect to learning page
          toast.error('Failed to start quiz. Please try again.')
          router.push('/dashboard/learning')
        }
      } finally {
        setIsStarting(false)
        setIsInitializing(false)
      }
    }

    initializeQuiz()
  }, [quizId]) // Only depend on quizId to prevent infinite loops

  // Debug dialog state
  useEffect(() => {
    console.log('Dialog open state changed:', isHistoryDialogOpen)
    console.log('Attempt history state:', attemptHistory)
    console.log('Loading state:', isLoadingHistory)
  }, [isHistoryDialogOpen, attemptHistory, isLoadingHistory])

  // Load attempt history
  const loadAttemptHistory = async () => {
    try {
      setIsLoadingHistory(true)
      console.log('Loading attempt history for quiz:', quizId)
      const attempts = await getQuizAttempts(quizId) as any[]
      console.log('Attempts received:', attempts)
      // Get the last 2 attempts
      const lastTwoAttempts = attempts.slice(0, 2)
      console.log('Last two attempts:', lastTwoAttempts)
      setAttemptHistory(lastTwoAttempts)
    } catch (err) {
      console.error('Failed to load attempt history:', err)
      toast.error('Failed to load attempt history')
    } finally {
      setIsLoadingHistory(false)
    }
  }

  // Submit quiz
  const handleSubmitQuiz = useCallback(async () => {
    if (!quizState.attemptId || quizState.isSubmitted) return

    try {
      setIsSubmitting(true)
      
      await submitQuizAttempt(quizState.attemptId, quizState.answers)
      
      setQuizState(prev => ({ ...prev, isSubmitted: true }))
      toast.success('Quiz submitted successfully!')
      
      // Redirect to results page
      setTimeout(() => {
        router.push(`/dashboard/learning/quiz/${quizId}/results?attemptId=${quizState.attemptId}`)
      }, 2000)
      
    } catch (err) {
      console.error('Failed to submit quiz:', err)
      toast.error('Failed to submit quiz. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }, [quizState.attemptId, quizState.answers, quizState.isSubmitted, submitQuizAttempt, router])

  // Timer countdown
  useEffect(() => {
    if (!quizData || quizState.isSubmitted || quizState.timeRemaining <= 0) return

    const timer = setInterval(() => {
      setQuizState(prev => {
        const newTimeRemaining = prev.timeRemaining - 1
        
        if (newTimeRemaining <= 0) {
          // Auto-submit when time expires
          handleSubmitQuiz()
          return { ...prev, timeRemaining: 0 }
        }
        
        // Show warning when 30 seconds remaining
        if (newTimeRemaining === 30 && !prev.isSubmitted) {
          toast.warning('⚠️ 30 seconds remaining! Submit your quiz now!', {
            duration: 5000,
            action: {
              label: 'Submit Now',
              onClick: () => handleSubmitQuiz()
            }
          })
        }
        
        return { ...prev, timeRemaining: newTimeRemaining }
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [quizData, quizState.isSubmitted, handleSubmitQuiz])

  // Format time remaining
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const formatAttemptDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  // Check if time is running low (last 5 minutes)
  const isTimeLow = quizState.timeRemaining <= 300 && quizState.timeRemaining > 0 // 5 minutes = 300 seconds
  
  // Check if time is critical (last 1 minute)
  const isTimeCritical = quizState.timeRemaining <= 60 && quizState.timeRemaining > 0

  // Audio notification for low time
  useEffect(() => {
    if (isTimeCritical && quizState.timeRemaining > 0 && !quizState.isSubmitted) {
      // Create a simple beep sound using Web Audio API
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)
      
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.5)
      
      return () => {
        audioContext.close()
      }
    }
  }, [isTimeCritical, quizState.timeRemaining, quizState.isSubmitted])

  // Handle answer selection
  const handleAnswerSelect = (questionId: number, optionId: number) => {
    setQuizState(prev => {
      const existingAnswerIndex = prev.answers.findIndex(
        answer => answer.QuestionID === questionId
      )
      
      const newAnswers = [...prev.answers]
      
      if (existingAnswerIndex >= 0) {
        newAnswers[existingAnswerIndex] = { QuestionID: questionId, OptionID: optionId }
      } else {
        newAnswers.push({ QuestionID: questionId, OptionID: optionId })
      }
      
      return { ...prev, answers: newAnswers }
    })
  }

  // Get current answer for a question
  const getCurrentAnswer = (questionId: number) => {
    return quizState.answers.find(answer => answer.QuestionID === questionId)
  }

  // Navigation functions
  const goToPrevious = () => {
    if (quizState.currentQuestionIndex > 0) {
      setQuizState(prev => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex - 1
      }))
    }
  }

  const goToNext = () => {
    if (quizData && quizState.currentQuestionIndex < (quizData.questions?.length || 0) - 1) {
      setQuizState(prev => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex + 1
      }))
    }
  }

  // Handle manual submit
  const handleManualSubmit = () => {
    if (!quizData?.questions) return
    
    if (quizState.answers.length < quizData.questions.length) {
      const unanswered = quizData.questions.length - quizState.answers.length
      if (!confirm(`You have ${unanswered} unanswered question(s). Are you sure you want to submit?`)) {
        return
      }
    }
    handleSubmitQuiz()
  }

  if (isStarting || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg">Loading quiz...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Alert className="max-w-md">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!quizData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Alert className="max-w-md">
          <XCircle className="h-4 w-4" />
          <AlertDescription>Quiz not found</AlertDescription>
        </Alert>
      </div>
    )
  }

  // Show cooldown message if user can't attempt the quiz
  if (cooldownInfo && !cooldownInfo.can_attempt) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-red-600">
                ⏰ Quiz Cooldown Active
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="w-8 h-8 text-red-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Quiz Attempt Restricted
                </h2>
                <p className="text-gray-600 mb-4">
                  {cooldownInfo.reason}
                </p>
                
                {cooldownInfo.days_remaining > 0 && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                    <p className="text-orange-800 font-medium">
                      ⏳ {cooldownInfo.days_remaining} days remaining in cooldown period
                    </p>
                  </div>
                )}
                
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Attempt History</h3>
                  <p className="text-sm text-gray-600">
                    You have made {cooldownInfo.attempt_count} attempt(s) at this quiz.
                  </p>
                  {cooldownInfo.attempt_count >= 2 && (
                    <p className="text-sm text-red-600 mt-1">
                      Maximum attempts reached. Cooldown period of 4 weeks activated.
                    </p>
                  )}
                </div>
                
                {cooldownInfo.attempt_count > 0 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-blue-900 mb-2">📊 Previous Attempts</h3>
                    <p className="text-sm text-blue-700">
                      View your last 2 quiz attempts and scores.
                    </p>
                    <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="mt-2"
                          onClick={() => {
                            setIsHistoryDialogOpen(true)
                            loadAttemptHistory()
                          }}
                        >
                          <History className="w-4 h-4 mr-2" />
                          View Attempt History
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-md">
                        <DialogHeader>
                          <DialogTitle className="flex items-center gap-2">
                            <History className="w-5 h-5" />
                            Attempt History
                          </DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          {isLoadingHistory ? (
                            <div className="text-center py-4">
                              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
                              <p className="text-sm text-gray-600">Loading attempt history...</p>
                            </div>
                          ) : attemptHistory.length > 0 ? (
                            attemptHistory.map((attempt, index) => (
                              <div key={attempt.AttemptID} className="border rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-medium">Attempt {index + 1}</h4>
                                  <Badge variant={attempt.IsPassed ? "default" : "destructive"}>
                                    {attempt.IsPassed ? 'PASSED' : 'FAILED'}
                                  </Badge>
                                </div>
                                <div className="space-y-1 text-sm text-gray-600">
                                  <p><strong>Score:</strong> {attempt.ScorePct ? Number(attempt.ScorePct).toFixed(1) : 'N/A'}%</p>
                                  <p><strong>Started:</strong> {formatAttemptDate(attempt.StartedAt)}</p>
                                  {attempt.CompletedAt && (
                                    <p><strong>Completed:</strong> {formatAttemptDate(attempt.CompletedAt)}</p>
                                  )}
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="text-center py-4">
                              <p className="text-gray-500">No previous attempts found.</p>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                )}
              </div>
              
              <div className="flex gap-3 justify-center">
                <Button
                  variant="outline"
                  onClick={() => router.push('/dashboard/learning')}
                >
                  ← Back to Learning
                </Button>
                <Button
                  onClick={() => router.push('/dashboard/learning')}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Take Different Quiz
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const currentQuestion = quizData.questions[quizState.currentQuestionIndex]
  const currentAnswer = getCurrentAnswer(currentQuestion.QuestionID)
  const progress = ((quizState.currentQuestionIndex + 1) / quizData.questions.length) * 100

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">{quizData.quiz.Title}</h1>
            <div className="flex items-center gap-4">
              <Badge variant="secondary">
                Question {quizState.currentQuestionIndex + 1} of {quizData.questions.length}
              </Badge>
              <div className={`flex items-center gap-2 font-mono text-lg ${
                isTimeCritical 
                  ? 'text-red-600 animate-pulse' 
                  : isTimeLow 
                    ? 'text-orange-600' 
                    : 'text-gray-700'
              }`}>
                <Clock className={`h-4 w-4 ${
                  isTimeCritical ? 'animate-pulse' : ''
                }`} />
                <span className="font-bold">
                  {formatTime(quizState.timeRemaining)}
                </span>
                {isTimeLow && (
                  <span className="text-xs ml-2 px-2 py-1 bg-red-100 text-red-700 rounded">
                    {isTimeCritical ? 'CRITICAL!' : 'Time Low!'}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Progress bar */}
          <Progress value={progress} className="h-2" />
          
          {/* Timer Progress */}
          {quizData.quiz.TimeLimitMin && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Time Remaining</span>
                <span>{formatTime(quizState.timeRemaining)} / {formatTime(quizData.quiz.TimeLimitMin * 60)}</span>
              </div>
              <Progress 
                value={(quizState.timeRemaining / (quizData.quiz.TimeLimitMin * 60)) * 100} 
                className={`h-1 ${
                  isTimeCritical 
                    ? 'bg-red-200' 
                    : isTimeLow 
                      ? 'bg-orange-200' 
                      : 'bg-gray-200'
                }`}
              />
            </div>
          )}
        </div>

        {/* Quiz Content */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">
              Question {quizState.currentQuestionIndex + 1}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Time Warning Alert */}
            {isTimeLow && (
              <Alert className={`mb-4 ${
                isTimeCritical 
                  ? 'border-red-500 bg-red-50 text-red-700' 
                  : 'border-orange-500 bg-orange-50 text-orange-700'
              }`}>
                <Clock className={`h-4 w-4 ${
                  isTimeCritical ? 'animate-pulse' : ''
                }`} />
                <AlertDescription className="font-semibold">
                  {isTimeCritical 
                    ? '⚠️ CRITICAL: Less than 1 minute remaining! Submit your quiz now!' 
                    : '⏰ Time is running low! You have less than 5 minutes remaining.'
                  }
                </AlertDescription>
              </Alert>
            )}
            
            <div className="mb-6">
              <p className="text-gray-700 mb-4">{currentQuestion.QuestionText}</p>
              
              <RadioGroup
                value={currentAnswer?.OptionID?.toString() || ''}
                onValueChange={(value) => 
                  handleAnswerSelect(currentQuestion.QuestionID, parseInt(value))
                }
              >
                {currentQuestion.options.map((option: any) => (
                  <div key={option.OptionID} className="flex items-center space-x-2 mb-3">
                    <RadioGroupItem value={option.OptionID.toString()} id={`option-${option.OptionID}`} />
                    <Label htmlFor={`option-${option.OptionID}`} className="text-sm cursor-pointer">
                      {option.OptionText}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>
          </CardContent>
        </Card>

        {/* Navigation and Submit */}
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={goToPrevious}
              disabled={quizState.currentQuestionIndex === 0}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            
            <Button
              variant="outline"
              onClick={goToNext}
              disabled={quizState.currentQuestionIndex === quizData.questions.length - 1}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => router.push('/dashboard/learning')}
            >
              Exit Quiz
            </Button>
            
            <Button
              onClick={handleManualSubmit}
              disabled={isSubmitting || quizState.isSubmitted}
              className="bg-green-600 hover:bg-green-700"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Submit Quiz
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Answer Summary */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">Answer Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-5 gap-2">
              {quizData.questions.map((question: any, index: number) => {
                const answer = getCurrentAnswer(question.QuestionID)
                const isAnswered = !!answer
                const isCurrent = index === quizState.currentQuestionIndex
                
                return (
                  <Button
                    key={question.QuestionID}
                    variant={isCurrent ? "default" : isAnswered ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setQuizState(prev => ({ ...prev, currentQuestionIndex: index }))}
                    className="h-8"
                  >
                    {index + 1}
                  </Button>
                )
              })}
            </div>
            <div className="mt-4 text-sm text-gray-600">
              Answered: {quizState.answers.length} / {quizData.questions.length}
            </div>
          </CardContent>
        </Card>

        {/* Completion Message */}
        {quizState.isSubmitted && (
          <Alert className="mt-6">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              Quiz submitted successfully! Redirecting to learning dashboard...
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  )
}