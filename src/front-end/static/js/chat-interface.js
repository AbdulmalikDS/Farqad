/**
 * Chat Interface Enhancements
 * Adds modern UI interactions to the chat interface
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Chat interface enhancements loading...");
    
    // Fix any existing message structure issues
    fixMessageStructure();
    
    // Add message animation class to existing messages
    initializeMessageAnimations();
    
    // Input field focus/blur effects
    setupInputEffects();
    
    // Enhanced scroll behavior
    setupSmoothScrolling();
    
    // Enhanced message display
    enhanceMessageDisplay();
    
    // Override the original addMessage function to ensure all messages are visible
    overrideAddMessage();
    
    console.log("Chat interface enhancements loaded successfully");
});

/**
 * Fix message structure issues
 */
function fixMessageStructure() {
    // Make sure the chat messages container exists
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) {
        console.error("Chat messages container not found");
        return;
    }
    
    // Fix existing messages that might have incorrect classes
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(message => {
        // Make sure all messages have either user or assistant class
        if (!message.classList.contains('user') && !message.classList.contains('assistant')) {
            message.classList.add('assistant'); // Default to assistant
        }
        
        // Make sure all messages have animated class
        message.classList.add('animated');
        
        // Make sure message content is formatted correctly
        const content = message.querySelector('.message-content');
        if (content) {
            content.dataset.formatted = 'true';
        }
    });
    
    // Make sure chat section and container are visible
    const chatSection = document.querySelector('.chat-section');
    if (chatSection) {
        chatSection.style.display = 'flex';
    }
    
    // Ensure the dashboard content container is properly structured
    const dashboardContent = document.querySelector('.dashboard-content');
    if (dashboardContent) {
        dashboardContent.style.display = 'flex';
    }
}

/**
 * Initialize animations for existing messages
 */
function initializeMessageAnimations() {
    const messages = document.querySelectorAll('.message');
    console.log(`Found ${messages.length} existing messages to animate`);
    
    messages.forEach((message, index) => {
        // Add animated class to all messages immediately
        message.classList.add('animated');
    });
    
    // Listen for new messages being added to the DOM
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('message')) {
                            // Add animation class immediately
                            node.classList.add('animated');
                            console.log("New message added and animated");
                        }
                    });
                }
            });
        });
        
        observer.observe(chatMessages, { childList: true });
    }
}

/**
 * Override the original addMessage function if needed
 */
function overrideAddMessage() {
    // Only override if the original function exists and we can access it
    if (window.addMessage && typeof window.addMessage === 'function') {
        const originalAddMessage = window.addMessage;
        
        window.addMessage = function(message, isUserMessage) {
            console.log(`Adding message: ${isUserMessage ? 'User' : 'Assistant'}`);
            
            // Create message element if original function doesn't
            let messageElement = originalAddMessage(message, isUserMessage);
            
            if (!messageElement) {
                console.log("Original addMessage didn't return an element, creating one manually");
                // Create a new message element
                messageElement = document.createElement('div');
                messageElement.className = `message ${isUserMessage ? 'user' : 'assistant'}`;
                
                // Create avatar
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = isUserMessage ? '👤' : '🤖';
                
                // Create content
                const content = document.createElement('div');
                content.className = 'message-content';
                content.innerHTML = message;
                
                // Add to message
                messageElement.appendChild(avatar);
                messageElement.appendChild(content);
                
                // Add to chat messages
                const chatMessages = document.querySelector('.chat-messages');
                if (chatMessages) {
                    chatMessages.appendChild(messageElement);
                }
            }
            
            // Ensure the message element is visible and has the animated class
            if (messageElement) {
                messageElement.classList.add('animated');
                
                // Add timestamp
                if (!messageElement.querySelector('.message-timestamp')) {
                    const timestamp = document.createElement('div');
                    timestamp.className = 'message-timestamp';
                    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    messageElement.appendChild(timestamp);
                }
                
                // Add mouse hover effects
                messageElement.addEventListener('mouseenter', () => {
                    messageElement.classList.add('hovered');
                });
                
                messageElement.addEventListener('mouseleave', () => {
                    messageElement.classList.remove('hovered');
                });
                
                // Scroll into view
                messageElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
            
            return messageElement;
        };
        
        console.log('Successfully enhanced the addMessage function');
    } else {
        console.log('Original addMessage function not found, will use observer instead');
    }
}

/**
 * Setup enhanced input field effects
 */
function setupInputEffects() {
    const inputField = document.querySelector('.input-container input[type="text"]');
    const inputContainer = document.querySelector('.input-container');
    
    if (inputField && inputContainer) {
        // Focus effect
        inputField.addEventListener('focus', () => {
            inputContainer.classList.add('focused');
        });
        
        // Blur effect
        inputField.addEventListener('blur', () => {
            inputContainer.classList.remove('focused');
        });
        
        // Auto-focus on page load
        setTimeout(() => {
            inputField.focus();
        }, 500);
        
        // Handle Enter key
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && inputField.value.trim() !== '') {
                const sendButton = document.querySelector('.send-btn');
                if (sendButton) {
                    sendButton.click();
                }
            }
        });
    }
}

/**
 * Setup smooth scrolling for chat messages
 */
function setupSmoothScrolling() {
    const chatMessages = document.querySelector('.chat-messages');
    
    if (chatMessages) {
        // Initial scroll to bottom
        scrollToBottom();
        
        // Listen for new content
        const observer = new MutationObserver(() => {
            scrollToBottom();
        });
        
        observer.observe(chatMessages, { childList: true, subtree: true });
    }
}

/**
 * Scroll chat container to bottom
 */
function scrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

/**
 * Enhance message display with interactive elements
 */
function enhanceMessageDisplay() {
    // Add timestamp support
    addMessageTimestamps();
    
    // Add hover effects
    setupMessageHoverEffects();
    
    // Support for code blocks and formatting in messages
    enhanceMessageFormatting();
}

/**
 * Add timestamps to messages
 */
function addMessageTimestamps() {
    const messages = document.querySelectorAll('.message');
    
    messages.forEach(message => {
        if (!message.querySelector('.message-timestamp')) {
            const timestamp = document.createElement('div');
            timestamp.className = 'message-timestamp';
            timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            message.appendChild(timestamp);
        }
    });
}

/**
 * Setup hover effects for messages
 */
function setupMessageHoverEffects() {
    const messages = document.querySelectorAll('.message');
    
    messages.forEach(message => {
        message.addEventListener('mouseenter', () => {
            message.classList.add('hovered');
        });
        
        message.addEventListener('mouseleave', () => {
            message.classList.remove('hovered');
        });
    });
}

/**
 * Enhance message formatting for code blocks, links, etc.
 */
function enhanceMessageFormatting() {
    const messageContents = document.querySelectorAll('.message-content');
    
    messageContents.forEach(content => {
        // Process only if not already processed
        if (!content.dataset.formatted) {
            // Mark as processed
            content.dataset.formatted = 'true';
            
            // Make links clickable
            content.innerHTML = content.innerHTML.replace(
                /(https?:\/\/[^\s]+)/g, 
                '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
            );
        }
    });
} 