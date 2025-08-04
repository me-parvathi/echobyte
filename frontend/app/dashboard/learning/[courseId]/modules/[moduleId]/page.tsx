"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, Play, CheckCircle, Clock, BookOpen, Video } from "lucide-react"
import { useLearning, type Course, type CourseModule, type ModuleProgress } from "@/hooks/use-learning"
import { useToast } from "@/hooks/use-toast"

// Video Player Component
const VideoPlayer = ({ url }: { url: string }) => {
  const getVideoEmbedUrl = (url: string) => {
    // YouTube video
    const youtubeRegex = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/
    const youtubeMatch = url.match(youtubeRegex)
    if (youtubeMatch) {
      return `https://www.youtube.com/embed/${youtubeMatch[1]}`
    }

    // Vimeo video
    const vimeoRegex = /vimeo\.com\/([0-9]+)/
    const vimeoMatch = url.match(vimeoRegex)
    if (vimeoMatch) {
      return `https://player.vimeo.com/video/${vimeoMatch[1]}`
    }

    // Direct video file (mp4, webm, etc.)
    const videoFileRegex = /\.(mp4|webm|ogg|mov|avi)$/i
    if (videoFileRegex.test(url)) {
      return url
    }

    // If no match, return the original URL
    return url
  }

  const embedUrl = getVideoEmbedUrl(url)
  const isDirectVideo = embedUrl === url && /\.(mp4|webm|ogg|mov|avi)$/i.test(url)

  if (isDirectVideo) {
    return (
      <video 
        controls 
        className="w-full h-full object-cover"
        preload="metadata"
      >
        <source src={url} type="video/mp4" />
        <source src={url} type="video/webm" />
        Your browser does not support the video tag.
      </video>
    )
  }

  return (
    <iframe
      src={embedUrl}
      className="w-full h-full"
      frameBorder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      title="Video content"
    />
  )
}

export default function ModuleDetailPage() {
  const params = useParams()
  const router = useRouter()
  const courseId = parseInt(params.courseId as string)
  const moduleId = parseInt(params.moduleId as string)
  
  const [course, setCourse] = useState<Course | null>(null)
  const [module, setModule] = useState<CourseModule | null>(null)
  const [moduleProgress, setModuleProgress] = useState<ModuleProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [completing, setCompleting] = useState(false)
  
  const { getCourses, getModuleProgress, markModuleCompleted } = useLearning()
  const { toast } = useToast()

  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        setLoading(true)
        
        // Fetch course and module progress data
        const [coursesData, moduleProgressData] = await Promise.all([
          getCourses({ is_active: true }),
          getModuleProgress(courseId)
        ])

        const courses = (coursesData as any)?.courses || []
        const moduleProgress = (moduleProgressData as any) || []
        
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
        
        // Find the specific module
        const foundModule = foundCourse.modules?.find((m: CourseModule) => m.ModuleID === moduleId)
        if (!foundModule) {
          toast({
            title: "Error",
            description: "Module not found",
            variant: "destructive"
          })
          router.push(`/dashboard/learning/${courseId}`)
          return
        }
        
        setModule(foundModule)
        
        // Find module progress
        const foundProgress = moduleProgress.find((p: ModuleProgress) => p.ModuleID === moduleId)
        setModuleProgress(foundProgress || null)
        
      } catch (error) {
        console.error('Failed to fetch module data:', error)
        toast({
          title: "Error",
          description: "Failed to load module data",
          variant: "destructive"
        })
      } finally {
        setLoading(false)
      }
    }

    if (courseId && moduleId) {
      fetchModuleData()
    }
  }, [courseId, moduleId])

  const handleMarkComplete = async () => {
    if (!module) return
    
    try {
      setCompleting(true)
      
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
      
      await markModuleCompleted(module.ModuleID, estimatedTimeMinutes)
      
      // Refresh module progress
      const moduleProgressData = await getModuleProgress(courseId)
      const moduleProgress = (moduleProgressData as any) || []
      const foundProgress = moduleProgress.find((p: ModuleProgress) => p.ModuleID === moduleId)
      setModuleProgress(foundProgress || null)
      
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
      setCompleting(false)
    }
  }

  const isCompleted = moduleProgress !== null

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

  if (!course || !module) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Module Not Found</h1>
          <Button onClick={() => router.push(`/dashboard/learning/${courseId}`)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Course
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
          onClick={() => router.push(`/dashboard/learning/${courseId}`)}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Course
        </Button>
        
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm text-gray-500">Course:</span>
          <span className="text-sm font-medium text-gray-700">{course.Title}</span>
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900">{module.Title}</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Main module content */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="h-5 w-5" />
                Module Content
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Video/Content Section */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Play className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Learning Content</span>
                </div>
                
                {module.VideoType === 'I' ? (
                  <div className="aspect-video bg-gray-200 rounded-lg overflow-hidden">
                    <VideoPlayer url={module.VideoURL} />
                  </div>
                ) : (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <BookOpen className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-700">External Content</span>
                    </div>
                    <p className="text-sm text-blue-600 mb-3">
                      This module contains external learning content.
                    </p>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => window.open(module.VideoURL, '_blank')}
                    >
                      Open Content
                    </Button>
                  </div>
                )}
              </div>

              {/* Module Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Module Sequence:</span>
                  <span className="font-medium">{module.ModuleSeq}</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">Status:</span>
                  <Badge variant={isCompleted ? "default" : "secondary"}>
                    {isCompleted ? "Completed" : "In Progress"}
                  </Badge>
                </div>
              </div>

              {isCompleted && moduleProgress && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700">Completed</span>
                  </div>
                  <p className="text-sm text-green-600">
                    Completed on {new Date(moduleProgress.CompletedAt).toLocaleDateString()}
                    {moduleProgress.TimeSpentMinutes && (
                      <span className="ml-2">
                        • Time spent: {moduleProgress.TimeSpentMinutes} minutes
                      </span>
                    )}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Module actions */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Module Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!isCompleted ? (
                <div className="space-y-3">
                  <p className="text-sm text-gray-600">
                    Complete this module to continue your learning journey.
                  </p>
                  
                  <Button 
                    onClick={handleMarkComplete}
                    disabled={completing}
                    className="w-full"
                  >
                    {completing ? "Completing..." : "Mark as Complete"}
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-gray-600">
                    You have successfully completed this module.
                  </p>
                  
                  <Button 
                    variant="outline"
                    className="w-full"
                    onClick={() => router.push(`/dashboard/learning/${courseId}`)}
                  >
                    Back to Course
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
} 