/**
 * Login Display Fix
 * Fixes login button visibility only
 */

(function() {
    console.log("[login-fix] Initializing login display fixes");
    
    // Function to properly handle login/logout button visibility
    function fixLoginButtonVisibility() {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const loginContainer = document.querySelector('.login-container');
        
        if (!loginBtn || !logoutBtn) return;
        
        // Check if user is logged in by looking for token, username, etc.
        const isLoggedIn = localStorage.getItem('token') || 
                          localStorage.getItem('username') || 
                          localStorage.getItem('adminname') ||
                          localStorage.getItem('org_name');
        
        // For debugging
        console.log("[login-fix] Login status check - Token:", localStorage.getItem('token'));
        console.log("[login-fix] Login status check - Username:", localStorage.getItem('username'));
        
        // Set visibility based on login status
        if (isLoggedIn) {
            // Hide login, show logout
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'flex';
            
            // Force applying display property directly
            loginBtn.setAttribute('style', 'display: none !important');
            logoutBtn.setAttribute('style', 'display: flex !important');
            
            // Apply CSS class for extra clarity
            loginBtn.classList.add('hidden');
            logoutBtn.classList.remove('hidden');
            
            console.log("[login-fix] User is logged in, hiding login button");
            
            // IMPORTANT: Remove the test username if it exists
            if (localStorage.getItem('username') === 'TestUser') {
                console.log("[login-fix] Removing test username");
                localStorage.removeItem('username');
            }
        } else {
            // Show login, hide logout
            loginBtn.style.display = 'flex';
            logoutBtn.style.display = 'none';
            
            // Force applying display property directly
            loginBtn.setAttribute('style', 'display: flex !important');
            logoutBtn.setAttribute('style', 'display: none !important');
            
            // Apply CSS class for extra clarity
            loginBtn.classList.remove('hidden');
            logoutBtn.classList.add('hidden');
            
            console.log("[login-fix] User is not logged in, showing login button");
        }
    }
    
    // Function to remove any existing username from the header if it's there
    function removeUsernameFromIcon() {
        const usernameElement = document.getElementById('header-username');
        if (usernameElement && usernameElement.parentNode) {
            usernameElement.parentNode.removeChild(usernameElement);
            console.log("[login-fix] Removed username from logo area");
        }
    }
    
    // Function to sync with server-side user data
    function syncWithServerUser() {
        // Find UI elements that might show the username
        const accountNameElement = document.querySelector('.user-account-info .user-name');
        const avatarElement = document.getElementById('user-avatar');
        
        if (accountNameElement) {
            // Get the actual username from the UI
            const displayedName = accountNameElement.textContent.trim();
            
            if (displayedName && displayedName !== 'TestUser') {
                console.log("[login-fix] Found actual username in UI:", displayedName);
                
                // Update localStorage with the actual username
                localStorage.setItem('username', displayedName);
                
                // Update the avatar if it exists
                if (avatarElement) {
                    avatarElement.textContent = displayedName.charAt(0).toUpperCase();
                }
            }
        }
    }
    
    // Run fixes immediately
    fixLoginButtonVisibility();
    removeUsernameFromIcon();
    syncWithServerUser();
    
    // Also run after a short delay to ensure DOM is fully loaded
    setTimeout(fixLoginButtonVisibility, 300);
    setTimeout(removeUsernameFromIcon, 300);
    setTimeout(syncWithServerUser, 300);
    
    // Monitor localStorage changes to update login button status
    window.addEventListener('storage', function(e) {
        if (e.key === 'token' || e.key === 'username' || e.key === 'adminname' || e.key === 'org_name') {
            fixLoginButtonVisibility();
        }
    });
    
    console.log("[login-fix] Login display fixes initialized");
})(); 