class MainPageManager {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.checkAuthentication();
        this.startAnimations();
    }

    initializeElements() {
        // Navigation elements
        this.navLinks = document.querySelectorAll('.nav-links a');
        this.primaryButton = document.querySelector('.primary-button');
        this.secondaryButton = document.querySelector('.secondary-button');
        
        // Animation elements
        this.heroTitle = document.querySelector('.hero h1');
        this.heroDescription = document.querySelector('.hero p');
        this.featureCards = document.querySelectorAll('.feature-card');
        
        // Stars background
        this.createStarryBackground();
    }

    setupEventListeners() {
        // Smooth scroll for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Button hover animations
        [this.primaryButton, this.secondaryButton].forEach(button => {
            if (button) {
                button.addEventListener('mouseenter', () => {
                    button.style.transform = 'translateY(-2px)';
                });

                button.addEventListener('mouseleave', () => {
                    button.style.transform = 'translateY(0)';
                });
            }
        });

        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });

        // Observe feature cards
        this.featureCards.forEach(card => {
            card.classList.add('fade-in');
            observer.observe(card);
        });

        // Set up file upload form if needed
        if (this.primaryButton) {
            this.primaryButton.addEventListener('click', (e) => {
                // Check if we already have a project context
                const projectId = localStorage.getItem('chatProjectId');
                if (!projectId) {
                    // We don't have a project yet, show upload dialog
                    e.preventDefault();
                    this.showUploadDialog();
                }
                // If we have a project, just follow the normal link to chatpage.html
            });
        }
    }

    createStarryBackground() {
        const starsContainer = document.createElement('div');
        starsContainer.className = 'stars-container';
        document.body.appendChild(starsContainer);

        // Create multiple layers of stars
        for (let i = 0; i < 3; i++) {
            const starsLayer = document.createElement('div');
            starsLayer.className = `stars-layer stars-layer-${i + 1}`;
            
            // Create random stars
            for (let j = 0; j < 50; j++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = `${Math.random() * 100}%`;
                star.style.top = `${Math.random() * 100}%`;
                star.style.animationDelay = `${Math.random() * 3}s`;
                starsLayer.appendChild(star);
            }
            
            starsContainer.appendChild(starsLayer);
        }
    }

    startAnimations() {
        // Add initial animations
        if (this.heroTitle) {
            this.heroTitle.classList.add('slide-in-left');
        }
        if (this.heroDescription) {
            this.heroDescription.classList.add('slide-in-right');
        }

        // Animate navigation links
        this.navLinks.forEach((link, index) => {
            link.style.animationDelay = `${index * 0.1}s`;
            link.classList.add('fade-in-down');
        });
    }

    checkAuthentication() {
        const token = localStorage.getItem('galaxy_chat_token');
        
        if (token) {
            // Update primary button to go directly to chat
            if (this.primaryButton) {
                this.primaryButton.href = '/chatpage.html';
                this.primaryButton.textContent = 'Continue Chatting 🚀';
            }
            // Hide secondary (login) button
            if (this.secondaryButton) {
                this.secondaryButton.style.display = 'none';
            }
            // Update nav buttons
            document.querySelectorAll('.auth-button').forEach(button => {
                if (button.classList.contains('login')) {
                    button.textContent = 'Go to Chat';
                    button.href = '/chatpage.html';
                } else {
                    button.style.display = 'none';
                }
            });
        }
    }

    showUploadDialog() {
        // Create modal element
        const modal = document.createElement('div');
        modal.className = 'upload-modal';
        modal.innerHTML = `
            <div class="upload-dialog">
                <h3>Upload a Document</h3>
                <p>Please upload a document to start chatting with Farqad</p>
                <form id="upload-form">
                    <div class="file-input-container">
                        <input type="file" id="fileInput" name="file" accept=".pdf,.txt,.csv,.xlsx,.docx">
                        <label for="fileInput">Choose File</label>
                    </div>
                    <div id="upload-status"></div>
                    <div class="dialog-buttons">
                        <button type="button" class="cancel-button">Cancel</button>
                        <button type="submit" class="upload-button">Upload & Start</button>
                    </div>
                </form>
            </div>
        `;
        
        // Add styles for the modal
        const style = document.createElement('style');
        style.textContent = `
            .upload-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(10, 4, 20, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .upload-dialog {
                background: rgba(35, 16, 68, 0.95);
                border: 1px solid rgba(147, 51, 234, 0.3);
                border-radius: 12px;
                padding: 2rem;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            .upload-dialog h3 {
                margin-top: 0;
                color: #E464FF;
                margin-bottom: 1rem;
            }
            
            .upload-dialog p {
                margin-bottom: 1.5rem;
                color: rgba(255, 255, 255, 0.9);
            }
            
            .file-input-container {
                margin-bottom: 1.5rem;
                position: relative;
            }
            
            .file-input-container input[type="file"] {
                position: absolute;
                width: 0.1px;
                height: 0.1px;
                opacity: 0;
                overflow: hidden;
                z-index: -1;
            }
            
            .file-input-container label {
                display: block;
                padding: 1rem;
                background: rgba(147, 51, 234, 0.1);
                border: 1px dashed rgba(147, 51, 234, 0.5);
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .file-input-container label:hover {
                background: rgba(147, 51, 234, 0.2);
            }
            
            #upload-status {
                min-height: 24px;
                margin-bottom: 1.5rem;
                text-align: center;
                font-size: 0.9rem;
            }
            
            .dialog-buttons {
                display: flex;
                justify-content: flex-end;
                gap: 1rem;
            }
            
            .cancel-button {
                padding: 0.6rem 1.2rem;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
                cursor: pointer;
            }
            
            .upload-button {
                padding: 0.6rem 1.2rem;
                background: #7E22CE;
                border: none;
                border-radius: 6px;
                color: white;
                cursor: pointer;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        // Add event listeners
        const cancelButton = modal.querySelector('.cancel-button');
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // The upload itself is handled by upload.js
    }
}

// Add required styles
const style = document.createElement('style');
style.textContent = `
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease-out, transform 0.6s ease-out;
    }

    .fade-in.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .slide-in-left {
        animation: slideInLeft 1s ease-out forwards;
    }

    .slide-in-right {
        animation: slideInRight 1s ease-out forwards;
    }

    .fade-in-down {
        animation: fadeInDown 0.5s ease-out forwards;
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stars-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }

    .stars-layer {
        position: absolute;
        width: 100%;
        height: 100%;
    }

    .star {
        position: absolute;
        width: 2px;
        height: 2px;
        background: white;
        border-radius: 50%;
        animation: twinkle 2s infinite;
    }

    .stars-layer-2 .star {
        width: 3px;
        height: 3px;
    }

    .stars-layer-3 .star {
        width: 1px;
        height: 1px;
    }

    @keyframes twinkle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
`;
document.head.appendChild(style);

// Initialize the main page manager
document.addEventListener('DOMContentLoaded', () => {
    new MainPageManager();
}); 