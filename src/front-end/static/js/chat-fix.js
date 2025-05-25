/**
 * Chat Interface Fix - Minimal approach
 * Only handles duplicate chat inputs and ensures responses appear in UI
 */

(function() {
    console.log("[chat-fix] Initializing minimal chat fixes");
    
    // PART 1: Remove duplicate chat inputs on page load
    function fixDuplicateInputs() {
        // Find the valid chat input within chat-section
        const chatSection = document.querySelector('.chat-section');
        if (!chatSection) return;
        
        const validInput = chatSection.querySelector('.chat-input');
        if (!validInput) return;
        
        // Make sure the valid one is visible
        validInput.style.display = 'block';
        
        // Find any inputs outside the chat-section and remove them
        document.querySelectorAll('.chat-input').forEach(input => {
            if (!chatSection.contains(input)) {
                console.log("[chat-fix] Removing duplicate chat input");
                input.remove();
            }
        });
    }
    
    // PART 2: Monitor for API responses and ensure they appear in the UI
    function monitorApiResponses() {
        const originalFetch = window.fetch;
        
        window.fetch = function(...args) {
            const promise = originalFetch.apply(this, args);
            
            // Only intercept chat-related API calls
            if (args[0] && typeof args[0] === 'string' && 
                (args[0].includes('/api/') || args[0].includes('/nlp/') || args[0].includes('/chat'))) {
                
                promise.then(response => {
                    // Clone the response so we can read it
                    const clone = response.clone();
                    
                    clone.json().then(data => {
                        // Check if this contains a message
                        if (data && (data.answer || data.message || data.response || data.content)) {
                            const messageText = data.answer || data.message || data.response || data.content || "";
                            console.log("[chat-fix] Intercepted response:", messageText.substring(0, 50) + "...");
                            
                            // Give the UI a moment to update naturally
                            setTimeout(() => {
                                ensureMessageIsDisplayed(messageText);
                            }, 500);
                        }
                    }).catch(() => {
                        // Not JSON, ignore
                    });
                });
            }
            
            return promise;
        };
    }
    
    // Helper: Ensure the message is displayed in the UI
    function ensureMessageIsDisplayed(messageText) {
        // First check if the message is already displayed
        const messagesContainer = document.querySelector('.chat-messages');
        if (!messagesContainer) return;
        
        let messageAlreadyDisplayed = false;
        
        // Check existing messages
        messagesContainer.querySelectorAll('.message-content').forEach(content => {
            // Standard duplicate check
            if (content.textContent.trim() === messageText.trim()) {
                messageAlreadyDisplayed = true;
                console.log("[chat-fix] Message already displayed");
            }
            
            // Special check for document analysis messages to avoid duplicates with same content
            if (messageText.includes('[Document Analysis]') && content.textContent.includes('[Document Analysis]')) {
                const newText = messageText.replace('[Document Analysis]', '').trim();
                const existingText = content.textContent.replace('[Document Analysis]', '').trim();
                
                if (newText === existingText) {
                    messageAlreadyDisplayed = true;
                    console.log("[chat-fix] Document analysis message already displayed with same content");
                }
            }
        });
        
        // If the message is not displayed yet, create a new message element
        if (!messageAlreadyDisplayed) {
            console.log("[chat-fix] Adding message to UI");
            const newMessage = document.createElement('div');
            newMessage.className = 'message assistant';
            
            newMessage.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content">${messageText}</div>
            `;
            
            messagesContainer.appendChild(newMessage);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    // Fix duplicate inputs immediately
    fixDuplicateInputs();
    
    // And also with a slight delay to catch any inputs added after page load
    setTimeout(fixDuplicateInputs, 300);
    setTimeout(fixDuplicateInputs, 1000);
    
    // Start monitoring API responses
    monitorApiResponses();
    
    // Create a MutationObserver to watch for any new chat inputs being added
    const bodyObserver = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length) {
                // Check if any chat inputs were added
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 && (
                        node.classList && node.classList.contains('chat-input') || 
                        node.querySelector && node.querySelector('.chat-input')
                    )) {
                        console.log("[chat-fix] New chat input detected, fixing duplicates");
                        fixDuplicateInputs();
                    }
                });
            }
        });
    });
    
    // Start observing the body
    bodyObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log("[chat-fix] Minimal chat fixes initialized");
})(); 