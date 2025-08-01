import type React from "react"
;('"use client')

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Star } from "lucide-react"

export default function FeedbackForm() {
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    console.log({ rating, comment })

    // Reset form
    setRating(0)
    setComment("")
    setIsSubmitting(false)
  }

  return (
    <div className="space-y-8">
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Feedback Form</CardTitle>
          <CardDescription>Share your thoughts and help us improve</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="rating">Rating</Label>
              <div className="flex items-center mt-2">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    type="button"
                    className={`text-3xl ${value <= rating ? "text-yellow-500" : "text-gray-300"}`}
                    onClick={() => setRating(value)}
                  >
                    <Star />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="comment">Comment</Label>
              <Textarea
                id="comment"
                placeholder="Share your feedback..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={4}
                className="resize-none"
              />
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit Feedback"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
