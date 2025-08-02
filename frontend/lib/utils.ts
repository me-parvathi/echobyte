import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
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
