// Upload.js - Handles file upload functionality and notifications

// Function to handle file upload completion
function notifyFileUploaded(projectId) {
    console.log(`File uploaded successfully. Project ID: ${projectId}`);
    
    // Store the project ID in localStorage for chat
    localStorage.setItem('chatProjectId', projectId);
    
    // Also set the chat mode to document mode
    localStorage.setItem('chatMode', 'document');
    console.log(`[upload.js] Set chatMode to 'document' in localStorage`);
    
    // Update global variables if they're available in the window context
    if (typeof window.currentChatProjectId !== 'undefined') {
        window.currentChatProjectId = projectId;
        console.log(`[upload.js] Updated global currentChatProjectId to: ${projectId}`);
    }
    
    if (typeof window.currentChatMode !== 'undefined') {
        window.currentChatMode = 'document';
        console.log(`[upload.js] Updated global currentChatMode to: 'document'`);
    }
    
    // Trigger a custom event for file upload completion
    const event = new CustomEvent('fileUploaded', { 
        detail: { 
            projectId: projectId 
        } 
    });
    window.dispatchEvent(event);
    
    // Force document list refresh
    if (typeof window.loadDocuments === 'function') {
        setTimeout(() => {
            console.log("[upload.js] Refreshing document list after upload");
            window.loadDocuments();
        }, 1000); // Small delay to ensure backend processing is complete
    }
    
    // Reload page if we're on the chat page to ensure context is properly applied
    if (window.location.pathname.includes('chatpage.html')) {
        console.log(`[upload.js] We're on the chat page. Scheduling a context reload.`);
        // Don't reload page, just force a context refresh
        setTimeout(() => {
            console.log(`[upload.js] Refreshing chat context for newly uploaded document`);
            if (typeof window.loadContextFromStorage === 'function') {
                window.loadContextFromStorage();
                console.log(`[upload.js] Context refresh complete.`);
            }
            
            // Force update of chat mode indicator
            if (typeof window.updateChatModeIndicator === 'function') {
                window.updateChatModeIndicator();
                console.log(`[upload.js] Chat mode indicator updated to reflect document mode.`);
            }
        }, 1500);
    }
}

// Initialize upload functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log("Upload.js: Initializing file upload handling");
    
    // Get file input element
    const fileInput = document.getElementById('file-upload');
    
    // Log if the file input was found
    if (fileInput) {
        console.log("File input found with ID 'file-upload'");
        
        // Add change event listener to handle file selection
        fileInput.addEventListener('change', function(event) {
            console.log('File input changed, handling upload...');
            handleFileUpload(event.target);
        });
        
        // Mark the input with flag to confirm initialization
        fileInput._hasChangeListener = true;
        console.log("Added change event listener to file input");
    } else {
        console.error("File input not found with ID 'file-upload'");
    }
    
    // Create a direct handler for the file upload label/button
    const uploadButton = document.querySelector('.upload-button');
    if (uploadButton) {
        console.log("Upload button/label found");
        uploadButton.addEventListener('click', function() {
            console.log("Upload button clicked, triggering file dialog");
        });
    }
});

// Function to handle file upload
async function handleFileUpload(inputElement) {
    if (!inputElement || !inputElement.files || inputElement.files.length === 0) {
        console.log('No file selected');
        return;
    }
    
    const file = inputElement.files[0];
    console.log(`Selected file: ${file.name} (${file.size} bytes)`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Generate a unique project ID
    const projectId = 'proj_' + Math.random().toString(36).substr(2, 9);
    console.log(`Generated project ID for upload: ${projectId}`);
    
    try {
        console.log(`Uploading file ${file.name} to project ${projectId}...`);
        
        // Show toast notification if available
        if (window.showToast) {
            window.showToast(`Uploading ${file.name}...`, 'info');
        }
        
        const response = await fetch(`/api/v1/data/upload/${projectId}`, {
            method: 'POST',
            body: formData
        });
        
        console.log(`Upload response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Upload successful, response:', data);
        
        // Get actual file and project IDs from response
        const actualProjectId = data.project_id || projectId;
        const fileId = data.file_id;
        
        // Notify about file upload completion
        notifyFileUploaded(actualProjectId);
        
        // Add a message to the chat about successful upload
        if (typeof window.addMessage === 'function') {
            const successMsg = `File "${file.name}" has been successfully uploaded. You can now ask questions about this document.`;
            window.addMessage(successMsg, false);
            console.log(`[upload.js] Added upload success message to chat`);
        }
        
        // Automatically focus on the uploaded document
        if (typeof window.focusOnDocument === 'function' && fileId) {
            console.log(`Auto-focusing on uploaded document: ${fileId}, filename: ${file.name}`);
            window.focusOnDocument(fileId, file.name);
            
            // Show toast notification of focus
            if (window.showToast) {
                window.showToast(`Now focusing on ${file.name}`, 'success');
            }
        } else {
            console.warn('Could not auto-focus on document - missing function or file ID');
        }
        
        // Clear the file input
        inputElement.value = '';
        
        // Show toast notification if available
        if (window.showToast) {
            window.showToast(`File uploaded successfully: ${file.name}`, 'success');
        }
    } catch (error) {
        console.error('Upload error:', error);
        
        // Show toast notification if available
        if (window.showToast) {
            window.showToast(`Upload failed: ${error.message}`, 'error');
        }
        
        // Add error message to chat if possible - with safer implementation
        try {
            if (typeof window.addMessage === 'function') {
                const errorMsg = `Failed to upload "${file.name}". Please try again.`;
                window.addMessage(errorMsg, false);
            }
        } catch (messageError) {
            console.error('Error adding message to chat:', messageError);
        }
        
        // Clear the file input
        inputElement.value = '';
    }
}

// Utility function to load STC.pdf automatically for testing
window.loadStcPdf = function() {
    // Create a fake file object for STC.pdf
    const stcBlob = new Blob(['STC PDF content simulation'], { type: 'application/pdf' });
    const stcFile = new File([stcBlob], 'STC.pdf', { type: 'application/pdf' });
    
    // Create a FormData object
    const formData = new FormData();
    formData.append('file', stcFile);
    
    // Generate a specific project ID for STC
    const projectId = 'stc-project-0';
    
    // Show loading indicator
    if (window.showToast) {
        window.showToast(`Loading STC.pdf document...`, 'info');
    }
    
    console.log(`[loadStcPdf] Creating STC document with project ID: ${projectId}`);
    
    // Directly call the backend test endpoint
    fetch(`/api/v1/debug/load-stc?project_id=${projectId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load STC.pdf: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('[loadStcPdf] STC.pdf loaded successfully:', data);
            
            // Store project ID
            localStorage.setItem('chatProjectId', projectId);
            
            // Focus on the STC document
            if (typeof window.focusOnDocument === 'function') {
                window.focusOnDocument('stc-doc-12345', 'STC.pdf');
            }
            
            // Show success notification
            if (window.showToast) {
                window.showToast('STC.pdf loaded successfully', 'success');
            }
            
            // Refresh document list
            if (typeof window.loadDocuments === 'function') {
                window.loadDocuments();
            }
        })
        .catch(error => {
            console.error('[loadStcPdf] Error loading STC.pdf:', error);
            
            // Show error notification
            if (window.showToast) {
                window.showToast(`Error loading STC.pdf: ${error.message}`, 'error');
            }
            
            // Fallback to normal focus
            if (typeof window.focusOnDocument === 'function') {
                window.focusOnDocument('stc-doc-12345', 'STC.pdf');
                
                if (window.showToast) {
                    window.showToast('Using built-in STC.pdf document instead', 'info');
                }
            }
        });
}; 