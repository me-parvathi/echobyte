"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Award, BookOpen, Clock, Star, Trophy, Play, CheckCircle, Lock, Target, TrendingUp } from "lucide-react"

export default function LearningModules() {
  const [selectedTrack, setSelectedTrack] = useState("all")

  const learningTracks = [
    {
      id: "devops",
      title: "DevOps Certification Track",
      description: "Master cloud infrastructure and deployment practices",
      modules: 8,
      completedModules: 3,
      estimatedTime: "40 hours",
      difficulty: "Intermediate",
      badge: "DevOps Engineer",
      color: "bg-blue-600",
      bgColor: "bg-blue-50",
      textColor: "text-blue-600",
    },
    {
      id: "security",
      title: "Cybersecurity Fundamentals",
      description: "Learn essential security practices and compliance",
      modules: 6,
      completedModules: 6,
      estimatedTime: "25 hours",
      difficulty: "Beginner",
      badge: "Security Champion",
      color: "bg-red-600",
      bgColor: "bg-red-50",
      textColor: "text-red-600",
    },
    {
      id: "leadership",
      title: "Leadership Development",
      description: "Build management and team leadership skills",
      modules: 10,
      completedModules: 2,
      estimatedTime: "35 hours",
      difficulty: "Advanced",
      badge: "Team Leader",
      color: "bg-purple-600",
      bgColor: "bg-purple-50",
      textColor: "text-purple-600",
    },
    {
      id: "data",
      title: "Data Analytics Mastery",
      description: "Advanced data analysis and visualization techniques",
      modules: 12,
      completedModules: 0,
      estimatedTime: "50 hours",
      difficulty: "Advanced",
      badge: "Data Analyst",
      color: "bg-green-600",
      bgColor: "bg-green-50",
      textColor: "text-green-600",
    },
  ]

  const azureQuizzes = [
    {
      id: 1,
      title: "Azure Fundamentals - Compute Services",
      questions: 25,
      timeLimit: 45,
      difficulty: "Beginner",
      lastAttempt: "85%",
      attempts: 2,
      maxAttempts: 3,
      status: "passed",
    },
    {
      id: 2,
      title: "Azure Storage Solutions",
      questions: 30,
      timeLimit: 60,
      difficulty: "Intermediate",
      lastAttempt: "72%",
      attempts: 1,
      maxAttempts: 3,
      status: "failed",
    },
    {
      id: 3,
      title: "Azure Networking Concepts",
      questions: 35,
      timeLimit: 75,
      difficulty: "Intermediate",
      lastAttempt: null,
      attempts: 0,
      maxAttempts: 3,
      status: "available",
    },
    {
      id: 4,
      title: "Azure Security & Identity",
      questions: 40,
      timeLimit: 90,
      difficulty: "Advanced",
      lastAttempt: null,
      attempts: 0,
      maxAttempts: 3,
      status: "locked",
    },
  ]

  const earnedBadges = [
    {
      id: 1,
      name: "Security Champion",
      description: "Completed cybersecurity fundamentals",
      earnedDate: "2024-11-15",
      color: "bg-red-600",
    },
    {
      id: 2,
      name: "Azure Fundamentals",
      description: "Passed Azure 104 certification quiz",
      earnedDate: "2024-10-22",
      color: "bg-blue-600",
    },
    {
      id: 3,
      name: "Team Collaborator",
      description: "Completed team building workshop",
      earnedDate: "2024-09-30",
      color: "bg-green-600",
    },
  ]

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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Learning & Development</h2>
        <p className="text-gray-600">Enhance your skills and earn certifications</p>
      </div>

      {/* Learning Stats */}
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
              <p className="text-2xl font-bold text-gray-900">11</p>
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
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">Learning Hours</p>
              <p className="text-2xl font-bold text-gray-900">127</p>
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
              <p className="text-sm font-medium text-gray-600">Skill Rank</p>
              <p className="text-2xl font-bold text-gray-900">#12</p>
              <p className="text-xs text-gray-500">In your department</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Learning Tracks */}
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Learning Tracks</CardTitle>
          <CardDescription>Structured learning paths to build expertise</CardDescription>
        </CardHeader>
        <CardContent>
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

                  <Button className="w-full" variant={track.completedModules > 0 ? "default" : "outline"}>
                    {track.completedModules === track.modules ? (
                      <>
                        <Trophy className="w-4 h-4 mr-2" />
                        Completed
                      </>
                    ) : track.completedModules > 0 ? (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Continue Learning
                      </>
                    ) : (
                      <>
                        <BookOpen className="w-4 h-4 mr-2" />
                        Start Track
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Azure Certification Quizzes */}
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Azure 104 Certification Quizzes</CardTitle>
          <CardDescription>Randomized, time-bound quizzes for DevOps compliance</CardDescription>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>

      {/* Earned Badges */}
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Your Achievements</CardTitle>
          <CardDescription>Badges and certifications you've earned</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {earnedBadges.map((badge) => (
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
        </CardContent>
      </Card>
    </div>
  )
}
