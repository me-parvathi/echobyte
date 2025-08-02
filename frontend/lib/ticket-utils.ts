import { Ticket, TicketActivity, PendingStatus } from '@/lib/types'

/**
 * Calculate pending status based on last comment time
 * If last comment was more than 36 hours ago, set pending status
 */
export function calculatePendingStatus(ticket: Ticket): PendingStatus {
  if (!ticket.activities || ticket.activities.length === 0) {
    return {
      is_pending_vendor: false,
      is_pending_user: false
    }
  }

  const comments = ticket.activities.filter(activity => activity.ActivityType === 'Comment')
  if (comments.length === 0) {
    return {
      is_pending_vendor: false,
      is_pending_user: false
    }
  }

  const lastComment = comments[comments.length - 1]
  const lastCommentTime = new Date(lastComment.PerformedAt)
  const now = new Date()
  const hoursSinceLastComment = (now.getTime() - lastCommentTime.getTime()) / (1000 * 60 * 60)

  // If last comment was more than 36 hours ago, set pending status
  if (hoursSinceLastComment > 36) {
    return {
      is_pending_vendor: true,
      is_pending_user: true,
      last_comment_time: lastComment.PerformedAt,
      last_comment_by: lastComment.performed_by,
      hours_since_last_comment: Math.floor(hoursSinceLastComment)
    }
  } else {
    return {
      is_pending_vendor: false,
      is_pending_user: false,
      last_comment_time: lastComment.PerformedAt,
      last_comment_by: lastComment.performed_by,
      hours_since_last_comment: Math.floor(hoursSinceLastComment)
    }
  }
}

/**
 * Get allowed status transitions for IT employees
 */
export function getAllowedStatusTransitions(currentStatus: string): string[] {
  const transitions: Record<string, string[]> = {
    'Open': ['In Progress', 'Resolved', 'Closed', 'Escalated', 'Cancelled'],
    'In Progress': ['Resolved', 'Closed', 'Escalated', 'Cancelled'],
    'Resolved': ['Closed', 'In Progress'],
    'Closed': ['In Progress'],
    'Escalated': ['In Progress', 'Resolved', 'Closed'],
    'Cancelled': ['Open']
  }

  return transitions[currentStatus] || []
}

/**
 * Get allowed status transitions for regular employees
 */
export function getAllowedEmployeeStatusTransitions(currentStatus: string): string[] {
  const transitions: Record<string, string[]> = {
    'Open': ['Cancelled'],
    'In Progress': ['Cancelled'],
    'Resolved': [],
    'Closed': [],
    'Escalated': ['Cancelled'],
    'Cancelled': []
  }

  return transitions[currentStatus] || []
}

/**
 * Check if user can update ticket status
 */
export function canUpdateTicketStatus(
  currentStatus: string, 
  newStatus: string, 
  userType: string
): boolean {
  if (userType === 'it') {
    return getAllowedStatusTransitions(currentStatus).includes(newStatus)
  } else {
    return getAllowedEmployeeStatusTransitions(currentStatus).includes(newStatus)
  }
}

/**
 * Check if user can update ticket priority
 */
export function canUpdateTicketPriority(userType: string): boolean {
  return userType === 'it'
}

/**
 * Format ticket number for display
 */
export function formatTicketNumber(ticketNumber: string): string {
  return ticketNumber
}

/**
 * Get ticket age in hours
 */
export function getTicketAge(createdAt: string): number {
  const created = new Date(createdAt)
  const now = new Date()
  return Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60))
}

/**
 * Get ticket age in days
 */
export function getTicketAgeInDays(createdAt: string): number {
  const created = new Date(createdAt)
  const now = new Date()
  return Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24))
}

/**
 * Check if ticket is overdue based on priority SLA
 */
export function isTicketOverdue(ticket: Ticket): boolean {
  if (!ticket.priority) return false
  
  const ticketAge = getTicketAge(ticket.CreatedAt)
  const slaHours = ticket.priority.SLAHours
  
  return ticketAge > slaHours && !['Resolved', 'Closed', 'Cancelled'].includes(ticket.StatusCode)
}

/**
 * Get overdue hours for ticket
 */
export function getOverdueHours(ticket: Ticket): number {
  if (!ticket.priority) return 0
  
  const ticketAge = getTicketAge(ticket.CreatedAt)
  const slaHours = ticket.priority.SLAHours
  
  if (ticketAge > slaHours && !['Resolved', 'Closed', 'Cancelled'].includes(ticket.StatusCode)) {
    return ticketAge - slaHours
  }
  
  return 0
}

/**
 * Get ticket urgency level
 */
export function getTicketUrgency(ticket: Ticket): 'low' | 'medium' | 'high' | 'critical' {
  const overdueHours = getOverdueHours(ticket)
  
  if (overdueHours > 48) return 'critical'
  if (overdueHours > 24) return 'high'
  if (overdueHours > 8) return 'medium'
  
  return 'low'
}

/**
 * Sort tickets by priority and age
 */
export function sortTicketsByPriority(tickets: Ticket[]): Ticket[] {
  return [...tickets].sort((a, b) => {
    // First sort by priority (High > Medium > Low)
    const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 }
    const aPriority = priorityOrder[a.priority?.PriorityName as keyof typeof priorityOrder] || 0
    const bPriority = priorityOrder[b.priority?.PriorityName as keyof typeof priorityOrder] || 0
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority
    }
    
    // Then sort by age (oldest first)
    const aAge = getTicketAge(a.CreatedAt)
    const bAge = getTicketAge(b.CreatedAt)
    
    return bAge - aAge
  })
}

/**
 * Get ticket statistics for dashboard
 */
export function getTicketStats(tickets: Ticket[]) {
  const stats = {
    total: tickets.length,
    open: tickets.filter(t => t.StatusCode === 'Open').length,
    inProgress: tickets.filter(t => t.StatusCode === 'In Progress').length,
    resolved: tickets.filter(t => t.StatusCode === 'Resolved').length,
    closed: tickets.filter(t => t.StatusCode === 'Closed').length,
    escalated: tickets.filter(t => t.StatusCode === 'Escalated').length,
    cancelled: tickets.filter(t => t.StatusCode === 'Cancelled').length,
    overdue: tickets.filter(t => isTicketOverdue(t)).length,
    byPriority: {} as Record<string, number>,
    byCategory: {} as Record<string, number>
  }

  // Count by priority
  tickets.forEach(ticket => {
    const priority = ticket.priority?.PriorityName || 'Unknown'
    stats.byPriority[priority] = (stats.byPriority[priority] || 0) + 1
  })

  // Count by category
  tickets.forEach(ticket => {
    const category = ticket.category?.CategoryName || 'Unknown'
    stats.byCategory[category] = (stats.byCategory[category] || 0) + 1
  })

  return stats
} 