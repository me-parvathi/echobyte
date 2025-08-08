"use client"

import withRBAC from "@/lib/withRBAC"

function OnboardingPage() {
  return <div className="p-6">Onboarding management - coming soon...</div>
}

export default withRBAC(OnboardingPage, ["hr"]) 