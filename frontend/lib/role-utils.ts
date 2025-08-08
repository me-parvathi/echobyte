import { api } from './api'

export interface RoleInfo {
  RoleID: number
  RoleName: string
  Description?: string
  IsActive: boolean
}

export interface EmployeeRoleWithDetails {
  AssignmentID: number
  EmployeeID: number
  RoleID: number
  RoleName: string
  Description?: string
  IsActive: boolean
  AssignedBy?: number
  AssignedAt?: string
}

/**
 * Fetches user roles from the backend and maps them to frontend user types
 */
export async function fetchUserRoles(): Promise<{ roles: EmployeeRoleWithDetails[], userType: string }> {
  try {
    console.log("🔄 Fetching user roles from API...")
    const roles = await api.get<EmployeeRoleWithDetails[]>("/api/auth/employee-roles/current")
    console.log("✅ User roles fetched:", roles)

    // Map roles to user types (Manager has higher priority than IT Support)
    let userType = "employee" // default

    // Check for HR role (highest priority)
    const hasHRRole = roles.some(role => role.RoleName === "HR Manager" && role.IsActive)
    if (hasHRRole) {
      userType = "hr"
    }

    // Check for Manager role (higher priority than IT)
    const hasManagerRole = roles.some(role => role.RoleName === "Manager" && role.IsActive)
    if (hasManagerRole) {
      userType = "manager"
    }

    // Check for IT Support role (only if not manager or HR)
    const hasITRole = roles.some(role => role.RoleName === "IT Support" && role.IsActive)
    if (hasITRole && userType === "employee") {
      userType = "it"
    }

    console.log("🎭 Mapped user type:", userType, "from roles:", roles.map(r => r.RoleName))
    
    return { roles, userType }
  } catch (error) {
    console.error("❌ Failed to fetch user roles:", error)
    // Return default employee type if role fetching fails
    return { roles: [], userType: "employee" }
  }
}

/**
 * Determines user type from roles array
 */
export function determineUserType(roles: EmployeeRoleWithDetails[]): string {
  // Check for HR role (highest priority)
  if (roles.some(role => role.RoleName === "HR Manager" && role.IsActive)) {
    return "hr"
  }

  // Check for Manager role (higher priority than IT)
  if (roles.some(role => role.RoleName === "Manager" && role.IsActive)) {
    return "manager"
  }

  // Check for IT Support role
  if (roles.some(role => role.RoleName === "IT Support" && role.IsActive)) {
    return "it"
  }

  // Default to employee
  return "employee"
} 