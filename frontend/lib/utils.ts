import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPasswordChangeDate(dateString?: string): string {
  if (!dateString) return "Never"
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return "Today"
    if (diffDays === 1) return "Yesterday"
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
    return `${Math.floor(diffDays / 365)} years ago`
  } catch {
    return "Unknown"
  }
}

// Employee profile data formatting utilities
export function formatFullName(firstName?: string, middleName?: string, lastName?: string): string {
  const parts = [firstName, middleName, lastName].filter(Boolean)
  return parts.length > 0 ? parts.join(" ") : "Not provided"
}

export function formatAddress(
  address1?: string,
  address2?: string,
  city?: string,
  state?: string,
  country?: string,
  postalCode?: string
): string {
  const parts = [address1, address2, city, state, postalCode, country].filter(Boolean)
  return parts.length > 0 ? parts.join(", ") : "Not provided"
}

export function formatPhoneNumber(phone?: string): string {
  if (!phone) return "Not provided"
  
  // Remove all non-digit characters
  const cleaned = phone.replace(/\D/g, "")
  
  // Format based on length
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  } else if (cleaned.length === 11 && cleaned.startsWith("1")) {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`
  }
  
  return phone
}

export function formatDate(dateString?: string | Date): string {
  if (!dateString) return "Not provided"
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    })
  } catch {
    return "Invalid date"
  }
}

export function formatEmploymentDuration(years?: number): string {
  if (!years || years === 0) return "Less than 1 year"
  if (years === 1) return "1 year"
  return `${years} years`
}

export function formatGender(genderCode?: string, genderName?: string): string {
  if (genderName) return genderName
  if (genderCode === "M") return "Male"
  if (genderCode === "F") return "Female"
  return "Not specified"
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

export function calculateAge(dateOfBirth?: string | Date): number | null {
  if (!dateOfBirth) return null
  
  try {
    const birthDate = new Date(dateOfBirth)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    
    return age
  } catch {
    return null
  }
}

// Utility function to get current user's employee ID
export function getCurrentEmployeeId(): number | null {
  if (typeof window === 'undefined') return null;
  
  const employeeId = localStorage.getItem('employeeId');
  return employeeId ? parseInt(employeeId, 10) : null;
}

// Utility function to get current user info
export function getCurrentUserInfo() {
  if (typeof window === 'undefined') return null;
  
  return {
    email: localStorage.getItem('userEmail'),
    name: localStorage.getItem('userName'),
    type: localStorage.getItem('userType'),
    employeeId: getCurrentEmployeeId(),
  };
}
