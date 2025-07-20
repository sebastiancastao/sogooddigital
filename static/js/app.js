/**
 * Custom JavaScript for Google Scholar Research Agent
 */

// Global application object
const ResearchAgent = {
    // Configuration
    config: {
        socketRetryAttempts: 3,
        socketRetryDelay: 1000,
        pollInterval: 2000,
        maxLogEntries: 100
    },
    
    // State management
    state: {
        isConnected: false,
        currentTaskId: null,
        lastUpdate: null,
        logs: []
    },
    
    // Initialize the application
    init: function() {
        console.log('🚀 Research Agent initialized');
        this.setupEventListeners();
        this.setupFormValidation();
        this.initializeAnimations();
    },
    
    // Setup global event listeners
    setupEventListeners: function() {
        // Global error handling
        window.addEventListener('error', this.handleGlobalError.bind(this));
        
        // Network status monitoring
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
        
        // Visibility change handling
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboard.bind(this));
    },
    
    // Setup form validation
    setupFormValidation: function() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.validateForm.bind(this));
        });
        
        // Real-time input validation
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateInput.bind(this));
            input.addEventListener('input', this.handleInputChange.bind(this));
        });
    },
    
    // Initialize animations
    initializeAnimations: function() {
        // Fade in elements on scroll
        this.setupScrollAnimations();
        
        // Loading animations
        this.setupLoadingAnimations();
        
        // Card hover effects
        this.setupCardEffects();
    },
    
    // Form validation
    validateForm: function(event) {
        const form = event.target;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateInput({ target: input })) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            this.showNotification('Please fill in all required fields correctly', 'error');
        }
        
        return isValid;
    },
    
    // Input validation
    validateInput: function(event) {
        const input = event.target;
        const value = input.value.trim();
        let isValid = true;
        let message = '';
        
        // Remove existing validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Required field validation
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required';
        }
        
        // Specific validation rules
        switch (input.type) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    isValid = false;
                    message = 'Please enter a valid email address';
                }
                break;
                
            case 'url':
                if (value && !this.isValidUrl(value)) {
                    isValid = false;
                    message = 'Please enter a valid URL';
                }
                break;
        }
        
        // Google File ID validation
        if (input.name === 'google_file_id' && value) {
            if (!this.isValidGoogleFileId(value)) {
                isValid = false;
                message = 'Please enter a valid Google File ID';
            }
        }
        
        // Apply validation styles
        input.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Show/hide validation message
        this.showInputValidation(input, message, isValid);
        
        return isValid;
    },
    
    // Handle input changes
    handleInputChange: function(event) {
        const input = event.target;
        
        // Auto-format Google File ID
        if (input.name === 'google_file_id') {
            this.formatGoogleFileId(input);
        }
        
        // Character counter for textareas
        if (input.tagName === 'TEXTAREA') {
            this.updateCharacterCounter(input);
        }
    },
    
    // Validation helper functions
    isValidEmail: function(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },
    
    isValidUrl: function(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    isValidGoogleFileId: function(fileId) {
        // Google File IDs are typically 25-50 characters long
        // and contain alphanumeric characters, hyphens, and underscores
        const regex = /^[a-zA-Z0-9_-]{10,}$/;
        return regex.test(fileId) && fileId.length >= 10;
    },
    
    // Format Google File ID input
    formatGoogleFileId: function(input) {
        let value = input.value.trim();
        
        // Extract file ID from full Google URL
        if (value.includes('docs.google.com') || value.includes('drive.google.com')) {
            const match = value.match(/\/d\/([a-zA-Z0-9_-]+)/);
            if (match) {
                input.value = match[1];
                this.showNotification('File ID extracted from URL', 'success');
            }
        }
    },
    
    // Show input validation message
    showInputValidation: function(input, message, isValid) {
        let feedback = input.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        
        if (message) {
            if (!feedback) {
                feedback = document.createElement('div');
                input.parentNode.appendChild(feedback);
            }
            
            feedback.className = isValid ? 'valid-feedback' : 'invalid-feedback';
            feedback.textContent = message;
            feedback.style.display = 'block';
        } else if (feedback) {
            feedback.style.display = 'none';
        }
    },
    
    // Update character counter
    updateCharacterCounter: function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        if (!maxLength) return;
        
        const currentLength = textarea.value.length;
        let counter = textarea.parentNode.querySelector('.character-counter');
        
        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'character-counter text-muted small mt-1';
            textarea.parentNode.appendChild(counter);
        }
        
        counter.textContent = `${currentLength}/${maxLength} characters`;
        
        if (currentLength > maxLength * 0.9) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.remove('text-warning');
        }
    },
    
    // Show notification
    showNotification: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 350px;';
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove notification
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 150);
            }
        }, duration);
        
        return notification;
    },
    
    // Get notification icon
    getNotificationIcon: function(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    },
    
    // Setup scroll animations
    setupScrollAnimations: function() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });
        
        // Observe cards and other elements
        document.querySelectorAll('.card, .alert, .hero-section').forEach(el => {
            observer.observe(el);
        });
    },
    
    // Setup loading animations
    setupLoadingAnimations: function() {
        // Animate progress bars
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    },
    
    // Setup card effects
    setupCardEffects: function() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    },
    
    // Handle global errors
    handleGlobalError: function(event) {
        console.error('Global error:', event.error);
        this.showNotification('An unexpected error occurred', 'error');
    },
    
    // Handle online status
    handleOnline: function() {
        this.showNotification('Connection restored', 'success');
    },
    
    // Handle offline status
    handleOffline: function() {
        this.showNotification('Connection lost - some features may not work', 'warning');
    },
    
    // Handle visibility change
    handleVisibilityChange: function() {
        if (document.hidden) {
            console.log('Page hidden');
        } else {
            console.log('Page visible');
            // Refresh status if on progress page
            if (window.location.pathname.includes('/progress/')) {
                this.refreshProgressStatus();
            }
        }
    },
    
    // Handle keyboard shortcuts
    handleKeyboard: function(event) {
        // Ctrl/Cmd + Enter to submit forms
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const form = event.target.closest('form');
            if (form) {
                form.submit();
            }
        }
        
        // ESC to close modals/notifications
        if (event.key === 'Escape') {
            document.querySelectorAll('.alert .btn-close').forEach(btn => btn.click());
        }
    },
    
    // Refresh progress status (for progress page)
    refreshProgressStatus: function() {
        const taskId = this.state.currentTaskId;
        if (!taskId) return;
        
        fetch(`/api/status/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (window.updateProgress && typeof window.updateProgress === 'function') {
                    window.updateProgress(data);
                }
            })
            .catch(error => {
                console.error('Error refreshing status:', error);
            });
    },
    
    // Utility functions
    utils: {
        // Format date
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString();
        },
        
        // Format file size
        formatFileSize: function(bytes) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            if (bytes === 0) return '0 Bytes';
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        },
        
        // Copy to clipboard
        copyToClipboard: function(text) {
            return navigator.clipboard.writeText(text).then(() => {
                ResearchAgent.showNotification('Copied to clipboard', 'success');
                return true;
            }).catch(err => {
                console.error('Failed to copy:', err);
                ResearchAgent.showNotification('Failed to copy to clipboard', 'error');
                return false;
            });
        },
        
        // Download blob as file
        downloadBlob: function(blob, filename) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        },
        
        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Throttle function
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    ResearchAgent.init();
});

// Make ResearchAgent available globally
window.ResearchAgent = ResearchAgent; 