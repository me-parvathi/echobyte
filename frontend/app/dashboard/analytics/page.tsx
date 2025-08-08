"use client";

import withRBAC from "@/lib/withRBAC";

function AnalyticsPage() {
  return (
    <div className="p-6">
      <iframe
        title="HR Portal Dashboards"
        width="100%"
        height="600"
        src="https://app.powerbi.com/view?r=eyJrIjoiYmYyYWExOGUtNDBhYy00ZWQ3LWE4NTAtZTI3N2I1NWVmOThhIiwidCI6IjBlYWRiNzdlLTQyZGMtNDdmOC1iYmUzLWVjMjM5NWUwNzEyYyIsImMiOjZ9"
        frameBorder="0"
        allowFullScreen
      ></iframe>
    </div>
  );
}

export default withRBAC(AnalyticsPage, ["hr", "manager"]);
