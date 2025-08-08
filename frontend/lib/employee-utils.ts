import { Employee, EmployeeWithDetails, Team, Department } from '@/lib/types';

/**
 * Creates lookup maps for teams and departments
 */
export function createLookupMaps(teams: Team[], departments: Department[]) {
  const teamLookup = new Map(teams.map(team => [team.TeamID, team]));
  const departmentLookup = new Map(departments.map(dept => [dept.DepartmentID, dept]));
  
  return { teamLookup, departmentLookup };
}

/**
 * Transforms backend employee data into frontend format with computed fields
 */
export function transformEmployeeToFrontend(
  employee: Employee, 
  teamLookup?: Map<number, Team>,
  departmentLookup?: Map<number, Department>
): EmployeeWithDetails {
  const fullName = `${employee.FirstName} ${employee.MiddleName ? employee.MiddleName + ' ' : ''}${employee.LastName}`.trim();
  const initials = getInitials(fullName);
  
  // Determine role based on designation or other criteria
  const role = determineRole(employee);
  
  // Determine status based on IsActive and other factors
  const status = employee.IsActive ? 'active' : 'inactive';
  
  // Generate skills based on designation (this could be enhanced with actual skills data)
  const skills = generateSkillsFromDesignation(employee.designation?.DesignationName);
  
  // Get team and department names from lookups
  const team = teamLookup?.get(employee.TeamID);
  const department = team ? departmentLookup?.get(team.DepartmentID) : undefined;
  
  const teamName = team?.TeamName;
  const departmentName = department?.DepartmentName;
  const locationName = employee.location?.LocationName;
  const managerName = employee.manager ? `${employee.manager.FirstName} ${employee.manager.LastName}`.trim() : undefined;
  
  return {
    ...employee,
    fullName,
    displayName: fullName,
    initials,
    role,
    status,
    skills,
    locationName,
    departmentName,
    teamName,
    managerName,
  };
}

/**
 * Gets initials from a full name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

/**
 * Determines the role based on employee designation and other criteria
 */
export function determineRole(employee: Employee): 'employee' | 'manager' | 'hr' | 'it' | 'ceo' | 'cto' {
  const designation = employee.designation?.DesignationName?.toLowerCase() || '';
  
  if (designation.includes('ceo') || designation.includes('chief executive')) {
    return 'ceo';
  }
  
  if (designation.includes('cto') || designation.includes('chief technology')) {
    return 'cto';
  }
  
  if (designation.includes('manager') || designation.includes('lead') || designation.includes('director')) {
    return 'manager';
  }
  
  if (designation.includes('hr') || designation.includes('human resource')) {
    return 'hr';
  }
  
  if (designation.includes('it') || designation.includes('technology') || designation.includes('system')) {
    return 'it';
  }
  
  return 'employee';
}

/**
 * Generates skills based on designation (placeholder implementation)
 */
export function generateSkillsFromDesignation(designation?: string): string[] {
  if (!designation) return [];
  
  const designationLower = designation.toLowerCase();
  
  if (designationLower.includes('engineer') || designationLower.includes('developer')) {
    return ['JavaScript', 'React', 'Node.js', 'TypeScript'];
  }
  
  if (designationLower.includes('manager')) {
    return ['Leadership', 'Project Management', 'Strategy'];
  }
  
  if (designationLower.includes('hr')) {
    return ['Recruitment', 'Employee Relations', 'Policy Development'];
  }
  
  if (designationLower.includes('it') || designationLower.includes('system')) {
    return ['System Administration', 'Network Security', 'Cloud Infrastructure'];
  }
  
  if (designationLower.includes('designer')) {
    return ['UI/UX Design', 'Figma', 'Adobe Creative Suite'];
  }
  
  if (designationLower.includes('qa') || designationLower.includes('test')) {
    return ['Manual Testing', 'Automated Testing', 'Quality Assurance'];
  }
  
  return ['Communication', 'Problem Solving', 'Teamwork'];
}

/**
 * Formats join date for display
 */
export function formatJoinDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Gets role color for UI display
 */
export function getRoleColor(role: string): string {
  switch (role) {
    case 'ceo':
      return 'from-red-500 to-rose-500';
    case 'cto':
      return 'from-indigo-500 to-blue-500';
    case 'manager':
      return 'from-emerald-500 to-teal-500';
    case 'hr':
      return 'from-purple-500 to-pink-500';
    case 'it':
      return 'from-blue-500 to-cyan-500';
    default:
      return 'from-orange-500 to-amber-500';
  }
}

/**
 * Gets status color for UI display
 */
export function getStatusColor(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800';
    case 'away':
      return 'bg-yellow-100 text-yellow-800';
    case 'offline':
      return 'bg-gray-100 text-gray-800';
    case 'inactive':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

/**
 * Gets role icon for UI display
 */
export function getRoleIcon(role: string): string {
  switch (role) {
    case 'manager':
      return '👑';
    case 'hr':
      return '👥';
    case 'it':
      return '🏢';
    case 'ceo':
      return '👑';
    case 'cto':
      return '💻';
    default:
      return '👤';
  }
}

/**
 * Transforms a list of employees to frontend format
 */
export function transformEmployeesToFrontend(
  employees: Employee[], 
  teamLookup?: Map<number, Team>,
  departmentLookup?: Map<number, Department>
): EmployeeWithDetails[] {
  return employees.map(employee => transformEmployeeToFrontend(employee, teamLookup, departmentLookup));
}

/**
 * Filters employees by search term
 */
export function filterEmployeesBySearch(employees: EmployeeWithDetails[], searchTerm: string): EmployeeWithDetails[] {
  if (!searchTerm) return employees;
  
  const lowerSearchTerm = searchTerm.toLowerCase();
  
  return employees.filter((employee) => {
    return (
      employee.fullName.toLowerCase().includes(lowerSearchTerm) ||
      employee.designation?.DesignationName.toLowerCase().includes(lowerSearchTerm) ||
      employee.CompanyEmail.toLowerCase().includes(lowerSearchTerm) ||
      employee.departmentName?.toLowerCase().includes(lowerSearchTerm) ||
      employee.skills?.some(skill => skill.toLowerCase().includes(lowerSearchTerm))
    );
  });
}

/**
 * Filters employees by department
 */
export function filterEmployeesByDepartment(employees: EmployeeWithDetails[], department: string): EmployeeWithDetails[] {
  if (!department || department === 'all') return employees;
  
  return employees.filter((employee) => employee.departmentName === department);
}

/**
 * Filters employees by role
 */
export function filterEmployeesByRole(employees: EmployeeWithDetails[], role: string): EmployeeWithDetails[] {
  if (!role || role === 'all') return employees;
  
  return employees.filter((employee) => employee.role === role);
} 