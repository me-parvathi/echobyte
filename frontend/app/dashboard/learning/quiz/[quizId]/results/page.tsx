"use client"

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useLearning } from '@/hooks/use-learning'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, XCircle, ArrowLeft, Trophy, Clock, AlertTriangle } from 'lucide-react'

interface QuizResult {
  question_id: number
  question_text: string
  explanation: string
  user_answer: {
    option_id: number
    option_text: string
    is_correct: boolean
  }
  correct_answer: {
    option_id: number
    option_text: string
  }
}

interface QuizResultsData {
  attempt_id: number
  quiz_id: number
  quiz_title: string
  score_percentage: number
  is_passed: boolean
  passing_percentage: number
  total_questions: number
  correct_answers: number
  started_at: string
  completed_at: string
  results: QuizResult[]
}

export default function QuizResultsPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const quizId = parseInt(params.quizId as string)
  const attemptId = parseInt(searchParams.get('attemptId') || '0')
  
  const { getQuizResults, loading, error } = useLearning()
  
  const [resultsData, setResultsData] = useState<QuizResultsData | null>(null)
  const hasLoaded = useRef(false) // Prevent multiple loads

  useEffect(() => {
    // Prevent multiple loads
    if (hasLoaded.current || !attemptId) return
    
    const loadResults = async () => {
      if (!attemptId) {
        toast.error('No attempt ID provided')
        router.push('/dashboard/learning')
        return
      }

      try {
        hasLoaded.current = true
        const results = await getQuizResults(attemptId) as QuizResultsData
        setResultsData(results)
      } catch (err) {
        console.error('Failed to load quiz results:', err)
        toast.error('Failed to load quiz results')
        router.push('/dashboard/learning')
      }
    }

    loadResults()
  }, [attemptId]) // Only depend on attemptId to prevent infinite loops

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getScoreColor = (score: number, passingScore: number) => {
    if (score >= passingScore) return 'text-green-600'
    return 'text-red-600'
  }

  const getScoreIcon = (score: number, passingScore: number) => {
    if (score >= passingScore) return <Trophy className="w-5 h-5 text-green-600" />
    return <AlertTriangle className="w-5 h-5 text-red-600" />
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg">Loading results...</p>
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

  if (!resultsData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Alert className="max-w-md">
          <XCircle className="h-4 w-4" />
          <AlertDescription>No results found</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard/learning')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Learning
          </Button>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl text-center">
                Quiz Results: {resultsData.quiz_title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {/* Score */}
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    {getScoreIcon(resultsData.score_percentage, resultsData.passing_percentage)}
                  </div>
                  <h3 className="text-lg font-semibold mb-1">Score</h3>
                  <p className={`text-3xl font-bold ${getScoreColor(resultsData.score_percentage, resultsData.passing_percentage)}`}>
                    {resultsData.score_percentage.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">
                    {resultsData.correct_answers} of {resultsData.total_questions} correct
                  </p>
                </div>

                {/* Pass/Fail Status */}
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    {resultsData.is_passed ? (
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    ) : (
                      <XCircle className="w-8 h-8 text-red-600" />
                    )}
                  </div>
                  <h3 className="text-lg font-semibold mb-1">Status</h3>
                  <Badge variant={resultsData.is_passed ? "default" : "destructive"} className="text-lg">
                    {resultsData.is_passed ? 'PASSED' : 'FAILED'}
                  </Badge>
                  <p className="text-sm text-gray-600 mt-1">
                    Passing: {resultsData.passing_percentage}%
                  </p>
                </div>

                {/* Time */}
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Clock className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold mb-1">Completed</h3>
                  <p className="text-sm text-gray-600">
                    {formatDate(resultsData.completed_at)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Results */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Question Results</h2>
          
          {resultsData.results.map((result, index) => (
            <Card key={result.question_id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">
                    Question {index + 1}
                  </h3>
                  <Badge variant={result.user_answer.is_correct ? "default" : "destructive"}>
                    {result.user_answer.is_correct ? 'Correct' : 'Incorrect'}
                  </Badge>
                </div>
                <p className="text-gray-700">{result.question_text}</p>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* User's Answer */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Your Answer:</h4>
                  <div className={`p-3 rounded-lg border ${
                    result.user_answer.is_correct 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-red-50 border-red-200'
                  }`}>
                    <div className="flex items-center">
                      {result.user_answer.is_correct ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mr-2" />
                      )}
                      <span className="text-gray-700">{result.user_answer.option_text}</span>
                    </div>
                  </div>
                </div>

                {/* Correct Answer (if user was wrong) */}
                {!result.user_answer.is_correct && result.correct_answer && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Correct Answer:</h4>
                    <div className="p-3 rounded-lg border bg-green-50 border-green-200">
                      <div className="flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        <span className="text-gray-700">{result.correct_answer.option_text}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Explanation */}
                {result.explanation && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Explanation:</h4>
                    <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                      <p className="text-gray-700">{result.explanation}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-center space-x-4">
          <Button
            onClick={() => router.push('/dashboard/learning')}
            variant="outline"
          >
            Back to Learning
          </Button>
          
          {!resultsData.is_passed && (
            <Button
              onClick={() => router.push(`/dashboard/learning/quiz/${quizId}`)}
              variant="default"
            >
              Try Again
            </Button>
          )}
        </div>
      </div>
    </div>
  )
} 