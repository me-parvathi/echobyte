"use client"

import AssetManagement from "@/components/features/asset-management"
import withRBAC from "@/lib/withRBAC"

function AssetsContent() {
  return <AssetManagement />
}

export default withRBAC(AssetsContent, ["it"]); 