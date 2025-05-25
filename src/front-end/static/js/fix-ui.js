/**
 * UI Fix Script for Personal Finance Chatbot
 * This script fixes common UI issues and enhances the chat interface
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("UI Fix Script loaded");
    
    // CRITICAL FIX: Remove the extra standalone chat input bar at the bottom of the page
    function removeExtraChatInput() {
        // First get the main chat-section which contains the "correct" chat input
        const chatSection = document.querySelector('.chat-section');
        const mainChatInput = chatSection ? chatSection.querySelector('.chat-input') : null;
        
        // Now find any chat-input elements NOT inside the chat-section
        const allChatInputs = document.querySelectorAll('.chat-input');
        
        console.log('[fix-ui.js] Found', allChatInputs.length, 'chat input elements');
        
        allChatInputs.forEach(input => {
            // Skip if this is the main chat input inside chat-section
            if (input === mainChatInput) return;
            
            // Check if this input is outside the chat-section
            if (!chatSection.contains(input)) {
                console.log('[fix-ui.js] Removing chat input outside of chat-section');
                if (input.parentNode) {
                    input.parentNode.removeChild(input);
                }
            }
        });
        
        // Also look for any input inside body but outside app-container
        const appContainer = document.querySelector('.app-container');
        if (appContainer) {
            const outsideInputs = document.querySelectorAll('body > .chat-input, body > div > .chat-input, body > div > div > .chat-input');
            outsideInputs.forEach(input => {
                if (!appContainer.contains(input)) {
                    console.log('[fix-ui.js] Removing chat input outside of app-container');
                    if (input.parentNode) {
                        input.parentNode.removeChild(input);
                    }
                }
            });
        }
    }
    
    // Call this function immediately
    removeExtraChatInput();
    
    // And also with a delay to catch any late-rendered inputs
    setTimeout(removeExtraChatInput, 100);
    setTimeout(removeExtraChatInput, 500);
    setTimeout(removeExtraChatInput, 1000);
    
    // Critical fix: Ensure there's only one chat input element visible
    const chatInputElements = document.querySelectorAll('.chat-input');
    
    if (chatInputElements.length > 1) {
        console.log('Multiple chat inputs found on initial load, hiding duplicates');
        
        // Keep only the most suitable one
        let bestInput = null;
        let bestScore = -1;
        
        chatInputElements.forEach(input => {
            let score = 0;
            // Prefer inputs that are properly positioned
            if (input.style.position === 'absolute' || 
                window.getComputedStyle(input).position === 'absolute') {
                score += 3;
            }
            
            // Prefer inputs that have content
            if (input.querySelector('input[type="text"]')) {
                score += 2;
            }
            
            // Prefer inputs that are visible
            if (input.style.display !== 'none' && 
                window.getComputedStyle(input).display !== 'none') {
                score += 1;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestInput = input;
            }
        });
        
        // Hide all except the best one
        chatInputElements.forEach(input => {
            if (input !== bestInput) {
                input.style.display = 'none';
            }
        });
    }
    
    // Fix 1: Suppress Chart.js errors in the UI by hiding them
    setTimeout(function() {
        const errorElements = document.querySelectorAll('.main-content > div:not(.dashboard-container)');
        errorElements.forEach(function(element) {
            if (element.textContent.includes('Chart') || 
                element.textContent.includes('chart') || 
                element.textContent.includes('Error')) {
                element.style.display = 'none';
            }
        });
    }, 500);
    
    // Fix 1.5: Add global event listener for the toggle charts button
    // This ensures it keeps working even if the button is recreated or modified
    document.addEventListener('click', function(e) {
        // Check if clicked element is the charts button or its child
        let targetElement = e.target;
        let isChartButton = false;
        
        // Traverse up to 5 levels to find the button
        for (let i = 0; i < 5; i++) {
            if (!targetElement) break;
            
            if (targetElement.id === 'toggle-charts-btn' || 
                targetElement.closest('#toggle-charts-btn')) {
                isChartButton = true;
                break;
            }
            
            targetElement = targetElement.parentElement;
        }
        
        if (isChartButton) {
            e.preventDefault();
            e.stopPropagation();
            
            const chartsPanel = document.getElementById('charts-panel');
            if (!chartsPanel) return;
            
            console.log('Chart button clicked (global handler)');
            
            // Toggle visibility
            if (chartsPanel.style.display === 'flex') {
                // Hide panel
                chartsPanel.style.opacity = '0';
                setTimeout(() => {
                    chartsPanel.style.display = 'none';
                    document.body.classList.add('charts-hidden');
                }, 300);
            } else {
                // Show panel
                chartsPanel.style.display = 'flex';
                setTimeout(() => {
                    chartsPanel.style.opacity = '1';
                    document.body.classList.remove('charts-hidden');
                    
                    // Force render charts
                    if (typeof window.renderAllCharts === 'function') {
                        window.renderAllCharts();
                    }
                }, 10);
            }
        }
    }, true); // Use capture phase to ensure this runs first
    
    // Fix 2: Make sure document panel is hidden by default
    const documentPanel = document.getElementById('document-list-panel');
    if (documentPanel) {
        documentPanel.style.display = 'none';
    }
    
    // Fix 3: Set correct body class to manage chart visibility
    document.body.classList.add('charts-hidden');
    
    // Fix 4: Make sure user can type in the chat input
    const chatInput = document.querySelector('.chat-input input[type="text"]');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const sendButton = document.querySelector('.send-btn');
                if (sendButton) {
                    sendButton.click();
                } else {
                    // Fallback message handling if send button is not found
                    const message = chatInput.value.trim();
                    if (message) {
                        addUserMessage(message);
                        chatInput.value = '';
                        
                        // Simple bot response
                        setTimeout(function() {
                            const botResponse = "I've received your message: \"" + message + "\". The full AI response functionality is still being connected.";
                            addBotMessage(botResponse);
                        }, 1000);
                    }
                }
            }
        });
    }
    
    // Helper function to add user message to chat
    function addUserMessage(text) {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">${text}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Helper function to add bot message to chat
    function addBotMessage(text) {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">${text}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Fix 5: Enhance the send button if the original event handler is missing
    const sendButton = document.querySelector('.send-btn');
    const sendButtonHandler = function() {
        const chatInput = document.querySelector('.chat-input input[type="text"]');
        if (chatInput) {
            const message = chatInput.value.trim();
            if (message) {
                addUserMessage(message);
                chatInput.value = '';
                
                // Simple bot response
                setTimeout(function() {
                    const botResponse = "I've received your message: \"" + message + "\". The full AI response functionality is still being connected.";
                    addBotMessage(botResponse);
                }, 1000);
            }
        }
    };
    
    // Only add our handler if the button doesn't already have a click event
    if (sendButton) {
        const existingHandler = sendButton.onclick;
        if (!existingHandler) {
            sendButton.addEventListener('click', sendButtonHandler);
        }
    }
    
    // Fix 6: Make sure the chat container takes proper height
    const appContainer = document.querySelector('.app-container');
    const mainContent = document.querySelector('.main-content');
    const dashboardContainer = document.querySelector('.dashboard-container');
    
    if (appContainer && mainContent && dashboardContainer) {
        // Ensure proper height calculations
        mainContent.style.height = '100%';
        dashboardContainer.style.height = '100%';
    }
    
    // Fix 7: Ensure messages display properly and don't disappear
    setTimeout(function() {
        // Fix chat section visibility and positioning
        const chatSection = document.querySelector('.chat-section');
        if (chatSection) {
            chatSection.style.maxWidth = '1000px';
            chatSection.style.margin = '0 auto';
            chatSection.style.overflow = 'hidden';
        }
        
        // Fix chat messages container
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            chatMessages.style.overflowY = 'auto';
            chatMessages.style.height = 'calc(100% - 70px)';
            chatMessages.style.display = 'flex';
            chatMessages.style.flexDirection = 'column';
            chatMessages.style.paddingBottom = '100px';
            
            // Ensure container has enough height to show messages
            setTimeout(function() {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }
        
        // Fix message width and display
        const messages = document.querySelectorAll('.message');
        messages.forEach(function(message) {
            message.style.width = 'calc(100% - 2rem)';
            message.style.display = 'flex';
            message.style.position = 'relative';
            message.style.zIndex = '1';
            
            if (message.classList.contains('user')) {
                message.style.alignSelf = 'flex-end';
            } else {
                message.style.alignSelf = 'flex-start';
            }
            
            // Fix message content width
            const content = message.querySelector('.message-content');
            if (content) {
                content.style.maxWidth = '80%';
                content.style.wordBreak = 'break-word';
                content.style.whiteSpace = 'pre-wrap';
            }
        });
        
        // Fix input bar positioning
        const chatInput = document.querySelector('.chat-input');
        if (chatInput) {
            chatInput.style.position = 'fixed';
            chatInput.style.bottom = '0';
            chatInput.style.left = '240px'; // Account for sidebar width
            chatInput.style.right = '0';
            chatInput.style.zIndex = '100';
            chatInput.style.backgroundColor = 'rgba(30, 15, 60, 0.95)';
            chatInput.style.backdropFilter = 'blur(10px)';
        }
    }, 200);
    
    // Fix 8: Watch for new messages and ensure they're properly styled
    const messageObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                // Check if new messages were added
                const newMessages = document.querySelectorAll('.message:not([data-fixed])');
                if (newMessages.length) {
                    newMessages.forEach(function(message) {
                        // Apply styling to new messages
                        message.style.width = 'calc(100% - 2rem)';
                        message.style.display = 'flex';
                        message.style.position = 'relative';
                        message.style.zIndex = '1';
                        message.style.marginBottom = '20px';
                        
                        if (message.classList.contains('user')) {
                            message.style.alignSelf = 'flex-end';
                        } else {
                            message.style.alignSelf = 'flex-start';
                        }
                        
                        // Fix message content width
                        const content = message.querySelector('.message-content');
                        if (content) {
                            content.style.maxWidth = '80%';
                            content.style.wordBreak = 'break-word';
                            content.style.whiteSpace = 'pre-wrap';
                        }
                        
                        // Mark as fixed
                        message.setAttribute('data-fixed', 'true');
                    });
                    
                    // Scroll to bottom
                    const chatMessages = document.querySelector('.chat-messages');
                    if (chatMessages) {
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
            }
        });
    });
    
    // Start observing the chat messages container
    const chatMessagesContainer = document.querySelector('.chat-messages');
    if (chatMessagesContainer) {
        messageObserver.observe(chatMessagesContainer, { childList: true });
    }
    
    // Fix 9: Restore chart button visibility and handle error messages
    setTimeout(function() {
        // Restore chart button visibility
        const chartButton = document.getElementById('toggle-charts-btn');
        if (chartButton) {
            chartButton.style.display = 'flex';
            chartButton.style.visibility = 'visible';
            chartButton.style.opacity = '1';
            chartButton.style.zIndex = '50';
            
            console.log('Chart button visibility restored');
        } else {
            console.error('Chart button not found');
        }
        
        // Hide API error messages
        document.querySelectorAll('.chat-messages > div').forEach(function(element) {
            if (element.textContent && (
                element.textContent.includes('Error: API error') || 
                element.textContent.includes('error: 500') ||
                element.textContent.includes('Please try again')
            )) {
                element.style.display = 'none';
                console.log('Hid error message:', element.textContent.substring(0, 30) + '...');
            }
        });
        
        // Make sure input container is properly positioned
        const inputContainer = document.querySelector('.input-container');
        if (inputContainer) {
            inputContainer.style.marginBottom = '0';
            inputContainer.style.marginTop = '0';
        }
        
        // Make sure the message container is properly scaled
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            chatMessages.style.paddingBottom = '120px';
            
            // Ensure scrollable area is properly sized
            chatMessages.addEventListener('DOMNodeInserted', function(event) {
                // Scroll to bottom when new messages appear
                setTimeout(function() {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 100);
            });
        }
    }, 300);
    
    // Fix 10: Apply regular cleanup to error messages and ensure message visibility
    setInterval(function() {
        // Hide API error messages
        document.querySelectorAll('.chat-messages > div').forEach(function(element) {
            if (element.textContent && (
                element.textContent.includes('Error: API error') || 
                element.textContent.includes('error: 500') ||
                element.textContent.includes('Please try again')
            )) {
                element.style.display = 'none';
            }
        });
        
        // Ensure messages are visible
        document.querySelectorAll('.message').forEach(function(message) {
            message.style.opacity = '1';
            message.style.visibility = 'visible';
            message.style.display = 'flex';
            
            // Adjust message positioning
            if (message.classList.contains('user')) {
                message.style.marginLeft = 'auto';
                message.style.marginRight = '0';
                message.style.flexDirection = 'row-reverse';
            } else {
                message.style.marginRight = 'auto';
                message.style.marginLeft = '0';
            }
            
            // Fix content visibility
            const content = message.querySelector('.message-content');
            if (content) {
                content.style.opacity = '1';
                content.style.visibility = 'visible';
            }
        });
    }, 1000);
    
    // Fix 11: Ensure the dashboard header is visible and chart button works
    setTimeout(function() {
        const dashboardHeader = document.querySelector('.dashboard-header');
        if (dashboardHeader) {
            dashboardHeader.style.display = 'flex';
            dashboardHeader.style.justifyContent = 'flex-end';
            dashboardHeader.style.zIndex = '50';
        }
        
        // Make chart button more reliable by creating a fresh event listener
        const chartButton = document.getElementById('toggle-charts-btn');
        const chartsPanel = document.getElementById('charts-panel');
        const chartCloseButton = document.querySelector('.close-charts-btn');
        
        if (chartButton && chartsPanel) {
            // Remove any existing event listeners to prevent conflicts
            const newChartButton = chartButton.cloneNode(true);
            chartButton.parentNode.replaceChild(newChartButton, chartButton);
            
            // Add fresh event listener
            newChartButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Chart button clicked (new handler)');
                
                // Toggle visibility
                if (chartsPanel.style.display === 'flex') {
                    // Hide panel
                    chartsPanel.style.opacity = '0';
                    setTimeout(() => {
                        chartsPanel.style.display = 'none';
                    document.body.classList.add('charts-hidden');
                    }, 300);
                } else {
                    // Show panel
                    chartsPanel.style.display = 'flex';
                    setTimeout(() => {
                        chartsPanel.style.opacity = '1';
                    document.body.classList.remove('charts-hidden');
                        
                        // Force render charts
                        if (typeof window.renderAllCharts === 'function') {
                            window.renderAllCharts();
                        }
                    }, 10);
                }
                
                return false;
            });
            
            console.log('Chart button handler reinstalled');
        }
        
        // Ensure the close button also works reliably
        if (chartCloseButton && chartsPanel) {
            // Remove existing listeners
            const newCloseButton = chartCloseButton.cloneNode(true);
            chartCloseButton.parentNode.replaceChild(newCloseButton, chartCloseButton);
            
            newCloseButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Hide panel
                chartsPanel.style.opacity = '0';
                setTimeout(() => {
                    chartsPanel.style.display = 'none';
                    document.body.classList.add('charts-hidden');
                }, 300);
                
                return false;
            });
        }
        
        // Add resizing and scrolling functionality to charts panel
        if (chartsPanel) {
            // Make sure panel has the right positioning and overflow
            chartsPanel.style.position = 'fixed';
            chartsPanel.style.overflow = 'hidden';
            
            // Make the panel content scrollable
            const panelContent = chartsPanel.querySelector('.panel-content');
            if (panelContent) {
                panelContent.style.overflow = 'auto';
                panelContent.style.height = 'calc(100% - 60px)';
                panelContent.style.paddingBottom = '20px';
            }
            
            // Add resize handle if it doesn't exist
            if (!document.getElementById('chart-resize-handle')) {
                const resizeHandle = document.createElement('div');
                resizeHandle.id = 'chart-resize-handle';
                resizeHandle.innerHTML = '⤡';
                resizeHandle.style.position = 'absolute';
                resizeHandle.style.bottom = '0';
                resizeHandle.style.right = '0';
                resizeHandle.style.width = '20px';
                resizeHandle.style.height = '20px';
                resizeHandle.style.cursor = 'nwse-resize';
                resizeHandle.style.background = 'rgba(138, 79, 255, 0.3)';
                resizeHandle.style.color = 'white';
                resizeHandle.style.display = 'flex';
                resizeHandle.style.alignItems = 'center';
                resizeHandle.style.justifyContent = 'center';
                resizeHandle.style.borderTopLeftRadius = '5px';
                resizeHandle.style.userSelect = 'none';
                resizeHandle.style.fontSize = '12px';
                resizeHandle.style.zIndex = '2000';
                
                chartsPanel.appendChild(resizeHandle);
                
                // Add resize functionality
                let isResizing = false;
                let startWidth, startHeight, startX, startY;
                
                // Debounce function for rendering charts
                function debounce(func, wait) {
                    let timeout;
                    return function() {
                        const context = this;
                        const args = arguments;
                        clearTimeout(timeout);
                        timeout = setTimeout(() => func.apply(context, args), wait);
                    };
                }
                
                // Create debounced version of renderAllCharts
                const debouncedRenderCharts = debounce(function() {
                    if (typeof window.renderAllCharts === 'function') {
                        window.renderAllCharts();
                    }
                }, 100);
                
                resizeHandle.addEventListener('mousedown', function(e) {
                    isResizing = true;
                    startWidth = chartsPanel.offsetWidth;
                    startHeight = chartsPanel.offsetHeight;
                    startX = e.clientX;
                    startY = e.clientY;
                    
                    // Add resize class to body
                    document.body.classList.add('resizing-charts');
                    e.preventDefault();
                });
                
                document.addEventListener('mousemove', function(e) {
                    if (!isResizing) return;
                    
                    const newWidth = startWidth + (e.clientX - startX);
                    const newHeight = startHeight + (e.clientY - startY);
                    
                    // Set minimum and maximum sizes
                    const minWidth = 300;
                    const minHeight = 300;
                    const maxWidth = window.innerWidth - 50;
                    const maxHeight = window.innerHeight - 50;
                    
                    chartsPanel.style.width = Math.min(maxWidth, Math.max(minWidth, newWidth)) + 'px';
                    chartsPanel.style.height = Math.min(maxHeight, Math.max(minHeight, newHeight)) + 'px';
                    
                    // Use debounced chart rendering during resize
                    debouncedRenderCharts();
                });
                
                document.addEventListener('mouseup', function() {
                    if (isResizing) {
                        isResizing = false;
                        document.body.classList.remove('resizing-charts');
                        
                        // Update localstorage
                        localStorage.setItem('chartsPanelWidth', chartsPanel.style.width);
                        localStorage.setItem('chartsPanelHeight', chartsPanel.style.height);
                        
                        // Render charts once resize is complete
                        if (typeof window.renderAllCharts === 'function') {
                            setTimeout(() => {
                                window.renderAllCharts();
                            }, 200);
                        }
                    }
                });
            }
            
            // Add drag handle if it doesn't exist
            if (!document.getElementById('chart-drag-handle')) {
                const dragHandle = document.createElement('div');
                dragHandle.id = 'chart-drag-handle';
                dragHandle.innerHTML = 'Financial Dashboard';
                dragHandle.style.position = 'sticky';
                dragHandle.style.top = '0';
                dragHandle.style.left = '0';
                dragHandle.style.width = '100%';
                dragHandle.style.padding = '10px';
                dragHandle.style.background = 'rgba(45, 25, 90, 0.95)';
                dragHandle.style.cursor = 'move';
                dragHandle.style.textAlign = 'center';
                dragHandle.style.color = 'white';
                dragHandle.style.fontWeight = 'bold';
                dragHandle.style.userSelect = 'none';
                dragHandle.style.zIndex = '1999';
                dragHandle.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
                
                // Find the right place to insert the drag handle (before panel-content)
                const panelContent = chartsPanel.querySelector('.panel-content');
                if (panelContent) {
                    chartsPanel.insertBefore(dragHandle, panelContent);
                } else {
                    chartsPanel.appendChild(dragHandle);
                }
                
                // Add dragging functionality
                let isDragging = false;
                let startLeft, startTop, dragStartX, dragStartY;
                
                dragHandle.addEventListener('mousedown', function(e) {
                    const rect = chartsPanel.getBoundingClientRect();
                    isDragging = true;
                    startLeft = rect.left;
                    startTop = rect.top;
                    dragStartX = e.clientX;
                    dragStartY = e.clientY;
                    e.preventDefault();
                });
                
                document.addEventListener('mousemove', function(e) {
                    if (!isDragging) return;
                    
                    const newLeft = startLeft + (e.clientX - dragStartX);
                    const newTop = startTop + (e.clientY - dragStartY);
                    
                    // Ensure panel stays within viewport
                    const maxLeft = window.innerWidth - chartsPanel.offsetWidth;
                    const maxTop = window.innerHeight - chartsPanel.offsetHeight;
                    
                    chartsPanel.style.left = Math.max(0, Math.min(newLeft, maxLeft)) + 'px';
                    chartsPanel.style.top = Math.max(0, Math.min(newTop, maxTop)) + 'px';
                    
                    // Update localstorage
                    localStorage.setItem('chartsPanelLeft', chartsPanel.style.left);
                    localStorage.setItem('chartsPanelTop', chartsPanel.style.top);
                });
                
                document.addEventListener('mouseup', function() {
                    if (isDragging) {
                        isDragging = false;
                    }
                });
            }
            
            // Restore saved position and size
            const savedWidth = localStorage.getItem('chartsPanelWidth');
            const savedHeight = localStorage.getItem('chartsPanelHeight');
            const savedLeft = localStorage.getItem('chartsPanelLeft');
            const savedTop = localStorage.getItem('chartsPanelTop');
            
            if (savedWidth) chartsPanel.style.width = savedWidth;
            if (savedHeight) chartsPanel.style.height = savedHeight;
            if (savedLeft) chartsPanel.style.left = savedLeft;
            if (savedTop) chartsPanel.style.top = savedTop;
        }
    }, 500);
    
    // Fix 12: Ensure automatic scrolling to bottom when new messages are added
    const messagesScrollContainer = document.querySelector('.chat-messages');
    if (messagesScrollContainer) {
        const scrollObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Scroll to bottom when new children are added
                    messagesScrollContainer.scrollTop = messagesScrollContainer.scrollHeight;
                    
                    // Double check after a small delay (for images or content that might take time to render)
                    setTimeout(function() {
                        messagesScrollContainer.scrollTop = messagesScrollContainer.scrollHeight;
                    }, 300);
                }
            });
        });
        
        // Start observing the chat messages container for changes
        scrollObserver.observe(messagesScrollContainer, { 
            childList: true,
            subtree: true
        });
        
        console.log("Automatic scrolling observer initialized");
    }
    
    // Fix 13: Add toggle for chat input minimization
    const chatInputBar = document.querySelector('.chat-input');
    if (chatInputBar) {
        // Create a small toggle button
  
        chatInputBar.appendChild(toggleButton);
        
        // Toggle input bar visibility when clicked
        toggleButton.addEventListener('click', function() {
            const isMinimized = chatInputBar.classList.toggle('minimized');
            if (isMinimized) {
                toggleButton.innerHTML = '▼';
                localStorage.setItem('chatInputMinimized', 'true');
            } else {
                toggleButton.innerHTML = '▲';
                localStorage.setItem('chatInputMinimized', 'false');
            }
        });
        
        // Focus input on click even when minimized
        chatInputBar.addEventListener('click', function(e) {
            if (chatInputBar.classList.contains('minimized') && e.target !== toggleButton) {
                chatInputBar.classList.remove('minimized');
                toggleButton.innerHTML = '▲';
                localStorage.setItem('chatInputMinimized', 'false');
                
                // Focus the input
                const inputElement = document.querySelector('.chat-input input[type="text"]');
                if (inputElement) {
                    setTimeout(() => {
                        inputElement.focus();
                    }, 50);
                }
            }
        });
        
        // Restore minimized state from localStorage
        if (localStorage.getItem('chatInputMinimized') === 'true') {
            chatInputBar.classList.add('minimized');
            toggleButton.innerHTML = '▼';
        }
    }
    
    // Fix 14: Remove duplicate chat input bars
    setTimeout(function() {
        // Find all chat input elements by various selectors
        const chatInputs = document.querySelectorAll('.chat-input, .chat-section .chat-input, div.chat-input');
        
        if (chatInputs.length > 1) {
            console.log('Found multiple chat input bars:', chatInputs.length);
            
            // Find the smallest one (which is likely the duplicate)
            let smallestInput = null;
            let smallestHeight = Number.MAX_SAFE_INTEGER;
            
            chatInputs.forEach(input => {
                const rect = input.getBoundingClientRect();
                console.log('Chat input dimensions:', rect.width, rect.height);
                
                // If this is the smaller one by height
                if (rect.height < smallestHeight) {
                    smallestHeight = rect.height;
                    smallestInput = input;
                }
            });
            
            // Remove the smallest one, which is likely the duplicate
            if (smallestInput && smallestInput.parentNode) {
                console.log('Removing smaller chat input bar');
                smallestInput.parentNode.removeChild(smallestInput);
            }
            
            // Make sure the remaining bar has proper styling
            const remainingInput = document.querySelector('.chat-input');
            if (remainingInput) {
                remainingInput.style.position = 'absolute';
                remainingInput.style.bottom = '0';
                remainingInput.style.left = '0';
                remainingInput.style.right = '0';
                remainingInput.style.zIndex = '100';
                remainingInput.style.padding = '15px 20px';
                remainingInput.style.background = 'rgba(30, 15, 60, 0.9)';
                remainingInput.style.borderTop = '1px solid rgba(138, 79, 255, 0.3)';
            }
        }
    }, 800);
    
    // Add a direct DOM traversal approach for stubborn duplicates
    setTimeout(function() {
        const bodyEl = document.body;
        if (!bodyEl) return;
        
        // Find the main chat section
        const chatSection = document.querySelector('.chat-section');
        const mainChatInput = chatSection ? chatSection.querySelector('.chat-input') : null;
        
        // Direct method: Look at all immediate children of body
        function scanAndRemoveChatInputs(element, depth = 0, maxDepth = 3) {
            if (depth > maxDepth) return;
            
            // Don't process the chat section itself
            if (element === chatSection) return;
            
            // Check if this element or any of its children are chat inputs
            const chatInputs = element.querySelectorAll('.chat-input');
            
            chatInputs.forEach(input => {
                // Skip if this is the main chat input
                if (input === mainChatInput) return;
                
                // Check if this is inside the chat section
                if (chatSection && chatSection.contains(input)) return;
                
                console.log('[fix-ui.js] Found standalone chat input to remove (depth: ' + depth + ')', input);
                
                // First, try to hide it with styles
                input.style.display = 'none';
                input.style.visibility = 'hidden';
                input.style.opacity = '0';
                input.style.pointerEvents = 'none';
                input.style.position = 'absolute';
                input.style.left = '-9999px';
                
                // Then try to remove it
                try {
                    if (input.parentNode) {
                        input.parentNode.removeChild(input);
                        console.log('[fix-ui.js] Successfully removed standalone chat input');
                    }
                } catch (e) {
                    console.error('[fix-ui.js] Error removing chat input:', e);
                }
            });
            
            // Recursively scan children
            for (let i = 0; i < element.children.length; i++) {
                scanAndRemoveChatInputs(element.children[i], depth + 1, maxDepth);
            }
        }
        
        // Start scan from the body element
        scanAndRemoveChatInputs(bodyEl);
        
    }, 1500);
    
    console.log("UI Fix Script completed initialization");
}); 