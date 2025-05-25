/**
 * User Display Manager
 * Shows user info when logged in, hides when logged out
 */

(function() {
    console.log("[user-display] Initializing user display manager");
    
    // State tracking
    let currentUsername = null;
    
    // Function to extract user info from various sources
    function getUserInfo() {
        // Check session storage first (most reliable for current session)
        const sessionUser = sessionStorage.getItem('username') || 
                           sessionStorage.getItem('email') || 
                           sessionStorage.getItem('user_email');
        
        // Then check local storage
        const localUser = localStorage.getItem('username') || 
                         localStorage.getItem('email') || 
                         localStorage.getItem('adminname') || 
                         localStorage.getItem('org_name');
        
        // Check for token (means user is logged in even if we don't have name)
        const hasToken = localStorage.getItem('token') !== null;
        
        // Try DOM elements that might contain user info
        const accountNameElement = document.querySelector('.user-account-info .user-name');
        const domUsername = accountNameElement ? accountNameElement.textContent.trim() : null;
        
        // Prioritize sources (DOM > Session > Local)
        const username = domUsername || sessionUser || localUser;
        
        return {
            username: username,
            isLoggedIn: hasToken || username !== null,
            email: sessionStorage.getItem('email') || localStorage.getItem('email')
        };
    }
    
    // Function to update the header with user info
    function updateHeaderUserInfo() {
        const userInfo = getUserInfo();
        const sidebarHeader = document.querySelector('.sidebar-header');
        
        // Remove any existing username display first
        const existingDisplay = document.getElementById('header-username');
        if (existingDisplay && existingDisplay.parentNode) {
            existingDisplay.parentNode.removeChild(existingDisplay);
        }
        
        // If user is logged in, show username in header
        if (userInfo.isLoggedIn && userInfo.username && sidebarHeader) {
            // Create username element if user is logged in
            const displayText = userInfo.email || userInfo.username;
            
            if (displayText && displayText !== 'TestUser') {
                const usernameElement = document.createElement('span');
                usernameElement.id = 'header-username';
                usernameElement.className = 'header-username';
                usernameElement.textContent = displayText;
                
                // Add styles inline to ensure they apply
                usernameElement.style.marginLeft = '10px';
                usernameElement.style.color = 'rgba(255, 255, 255, 0.9)';
                usernameElement.style.fontWeight = '600';
                usernameElement.style.fontSize = '14px';
                usernameElement.style.display = 'inline-block';
                usernameElement.style.maxWidth = '180px';
                usernameElement.style.whiteSpace = 'nowrap';
                usernameElement.style.overflow = 'hidden';
                usernameElement.style.textOverflow = 'ellipsis';
                
                // Add it after the Farqad text
                const logoText = sidebarHeader.querySelector('span');
                if (logoText) {
                    logoText.parentNode.insertBefore(usernameElement, logoText.nextSibling);
                    console.log("[user-display] Added user info to header:", displayText);
                    
                    // Track current username to avoid unnecessary updates
                    currentUsername = displayText;
                }
            }
        } else {
            console.log("[user-display] User not logged in or no username available");
            currentUsername = null;
        }
    }
    
    // Function to handle login/logout button visibility
    function updateLoginButtons() {
        const userInfo = getUserInfo();
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (!loginBtn || !logoutBtn) return;
        
        if (userInfo.isLoggedIn) {
            // User is logged in - hide login, show logout
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'flex';
        } else {
            // User is logged out - show login, hide logout
            loginBtn.style.display = 'flex';
            logoutBtn.style.display = 'none';
        }
    }
    
    // Run immediately
    updateHeaderUserInfo();
    updateLoginButtons();
    
    // Also run after delays to ensure DOM is loaded
    setTimeout(updateHeaderUserInfo, 300);
    setTimeout(updateLoginButtons, 300);
    setTimeout(updateHeaderUserInfo, 1000);
    
    // Set up polling to keep the display up to date
    setInterval(() => {
        const userInfo = getUserInfo();
        
        // Only update if username has changed
        if (userInfo.username !== currentUsername) {
            updateHeaderUserInfo();
            updateLoginButtons();
        }
    }, 2000);
    
    // Listen for storage events (login/logout)
    window.addEventListener('storage', function(e) {
        if (e.key === 'token' || e.key === 'username' || e.key === 'email' || 
            e.key === 'adminname' || e.key === 'org_name') {
            updateHeaderUserInfo();
            updateLoginButtons();
        }
    });
    
    // Handle DOM mutations to detect login status changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                // Check if user-account-info is modified
                if (mutation.target.closest && mutation.target.closest('.user-account-info')) {
                    updateHeaderUserInfo();
                    updateLoginButtons();
                }
            }
        });
    });
    
    // Start observing relevant parts of the document
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    console.log("[user-display] User display manager initialized");
})(); 