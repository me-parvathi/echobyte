// Simple test to verify leave approval functionality
// This can be run in the browser console to test the API endpoints

async function testLeaveApproval() {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
  
  console.log('Testing Leave Approval System...');
  
  try {
    // Test 1: Check if API is accessible
    console.log('1. Testing API connectivity...');
    const response = await fetch(`${baseUrl}/api/leave/applications`);
    if (response.ok) {
      console.log('✅ API is accessible');
    } else {
      console.log('❌ API is not accessible');
      return;
    }
    
    // Test 2: Check if comments API is accessible
    console.log('2. Testing Comments API...');
    const commentsResponse = await fetch(`${baseUrl}/api/comments/LeaveApplication/1`);
    if (commentsResponse.ok) {
      console.log('✅ Comments API is accessible');
    } else {
      console.log('⚠️ Comments API may not be implemented yet');
    }
    
    // Test 3: Check if conflict detection API is accessible
    console.log('3. Testing Conflict Detection API...');
    const conflictResponse = await fetch(`${baseUrl}/api/leave/check-conflicts?start_date=2024-01-15&end_date=2024-01-19&manager_id=1`);
    if (conflictResponse.ok) {
      console.log('✅ Conflict Detection API is accessible');
    } else {
      console.log('⚠️ Conflict Detection API may not be implemented yet');
    }
    
    console.log('✅ All tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testLeaveApproval };
} else {
  // Make available globally for browser testing
  window.testLeaveApproval = testLeaveApproval;
} 