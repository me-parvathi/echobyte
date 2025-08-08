// Test script to verify manager detection
console.log("🧪 Testing Manager Detection");

// Test the role-based detection
async function testManagerDetection() {
  try {
    // Test the role fetching
    const response = await fetch('/api/auth/employee-roles/current', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (response.ok) {
      const roles = await response.json();
      console.log("✅ User roles:", roles);
      
      // Check for manager role
      const hasManagerRole = roles.some(role => role.RoleName === "Manager" && role.IsActive);
      const hasHRRole = roles.some(role => role.RoleName === "HR Manager" && role.IsActive);
      
      console.log("Manager role:", hasManagerRole);
      console.log("HR role:", hasHRRole);
      
      if (hasManagerRole || hasHRRole) {
        console.log("✅ User is a manager or HR - should see feedback viewer tab");
      } else {
        console.log("❌ User is not a manager or HR - won't see feedback viewer tab");
      }
    } else {
      console.log("❌ Failed to fetch roles:", response.status);
    }
  } catch (error) {
    console.error("❌ Error testing manager detection:", error);
  }
}

// Run the test
testManagerDetection(); 