class AuthService {
    constructor() {
        this.baseUrl = 'http://localhost:8000/auth';
        this.tokenKey = 'galaxy_chat_token';
    }

    async login(username, password) {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${this.baseUrl}/token`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            this.setToken(data.access_token);
            return data;
        } catch (error) {
            throw error;
        }
    }

    async register(username, password) {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${this.baseUrl}/register`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    removeToken() {
        localStorage.removeItem(this.tokenKey);
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    logout() {
        this.removeToken();
        window.location.href = '/login.html';
    }
}

class UIManager {
    constructor(authService) {
        this.authService = authService;
        this.loginForm = document.getElementById('loginForm');
        this.tabs = document.querySelectorAll('.tab');
        this.formContainer = document.querySelector('.login-card');
        this.submitBtn = this.loginForm.querySelector('.submit-btn');
        
        this.setupEventListeners();
        this.checkAuthentication();
    }

    setupEventListeners() {
        // Tab switching
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => this.handleTabSwitch(tab));
        });

        // Form submission
        this.loginForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    handleTabSwitch(selectedTab) {
        this.tabs.forEach(tab => tab.classList.remove('active'));
        selectedTab.classList.add('active');

        const isLogin = selectedTab.textContent.toLowerCase() === 'login';
        this.updateFormForMode(isLogin);
    }

    updateFormForMode(isLogin) {
        const headerTitle = this.formContainer.querySelector('.login-header h1');
        const headerDesc = this.formContainer.querySelector('.login-header p');
        const forgotPassword = this.formContainer.querySelector('.forgot-password');

        if (isLogin) {
            headerTitle.textContent = 'Welcome Back';
            headerDesc.textContent = 'Enter your credentials to access your account';
            this.submitBtn.textContent = 'Login';
            forgotPassword.style.display = 'block';
        } else {
            headerTitle.textContent = 'Create Account';
            headerDesc.textContent = 'Sign up for a new Galaxy Chat account';
            this.submitBtn.textContent = 'Register';
            forgotPassword.style.display = 'none';
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const isLogin = this.formContainer.querySelector('.tab.active').textContent.toLowerCase() === 'login';
        const username = this.loginForm.querySelector('input[type="email"]').value;
        const password = this.loginForm.querySelector('input[type="password"]').value;

        try {
            this.showLoading();

            if (isLogin) {
                await this.authService.login(username, password);
                this.showMessage('Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = '/chatpage.html';
                }, 1500);
            } else {
                await this.authService.register(username, password);
                this.showMessage('Registration successful! Please login.', 'success');
                setTimeout(() => {
                    this.tabs[0].click(); // Switch to login tab
                }, 1500);
            }
        } catch (error) {
            this.showMessage(error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showMessage(message, type = 'error') {
        const existingMessage = this.formContainer.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        this.loginForm.insertBefore(messageElement, this.loginForm.firstChild);

        setTimeout(() => messageElement.remove(), 5000);
    }

    showLoading() {
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<span class="loading"></span>';
    }

    hideLoading() {
        this.submitBtn.disabled = false;
        const isLogin = this.formContainer.querySelector('.tab.active').textContent.toLowerCase() === 'login';
        this.submitBtn.textContent = isLogin ? 'Login' : 'Register';
    }

    checkAuthentication() {
        if (this.authService.isAuthenticated() && window.location.pathname.includes('login.html')) {
            window.location.href = '/chatpage.html';
        }
    }
}

// Initialize the auth service and UI manager
const authService = new AuthService();
const uiManager = new UIManager(authService);

// Add styles for messages and loading
const style = document.createElement('style');
style.textContent = `
    .message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }

    .message.error {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid rgba(255, 0, 0, 0.2);
        color: #ff6b6b;
    }

    .message.success {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid rgba(0, 255, 0, 0.2);
        color: #51cf66;
    }

    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style); 