"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Pagination } from "@/components/ui/pagination"
import { 
  TicketIcon, 
  Search, 
  Filter, 
  RefreshCw, 
  MessageSquare, 
  Edit, 
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  Play,
  AlertTriangle,
  User,
  Calendar,
  Tag
} from "lucide-react"
import { useTickets, useTicketLookups, useTicketStatistics } from "@/hooks/use-tickets"
import useUserInfo from "@/hooks/use-user-info"
import { TicketStatusBadge } from "@/components/ui/ticket-status-badge"
import { TicketPriorityBadge } from "@/components/ui/ticket-priority-badge"
import { TicketComment } from "@/components/ui/ticket-comment"
import { TicketUpdate, TicketActivityCreate } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"

export function ITTicketsManager() {
  const { userInfo } = useUserInfo()
  const { toast } = useToast()
  
  // State for filters and search
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [priorityFilter, setPriorityFilter] = useState<string>("all")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  
  // Filter change handlers
  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value)
    // Refetch tickets with new filter
    setTimeout(() => refetchTickets(), 100)
  }

  const handlePriorityFilterChange = (value: string) => {
    setPriorityFilter(value)
    // Refetch tickets with new filter
    setTimeout(() => refetchTickets(), 100)
  }

  const handleCategoryFilterChange = (value: string) => {
    setCategoryFilter(value)
    // Refetch tickets with new filter
    setTimeout(() => refetchTickets(), 100)
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    // For search, we can filter client-side since it's just text search
  }
  
  // State for selected ticket and dialog
  const [selectedTicket, setSelectedTicket] = useState<any>(null)
  const [isTicketDialogOpen, setIsTicketDialogOpen] = useState(false)
  const [newComment, setNewComment] = useState("")
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  
  // State for ticket updates
  const [isUpdatingTicket, setIsUpdatingTicket] = useState(false)
  const [updateData, setUpdateData] = useState<TicketUpdate>({})

  // Hooks for data fetching with pagination
  const { 
    tickets, 
    loading: ticketsLoading, 
    error: ticketsError, 
    updateTicket, 
    addComment,
    refetch: refetchTickets,
    currentPage,
    pageSize,
    totalCount,
    hasNext,
    hasPrevious,
    goToPage
  } = useTickets({
    immediate: true, // Explicitly enable immediate fetch
    pageSize: 10, // Smaller page size for better performance
    filters: {
      status_code: statusFilter === "all" ? undefined : statusFilter,
      priority_code: priorityFilter === "all" ? undefined : priorityFilter,
      category_id: categoryFilter === "all" ? undefined : parseInt(categoryFilter)
    },
    onSuccess: (data) => {
      console.log('Tickets loaded successfully:', data);
    },
    onError: (error) => {
      console.error('Error loading tickets:', error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      })
    }
  })

  const { 
    categories, 
    priorities, 
    statuses,
    loading: lookupsLoading 
  } = useTicketLookups()

  const { 
    statistics, 
    loading: statsLoading 
  } = useTicketStatistics()

  // Debug logging
  console.log('ITTicketsManager render:', {
    ticketsLoading,
    ticketsError,
    ticketsCount: tickets?.length || 0,
    totalCount,
    currentPage,
    pageSize,
    statusesCount: statuses?.length || 0,
    lookupsLoading,
    statistics: statistics,
    statsLoading
  });

  // Memoized filtered tickets to prevent unnecessary re-renders
  const filteredTickets = useMemo(() => {
    return tickets.filter(ticket => {
      const matchesSearch = searchTerm === "" || 
        ticket.Subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.Description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.TicketNumber.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = statusFilter === "all" || ticket.StatusCode === statusFilter
      const matchesPriority = priorityFilter === "all" || ticket.PriorityCode === priorityFilter
      const matchesCategory = categoryFilter === "all" || ticket.CategoryID.toString() === categoryFilter

      return matchesSearch && matchesStatus && matchesPriority && matchesCategory
    })
  }, [tickets, searchTerm, statusFilter, priorityFilter, categoryFilter])

  // Handle ticket status update
  const handleStatusUpdate = async (ticketId: number, newStatusCode: string) => {
    if (!userInfo?.employeeId) return

    setIsUpdatingTicket(true)
    try {
      await updateTicket(ticketId, { StatusCode: newStatusCode })
      toast({
        title: "Success",
        description: "Ticket status updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update ticket status",
        variant: "destructive"
      })
    } finally {
      setIsUpdatingTicket(false)
    }
  }

  // Handle priority update
  const handlePriorityUpdate = async (ticketId: number, newPriorityCode: string) => {
    if (!userInfo?.employeeId) return

    setIsUpdatingTicket(true)
    try {
      await updateTicket(ticketId, { PriorityCode: newPriorityCode })
      toast({
        title: "Success",
        description: "Ticket priority updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update ticket priority",
        variant: "destructive"
      })
    } finally {
      setIsUpdatingTicket(false)
    }
  }

  // Handle comment submission
  const handleAddComment = async () => {
    if (!selectedTicket || !newComment.trim() || !userInfo?.employeeId) return

    const commentText = newComment.trim()
    const employeeId = parseInt(userInfo.employeeId)
    
    // Clear input immediately for better UX
    setNewComment("")
    setIsSubmittingComment(true)
    
    try {
      await addComment(selectedTicket.TicketID, commentText, employeeId)
      
      // Get user name from userInfo
      const userName = userInfo.name || 'Unknown User'
      const [firstName, lastName] = userName.split(' ')
      
      // Refresh the selected ticket to show the new comment immediately
      const updatedTickets = tickets.map(ticket => 
        ticket.TicketID === selectedTicket.TicketID 
          ? { ...ticket, activities: [...(ticket.activities || []), {
              ActivityID: Date.now(), // Temporary ID for immediate display
              TicketID: selectedTicket.TicketID,
              ActivityType: 'Comment',
              ActivityDetails: commentText,
              PerformedAt: new Date().toISOString(),
              performed_by: {
                EmployeeID: employeeId,
                FirstName: firstName || 'Unknown',
                LastName: lastName || 'User'
              }
            }]}
          : ticket
      )
      
      // Update the selected ticket with the new comment
      setSelectedTicket((prev: any) => prev ? {
        ...prev,
        activities: [...(prev.activities || []), {
          ActivityID: Date.now(),
          TicketID: selectedTicket.TicketID,
          ActivityType: 'Comment',
          ActivityDetails: commentText,
          PerformedAt: new Date().toISOString(),
          performed_by: {
            EmployeeID: employeeId,
            FirstName: firstName || 'Unknown',
            LastName: lastName || 'User'
          }
        }]
      } : null)
      
      toast({
        title: "Success",
        description: "Comment added successfully",
      })
    } catch (error) {
      // Restore the comment text if there was an error
      setNewComment(commentText)
      toast({
        title: "Error",
        description: "Failed to add comment",
        variant: "destructive"
      })
    } finally {
      setIsSubmittingComment(false)
    }
  }

  // Open ticket details dialog
  const openTicketDialog = (ticket: any) => {
    setSelectedTicket(ticket)
    setIsTicketDialogOpen(true)
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return "Unknown date"
    }
  }

  // Get status options for IT employees - with fallback to all statuses
  const getStatusOptions = () => {
    const filteredStatuses = statuses.filter(status => 
      ['Open', 'In Progress', 'Resolved', 'Closed', 'Escalated', 'Cancelled'].includes(status.TicketStatusName)
    )
    
    // If filtered statuses are empty, return all statuses as fallback
    if (filteredStatuses.length === 0) {
      console.log('No filtered statuses found, using all statuses:', statuses)
      return statuses
    }
    
    console.log('Filtered statuses:', filteredStatuses)
    return filteredStatuses
  }

  // Calculate total pages
  const totalPages = Math.ceil(totalCount / pageSize)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IT Ticket Management</h1>
          <p className="text-gray-600">Manage and resolve support tickets</p>
        </div>
        <Button 
          onClick={() => refetchTickets()} 
          variant="outline" 
          disabled={ticketsLoading}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${ticketsLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <TicketIcon className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">Total Tickets</p>
                  <p className="text-2xl font-bold">{statistics.total_tickets || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">Open</p>
                  <p className="text-2xl font-bold">{statistics.open_tickets || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Play className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="text-sm text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold">{statistics.in_progress_tickets || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Resolved</p>
                  <p className="text-2xl font-bold">{statistics.resolved_tickets || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Statistics Loading State */}
      {statsLoading && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-6 h-6 animate-spin mr-2" />
              Loading statistics...
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search tickets..."
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Status</Label>
              <Select value={statusFilter} onValueChange={handleStatusFilterChange}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  {statuses.map((status) => (
                    <SelectItem key={status.TicketStatusCode} value={status.TicketStatusCode}>
                      {status.TicketStatusName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Priority</Label>
              <Select value={priorityFilter} onValueChange={handlePriorityFilterChange}>
                <SelectTrigger>
                  <SelectValue placeholder="All priorities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All priorities</SelectItem>
                  {priorities.map((priority) => (
                    <SelectItem key={priority.PriorityCode} value={priority.PriorityCode}>
                      {priority.PriorityName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={categoryFilter} onValueChange={handleCategoryFilterChange}>
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.CategoryID} value={category.CategoryID.toString()}>
                      {category.CategoryName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tickets List */}
      <Card>
        <CardHeader>
          <CardTitle>Tickets ({totalCount} total)</CardTitle>
          <CardDescription>Manage and update ticket status</CardDescription>
        </CardHeader>
        <CardContent>
          {ticketsLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-6 h-6 animate-spin mr-2" />
              Loading tickets...
            </div>
          ) : ticketsError ? (
            <div className="flex items-center justify-center py-8 text-red-600">
              <AlertTriangle className="w-6 h-6 mr-2" />
              Failed to load tickets
            </div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <TicketIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No tickets found</p>
              <p className="text-sm">Try adjusting your filters</p>
              <p className="text-xs text-gray-400 mt-2">
                Debug: Loading={ticketsLoading}, Count={tickets?.length}
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {tickets.map((ticket) => (
                  <div
                    key={ticket.TicketID}
                    className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-4">
                        <TicketIcon className="w-5 h-5 text-gray-400" />
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono text-sm font-medium text-gray-900">{ticket.TicketNumber}</span>
                            <TicketStatusBadge status={ticket.StatusCode} />
                            <TicketPriorityBadge priority={ticket.PriorityCode} />
                          </div>
                          <p className="font-medium text-gray-900 mb-1">{ticket.Subject}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>Created: {formatDate(ticket.CreatedAt)}</span>
                            <span>Updated: {formatDate(ticket.UpdatedAt)}</span>
                            <span>By: {ticket.opened_by?.FirstName} {ticket.opened_by?.LastName}</span>
                            {ticket.assigned_to && (
                              <span>Assignee: {ticket.assigned_to.FirstName} {ticket.assigned_to.LastName}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => openTicketDialog(ticket)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                    
                    {/* Quick Actions */}
                    <div className="flex items-center gap-2 mt-3">
                      <Select 
                        value={ticket.StatusCode} 
                        onValueChange={(value) => handleStatusUpdate(ticket.TicketID, value)}
                        disabled={isUpdatingTicket || lookupsLoading}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue placeholder={lookupsLoading ? "Loading..." : "Select status"} />
                        </SelectTrigger>
                        <SelectContent>
                          {lookupsLoading ? (
                            <SelectItem value="loading" disabled>Loading statuses...</SelectItem>
                          ) : getStatusOptions().length === 0 ? (
                            <SelectItem value="no-statuses" disabled>No statuses available</SelectItem>
                          ) : (
                            getStatusOptions().map((status) => (
                              <SelectItem key={status.TicketStatusCode} value={status.TicketStatusCode}>
                                {status.TicketStatusName}
                              </SelectItem>
                            ))
                          )}
                        </SelectContent>
                      </Select>
                      
                      <Select 
                        value={ticket.PriorityCode} 
                        onValueChange={(value) => handlePriorityUpdate(ticket.TicketID, value)}
                        disabled={isUpdatingTicket || lookupsLoading}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue placeholder={lookupsLoading ? "Loading..." : "Select priority"} />
                        </SelectTrigger>
                        <SelectContent>
                          {lookupsLoading ? (
                            <SelectItem value="loading" disabled>Loading priorities...</SelectItem>
                          ) : priorities.length === 0 ? (
                            <SelectItem value="no-priorities" disabled>No priorities available</SelectItem>
                          ) : (
                            priorities.map((priority) => (
                              <SelectItem key={priority.PriorityCode} value={priority.PriorityCode}>
                                {priority.PriorityName}
                              </SelectItem>
                            ))
                          )}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              <div className="mt-6">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={goToPage}
                  hasNext={hasNext}
                  hasPrevious={hasPrevious}
                  totalCount={totalCount}
                  pageSize={pageSize}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Ticket Details Dialog */}
      <Dialog open={isTicketDialogOpen} onOpenChange={setIsTicketDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <TicketIcon className="w-5 h-5" />
              {selectedTicket?.TicketNumber} - {selectedTicket?.Subject}
            </DialogTitle>
            <DialogDescription>
              Ticket details and conversation
            </DialogDescription>
          </DialogHeader>
          
          {selectedTicket && (
            <div className="space-y-6">
              {/* Ticket Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Ticket Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Status</Label>
                      <div className="mt-1">
                        <TicketStatusBadge status={selectedTicket.StatusCode} />
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Priority</Label>
                      <div className="mt-1">
                        <TicketPriorityBadge priority={selectedTicket.PriorityCode} />
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Category</Label>
                      <p className="mt-1 text-sm">{selectedTicket.category?.CategoryName}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Created</Label>
                      <p className="mt-1 text-sm">{formatDate(selectedTicket.CreatedAt)}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Opened By</Label>
                      <p className="mt-1 text-sm">
                        {selectedTicket.opened_by?.FirstName} {selectedTicket.opened_by?.LastName}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Assigned To</Label>
                      <p className="mt-1 text-sm">
                        {selectedTicket.assigned_to ? 
                          `${selectedTicket.assigned_to.FirstName} ${selectedTicket.assigned_to.LastName}` : 
                          'Unassigned'
                        }
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium">Description</Label>
                    <p className="mt-1 text-sm whitespace-pre-wrap">{selectedTicket.Description}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Comments */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Comments</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Add Comment */}
                  <div className="space-y-2">
                    <Label>Add Comment</Label>
                    <div className="flex gap-2">
                      <Textarea
                        placeholder="Add a comment..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        className="flex-1"
                        rows={3}
                      />
                      <Button 
                        onClick={handleAddComment}
                        disabled={!newComment.trim() || isSubmittingComment}
                      >
                        <MessageSquare className="w-4 h-4 mr-2" />
                        {isSubmittingComment ? 'Adding...' : 'Add'}
                      </Button>
                    </div>
                  </div>

                  {/* Comments List */}
                  <div className="space-y-4">
                    {selectedTicket.activities?.filter((activity: any) => activity.ActivityType === 'Comment').map((comment: any) => (
                      <TicketComment key={comment.ActivityID} comment={comment} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
} 