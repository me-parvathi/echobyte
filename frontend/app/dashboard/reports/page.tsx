"use client"

import withRBAC from "@/lib/withRBAC"

function ReportsPage() {
  return <div className="p-6">Reports - coming soon...</div>
}

export default withRBAC(ReportsPage, ["manager", "hr"]) 