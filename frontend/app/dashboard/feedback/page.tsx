"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { AlertCircle, MessageSquare, Eye, Heart, Plus } from "lucide-react"
import FeedbackForm from "@/components/features/feedback-form"
import WomenFeedbackForm from "@/components/features/women-feedback-form"
import FeedbackViewer from "@/components/features/feedback-viewer"
import useUserInfo from "@/hooks/use-user-info"

export default function FeedbackPage() {
  const { userInfo, loading, error, isFemale, isManager, isHR } = useUserInfo()
  const [activeTab, setActiveTab] = useState("submit")
  const [showWomenForm, setShowWomenForm] = useState(false)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  // Debug: Log user info to see what's happening
  console.log("User Info:", { userInfo, isFemale, isManager, isHR })

  // Determine if user can view feedback (managers and HR)
  const canViewFeedback = isManager || isHR

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <MessageSquare className="h-6 w-6 text-blue-500" />
        <h1 className="text-2xl font-bold">Feedback</h1>
      </div>

      {canViewFeedback ? (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="submit" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Submit Feedback
            </TabsTrigger>
            <TabsTrigger value="view" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              View Feedback
            </TabsTrigger>
          </TabsList>

          <TabsContent value="submit" className="space-y-6">
            {/* Women-specific feedback form - only show button for women */}
            {isFemale && (
              <Card className="border-l-4 border-l-pink-500">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Heart className="h-5 w-5 text-pink-500" />
                      <CardTitle>Women's Feedback</CardTitle>
                    </div>
                    {!showWomenForm && (
                      <Button 
                        onClick={() => setShowWomenForm(true)}
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-2"
                      >
                        <Plus className="h-4 w-4" />
                        Open Women's Form
                      </Button>
                    )}
                  </div>
                  <CardDescription>
                    Special feedback form for women employees with categories like safe workplace, equal employment, and maternity benefits.
                  </CardDescription>
                </CardHeader>
                {showWomenForm && (
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-end">
                        <Button 
                          onClick={() => setShowWomenForm(false)}
                          variant="ghost"
                          size="sm"
                        >
                          Close Form
                        </Button>
                      </div>
                      <WomenFeedbackForm />
                    </div>
                  </CardContent>
                )}
              </Card>
            )}

            {/* General feedback form */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-blue-500" />
                  <CardTitle>General Feedback</CardTitle>
                </div>
                <CardDescription>
                  Submit general feedback about work environment, team collaboration, management, and more.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FeedbackForm />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="view">
            <FeedbackViewer />
          </TabsContent>
        </Tabs>
      ) : (
        // Regular employees can only submit feedback
        <div className="space-y-6">
          {/* Women-specific feedback form - only show button for women */}
          {isFemale && (
            <Card className="border-l-4 border-l-pink-500">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-pink-500" />
                    <CardTitle>Women's Feedback</CardTitle>
                  </div>
                  {!showWomenForm && (
                    <Button 
                      onClick={() => setShowWomenForm(true)}
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      Open Women's Form
                    </Button>
                  )}
                </div>
                <CardDescription>
                  Special feedback form for women employees with categories like safe workplace, equal employment, and maternity benefits.
                </CardDescription>
              </CardHeader>
              {showWomenForm && (
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-end">
                      <Button 
                        onClick={() => setShowWomenForm(false)}
                        variant="ghost"
                        size="sm"
                      >
                        Close Form
                      </Button>
                    </div>
                    <WomenFeedbackForm />
                  </div>
                </CardContent>
              )}
            </Card>
          )}

          {/* General feedback form */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-500" />
                <CardTitle>General Feedback</CardTitle>
              </div>
              <CardDescription>
                Submit general feedback about work environment, team collaboration, management, and more.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FeedbackForm />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
} 