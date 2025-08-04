"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { 
  Upload, 
  Camera, 
  X, 
  Check, 
  AlertCircle,
  User,
  Trash2
} from "lucide-react"
import { apiPost, apiGet, apiDelete } from "@/lib/api"
import { getInitials } from "@/lib/utils"

interface ProfilePictureUploadProps {
  employeeId: number
  uploadedById: number
  currentPictureUrl?: string
  employeeName: string
  onPictureUpdate?: (pictureUrl: string) => void
}

interface ProfilePictureResponse {
  PictureID: number
  EmployeeID: number
  UploadedByID: number
  UploadedAt: string
  FileName: string
  FilePath: string
  FileSize: number
  MimeType: string
}

interface ProfilePictureUploadResponse {
  success: boolean
  blob_name: string
  blob_url: string
  file_size: number
  content_type: string
  metadata: Record<string, any>
  picture_id: number | null
}

interface ProfilePictureDeleteResponse {
  success: boolean
  message: string
  blob_name: string
  picture_id: number | null
}

export default function ProfilePictureUpload({
  employeeId,
  uploadedById,
  currentPictureUrl,
  employeeName,
  onPictureUpdate
}: ProfilePictureUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [currentPictureId, setCurrentPictureId] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch current picture ID when component mounts or currentPictureUrl changes
  useEffect(() => {
    const fetchCurrentPictureId = async () => {
      if (currentPictureUrl && employeeId) {
        try {
          const response = await apiGet<ProfilePictureResponse>(`/api/profile/${employeeId}/latest`)
          if (response && response.PictureID) {
            setCurrentPictureId(response.PictureID)
          }
        } catch (error) {
          console.error('Failed to fetch current picture ID:', error)
        }
      } else {
        setCurrentPictureId(null)
      }
    }

    fetchCurrentPictureId()
  }, [currentPictureUrl, employeeId])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError("Please select a valid image file (JPEG, PNG, GIF, or WebP)")
      return
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      setError("File size must be less than 5MB")
      return
    }

    setSelectedFile(file)
    setError(null)
    setSuccess(null)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)
    setError(null)
    setSuccess(null)

    try {
      // Create FormData
      const formData = new FormData()
      formData.append('file', selectedFile)

      // Upload profile picture
      const response: ProfilePictureUploadResponse = await apiPost(
        `/profile/upload/${employeeId}?uploaded_by_id=${uploadedById}`,
        formData
      )

      if (response.success) {
        setSuccess("Profile picture uploaded successfully!")
        setPreviewUrl(null)
        setSelectedFile(null)
        
        // Call the callback with the new picture URL
        if (onPictureUpdate) {
          onPictureUpdate(response.blob_url)
        }

        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
      } else {
        setError("Failed to upload profile picture")
      }
    } catch (error: any) {
      console.error("Upload error:", error)
      setError(error.message || "Failed to upload profile picture")
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const handleCancel = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setError(null)
    setSuccess(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleDelete = async () => {
    if (!currentPictureId) {
      setError("No profile picture to delete")
      return
    }

    setIsDeleting(true)
    setError(null)
    setSuccess(null)

    try {
      const response: ProfilePictureDeleteResponse = await apiDelete(
        `/api/profile/picture/${currentPictureId}`
      )

      if (response.success) {
        setSuccess("Profile picture deleted successfully!")
        setCurrentPictureId(null)
        
        // Call the callback to update the parent component
        if (onPictureUpdate) {
          onPictureUpdate("") // Pass empty string to indicate no picture
        }
      } else {
        setError("Failed to delete profile picture")
      }
    } catch (error: any) {
      console.error("Delete error:", error)
      setError(error.message || "Failed to delete profile picture")
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="w-5 h-5" />
          Profile Picture
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Profile Picture */}
        <div className="flex flex-col items-center space-y-4">
          <Avatar className="w-24 h-24 ring-4 ring-orange-200">
            {currentPictureUrl ? (
              <AvatarImage src={currentPictureUrl} alt={employeeName} />
            ) : null}
            <AvatarFallback className="bg-gradient-to-r from-orange-500 to-amber-500 text-white text-2xl font-bold">
              {getInitials(employeeName)}
            </AvatarFallback>
          </Avatar>
          
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {currentPictureUrl ? "Current profile picture" : "No profile picture set"}
            </p>
          </div>
        </div>

        <Separator />

        {/* Upload Section */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="profile-picture" className="text-sm font-medium">
              Upload New Picture
            </Label>
            <div className="mt-2">
              <Input
                id="profile-picture"
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleFileSelect}
                className="cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-1">
                Supported formats: JPEG, PNG, GIF, WebP (max 5MB)
              </p>
            </div>
          </div>

          {/* File Preview */}
          {previewUrl && (
            <div className="space-y-2">
              <Label className="text-sm font-medium">Preview</Label>
              <div className="flex items-center space-x-4">
                <Avatar className="w-16 h-16">
                  <AvatarImage src={previewUrl} alt="Preview" />
                  <AvatarFallback className="bg-gray-200">
                    <User className="w-6 h-6" />
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <p className="text-sm font-medium">
                    {selectedFile?.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile?.size || 0 / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Upload Progress */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center space-x-2 text-red-600 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="flex items-center space-x-2 text-green-600 text-sm">
              <Check className="w-4 h-4" />
              <span>{success}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            {selectedFile && (
              <>
                <Button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="flex-1"
                >
                  {isUploading ? (
                    <>
                      <Upload className="w-4 h-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleCancel}
                  variant="outline"
                  disabled={isUploading}
                >
                  <X className="w-4 h-4" />
                </Button>
              </>
            )}
          </div>

          {/* Delete Button */}
          {currentPictureUrl && !selectedFile && (
            <Button
              onClick={handleDelete}
              variant="destructive"
              size="sm"
              className="w-full"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Trash2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Remove Picture
                </>
              )}
            </Button>
          )}
        </div>

        {/* File Requirements */}
        <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
          <h4 className="text-sm font-medium mb-2">Requirements</h4>
          <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <li>• Maximum file size: 5MB</li>
            <li>• Supported formats: JPEG, PNG, GIF, WebP</li>
            <li>• Recommended dimensions: 400x400 pixels</li>
            <li>• Square aspect ratio works best</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
} 