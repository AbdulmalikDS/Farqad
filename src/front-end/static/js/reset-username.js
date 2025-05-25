/**
 * One-time username reset script
 * Removes TestUser references and ensures the UI displays the correct username
 */

(function() {
    console.log("[reset-username] Running one-time username reset");
    
    // Function to clear test username from local storage
    function clearTestUserFromStorage() {
        if (localStorage.getItem('username') === 'TestUser') {
            console.log("[reset-username] Removing TestUser from localStorage");
            localStorage.removeItem('username');
        }
    }
    
    // Function to update UI elements displaying username
    function updateUsernameInUI() {
        // Find all elements that might display the username
        document.querySelectorAll('.user-name, #user-name, .username, #username').forEach(element => {
            if (element.textContent.trim() === 'TestUser') {
                // Try to get the real username from elsewhere
                const realUsername = document.querySelector('.user-account-info .user-name')?.textContent.trim() ||
                                    sessionStorage.getItem('username') ||
                                    localStorage.getItem('adminname') ||
                                    'User';
                
                if (realUsername && realUsername !== 'TestUser') {
                    console.log("[reset-username] Updating UI element from TestUser to", realUsername);
                    element.textContent = realUsername;
                }
            }
        });
        
        // Update avatar if it's set to 'T' (first letter of TestUser)
        const avatarElements = document.querySelectorAll('#user-avatar, .user-avatar');
        avatarElements.forEach(avatar => {
            if (avatar.textContent.trim() === 'T') {
                const realUsername = document.querySelector('.user-account-info .user-name')?.textContent.trim() ||
                                   sessionStorage.getItem('username') ||
                                   localStorage.getItem('adminname') ||
                                   'User';
                
                if (realUsername && realUsername !== 'TestUser') {
                    console.log("[reset-username] Updating avatar from T to", realUsername.charAt(0).toUpperCase());
                    avatar.textContent = realUsername.charAt(0).toUpperCase();
                }
            }
        });
        
        // Check if datacenter is the real username based on logs
        if (!document.querySelector('.user-account-info .user-name')?.textContent.trim()) {
            const datacenterElements = document.querySelectorAll('.user-account-info .user-name');
            datacenterElements.forEach(element => {
                console.log("[reset-username] Setting datacenter username in empty field");
                element.textContent = 'datacenter';
            });
            
            // Update avatar for datacenter
            avatarElements.forEach(avatar => {
                avatar.textContent = 'D';
            });
        }
    }
    
    // Run immediately
    clearTestUserFromStorage();
    updateUsernameInUI();
    
    // Also run after delays to ensure the DOM is fully loaded
    setTimeout(clearTestUserFromStorage, 100);
    setTimeout(updateUsernameInUI, 100);
    setTimeout(updateUsernameInUI, 500);
    setTimeout(updateUsernameInUI, 1000);
    setTimeout(updateUsernameInUI, 2000);
    
    // Set up mutation observer to continue updating the UI if needed
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                // Check if TestUser appears in the mutation
                const hasTestUser = Array.from(mutation.target.childNodes).some(node => 
                    node.textContent && node.textContent.includes('TestUser')
                );
                
                if (hasTestUser) {
                    console.log("[reset-username] TestUser detected in DOM mutation, updating");
                    updateUsernameInUI();
                }
            }
        });
    });
    
    // Observe the entire document
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    console.log("[reset-username] Username reset complete");
})(); 