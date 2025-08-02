"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Pagination } from "@/components/ui/pagination"
import { 
  Plus, 
  Send, 
  Clock, 
  RefreshCw, 
  MessageSquare, 
  Phone, 
  Mail, 
  AlertTriangle,
  Eye,
  TicketIcon
} from "lucide-react"
import { useTickets, useTicketLookups, useAssetSelection } from "@/hooks/use-tickets"
import useUserInfo from "@/hooks/use-user-info"
import { TicketStatusBadge } from "@/components/ui/ticket-status-badge"
import { TicketPriorityBadge } from "@/components/ui/ticket-priority-badge"
import { TicketComment } from "@/components/ui/ticket-comment"
import { TicketCreate } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"

export default function SupportTicket() {
  const { userInfo } = useUserInfo()
  const { toast } = useToast()
  
  // Form state
  const [categoryId, setCategoryId] = useState<string>("")
  const [priorityCode, setPriorityCode] = useState<string>("")
  const [subject, setSubject] = useState("")
  const [description, setDescription] = useState("")
  const [assetId, setAssetId] = useState<string>("none")
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Ticket dialog state
  const [selectedTicket, setSelectedTicket] = useState<any>(null)
  const [isTicketDialogOpen, setIsTicketDialogOpen] = useState(false)
  const [newComment, setNewComment] = useState("")
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [shouldFetchTickets, setShouldFetchTickets] = useState(false)

  // Hooks for data fetching with pagination
  const { 
    tickets, 
    loading: ticketsLoading, 
    error: ticketsError, 
    createTicket, 
    addComment,
    refetch: refetchTickets,
    currentPage,
    pageSize,
    totalCount,
    hasNext,
    hasPrevious,
    goToPage
  } = useTickets({
    immediate: shouldFetchTickets, // Only fetch when shouldFetchTickets is true
    pageSize: 5, // Small page size for user tickets
    filters: userInfo?.employeeId ? { opened_by_id: parseInt(userInfo.employeeId) } : {},
    onSuccess: (data) => {
      console.log('User tickets loaded successfully:', data);
    },
    onError: (error) => {
      console.error('Error loading user tickets:', error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      })
    }
  })

  // Debug logging
  console.log('SupportTicket render:', {
    userInfo: userInfo?.employeeId,
    shouldFetchTickets,
    ticketsLoading,
    ticketsError,
    ticketsCount: tickets?.length || 0,
    totalCount,
    currentPage,
    pageSize
  });

  // Set shouldFetchTickets when userInfo becomes available
  useEffect(() => {
    if (userInfo?.employeeId && !shouldFetchTickets) {
      console.log('User info available, enabling ticket fetch for employee:', userInfo.employeeId);
      setShouldFetchTickets(true);
    }
  }, [userInfo?.employeeId, shouldFetchTickets]);

  const { 
    categories, 
    priorities, 
    loading: lookupsLoading, 
    error: lookupsError 
  } = useTicketLookups()

  const { 
    assets, 
    loading: assetsLoading 
  } = useAssetSelection(
    userInfo?.employeeId ? parseInt(userInfo.employeeId) : 0,
    categoryId ? parseInt(categoryId) : undefined
  )

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!userInfo?.employeeId) {
      toast({
        title: "Error",
        description: "User information not available",
        variant: "destructive"
      })
      return
    }

    if (!categoryId || !priorityCode || !subject || !description) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive"
      })
      return
    }

    setIsSubmitting(true)

    try {
      const ticketData: TicketCreate = {
        Subject: subject,
        Description: description,
        CategoryID: parseInt(categoryId),
        PriorityCode: priorityCode,
        StatusCode: "Open",
        AssetID: assetId && assetId !== "none" ? parseInt(assetId) : undefined
      }

      await createTicket(ticketData, parseInt(userInfo.employeeId))
      
      // Reset form
      setCategoryId("")
      setPriorityCode("")
      setSubject("")
      setDescription("")
      setAssetId("none")

      toast({
        title: "Success",
        description: "Ticket created successfully",
      })
    } catch (error) {
      console.error("Failed to create ticket:", error)
      toast({
        title: "Error",
        description: "Failed to create ticket. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return "Unknown date"
    }
  }

  // Calculate total pages for user tickets
  const totalPages = Math.ceil(totalCount / pageSize)

  // Open ticket details dialog
  const openTicketDialog = (ticket: any) => {
    setSelectedTicket(ticket)
    setIsTicketDialogOpen(true)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Tickets</h1>
          <p className="text-gray-600">Create and manage your support requests</p>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Create Ticket Form */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Create New Ticket
            </CardTitle>
            <CardDescription>Submit a new support request or report an issue</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select value={categoryId} onValueChange={setCategoryId} required>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.CategoryID} value={category.CategoryID.toString()}>
                        <div>
                          <div className="font-medium">{category.CategoryName}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">Priority Level *</Label>
                <Select value={priorityCode} onValueChange={setPriorityCode} required>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    {priorities.map((priority) => (
                      <SelectItem key={priority.PriorityCode} value={priority.PriorityCode}>
                        <div className="flex items-center gap-2">
                          <TicketPriorityBadge priority={priority.PriorityCode} />
                          <div>
                            <div className="font-medium">{priority.PriorityName}</div>
                            <div className="text-sm text-gray-500">SLA: {priority.SLAHours}h</div>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="asset">Related Asset (Optional)</Label>
                <Select value={assetId} onValueChange={setAssetId}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select asset (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No asset</SelectItem>
                    {assets?.personal_assets.map((asset) => (
                      <SelectItem key={asset.AssetID} value={asset.AssetID.toString()}>
                        <div>
                          <div className="font-medium">{asset.AssetTag}</div>
                          <div className="text-sm text-gray-500">{asset.AssetTypeName} - {asset.LocationName}</div>
                        </div>
                      </SelectItem>
                    ))}
                    {assets?.community_assets.map((asset) => (
                      <SelectItem key={asset.AssetID} value={asset.AssetID.toString()}>
                        <div>
                          <div className="font-medium">{asset.AssetTag} (Community)</div>
                          <div className="text-sm text-gray-500">{asset.AssetTypeName} - {asset.LocationName}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject *</Label>
                <Input
                  id="subject"
                  placeholder="Brief description of your issue"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Please provide detailed information about your request or issue..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={5}
                  className="resize-none"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                disabled={isSubmitting || lookupsLoading}
              >
                {isSubmitting ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Submitting Ticket...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Submit Ticket
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Quick Help */}
        <Card className="border-0 shadow-sm">
          <CardHeader>
            <CardTitle>Quick Help</CardTitle>
            <CardDescription>Common support categories and contact information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-gray-900">IT Support</h4>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                    <Phone className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                    <Mail className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">Technical issues, software, hardware</p>
              <p className="text-sm font-medium text-blue-600">Ext: 2001 | it-support@company.com</p>
            </div>

            <div className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors duration-200">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-gray-900">HR Support</h4>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                    <Phone className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                    <Mail className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">Benefits, policies, employee relations</p>
              <p className="text-sm font-medium text-blue-600">Ext: 2002 | hr@company.com</p>
            </div>

            <div className="p-4 bg-red-50 rounded-xl border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <h4 className="font-medium text-red-900">Emergency</h4>
              </div>
              <p className="text-sm text-red-700">For urgent security or safety issues, call: ext. 911</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User's Tickets */}
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Your Support Tickets ({totalCount} total)</CardTitle>
          <CardDescription>Track the status of your submitted tickets</CardDescription>
        </CardHeader>
        <CardContent>
          {ticketsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Clock className="w-6 h-6 animate-spin mr-2" />
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
              <p className="text-sm">Create your first support ticket above</p>
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
                          className="bg-transparent"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination for user tickets */}
              {totalPages > 1 && (
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
              )}
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
