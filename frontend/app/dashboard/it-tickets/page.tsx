"use client"

import withRBAC from "@/lib/withRBAC"
import { ITTicketsManager } from "@/components/features/it-tickets-manager"

function ITTicketsPage() {
  return <ITTicketsManager />
}

export default withRBAC(ITTicketsPage, ["it"]) 