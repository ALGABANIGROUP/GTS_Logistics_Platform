// Sales Team Authentication Test Script
// Run this in the browser console (F12) on the Sales Team page

console.log('🔍 Sales Team Authentication Diagnostic');
console.log('=====================================');

// Check localStorage
console.log('1. LocalStorage Check:');
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');
const userData = localStorage.getItem('user');

console.log('- Access Token:', accessToken ? '✅ Present' : '❌ Missing');
console.log('- Refresh Token:', refreshToken ? '✅ Present' : '❌ Missing');
console.log('- User Data:', userData ? '✅ Present' : '❌ Missing');

if (userData) {
    try {
        const user = JSON.parse(userData);
        console.log('- User Role:', user.role || 'Not specified');
        console.log('- User Email:', user.email || 'Not specified');
    } catch (e) {
        console.log('- User Data Parse Error:', e.message);
    }
}

// Check sessionStorage
console.log('\n2. SessionStorage Check:');
const sessionUser = sessionStorage.getItem('user');
const authContext = sessionStorage.getItem('auth_context');

console.log('- Session User:', sessionUser ? '✅ Present' : '❌ Missing');
console.log('- Auth Context:', authContext ? '✅ Present' : '❌ Missing');

// Test API connectivity
console.log('\n3. API Connectivity Test:');
fetch('http://127.0.0.1:8000/api/v1/auth/me', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
})
.then(response => {
    console.log('- Auth API Status:', response.status);
    if (response.status === 200) {
        console.log('✅ Authentication API working');
        return response.json();
    } else {
        console.log('❌ Authentication API failed');
        throw new Error(`HTTP ${response.status}`);
    }
})
.then(data => {
    console.log('- Auth Response:', data);
})
.catch(error => {
    console.log('- Auth API Error:', error.message);
    console.log('💡 This might indicate expired token or backend not running');
});

// Quick fix functions
window.clearAuthStorage = function() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('auth_context');
    console.log('🧹 Auth storage cleared! Please refresh the page and log in again.');
};

window.showAuthStatus = function() {
    console.log('Current Auth Status:');
    console.log('- Token exists:', !!localStorage.getItem('access_token'));
    console.log('- User exists:', !!localStorage.getItem('user'));
    console.log('- Is authenticated (client-side):', !!window.authUser);
};

console.log('\n🔧 Available Commands:');
console.log('- clearAuthStorage(): Clear all auth data');
console.log('- showAuthStatus(): Show current auth status');
console.log('- window.location.href = "/login": Go to login page');

console.log('\n📋 Next Steps:');
console.log('1. If token is missing/expired: Run clearAuthStorage() then go to /login');
console.log('2. If backend is down: Check if backend server is running on port 8000');
console.log('3. If everything looks good: The Sales Team page should load with mock data');