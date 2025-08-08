import { useState, useEffect } from 'react'
import { getLatestProfilePicture } from '@/lib/api'

interface ProfilePicture {
  FilePath: string
  FileName: string
  FileSize: number
  MimeType: string
}

export function useProfilePicture(employeeId: number) {
  const [pictureUrl, setPictureUrl] = useState<string | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProfilePicture = async () => {
    if (!employeeId) {
      console.log('No employee ID provided for profile picture fetch')
      return
    }

    console.log('Fetching profile picture for employee ID:', employeeId)
    setIsLoading(true)
    setError(null)

    try {
      const picture = await getLatestProfilePicture(employeeId)
      console.log('Profile picture response:', picture)

      if (picture && picture.FilePath) {
        // Use the backend proxy endpoint instead of direct Azure URL
        const proxyUrl = `/api/profile/serve-latest/${employeeId}`
        console.log('Setting picture URL (proxy):', proxyUrl)
        setPictureUrl(proxyUrl)
      } else {
        console.log('No picture found or no FilePath')
        setPictureUrl(undefined)
      }
    } catch (err: any) {
      if (err && err.status === 404) {
        // No photo uploaded – silently fall back to default avatar
        setPictureUrl(undefined)
        return; // Skip error handling/logging for expected 404
      }
      console.error('Failed to fetch profile picture:', err)
      setError(err.message || 'Failed to load profile picture')
      setPictureUrl(undefined)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProfilePicture()
  }, [employeeId])

  const updatePictureUrl = (newUrl: string) => {
    setPictureUrl(newUrl)
    setError(null)
  }

  return {
    pictureUrl,
    isLoading,
    error,
    refetch: fetchProfilePicture,
    updatePictureUrl
  }
} 