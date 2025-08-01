"use client"

import withRBAC from "@/lib/withRBAC"

function PerformancePage() {
  return <div className="p-6">Performance management - coming soon...</div>
}

export default withRBAC(PerformancePage, ["manager", "hr"]) 