/**
 * Chat Application JavaScript
 * Handles real-time features and UI interactions
 */

class ChatApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupRealTimeUpdates();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // Auto-resize textareas
        this.setupAutoResize();

        // Confirm delete actions
        this.setupConfirmations();

        // Keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Message input enhancements
        this.setupMessageInput();
    }

    setupAutoResize() {
        // Auto-resize textareas
        document.addEventListener('input', function(e) {
            if (e.target.tagName.toLowerCase() === 'textarea') {
                e.target.style.height = 'auto';
                e.target.style.height = (e.target.scrollHeight) + 'px';
            }
        });
    }

    setupConfirmations() {
        // Add confirmation to delete buttons
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('delete-btn') ||
                e.target.closest('.delete-btn')) {

                if (!confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    setupKeyboardShortcuts() {
        // Ctrl+Enter to send message
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const messageForm = document.getElementById('message-form');
                if (messageForm) {
                    e.preventDefault();
                    messageForm.dispatchEvent(new Event('submit'));
                }
            }
        });

        // Escape to close modals
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                });
            }
        });
    }

    setupMessageInput() {
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            // Character counter
            this.setupCharacterCounter(messageInput);

            // Typing indicator (placeholder for future real-time feature)
            this.setupTypingIndicator(messageInput);
        }
    }

    setupCharacterCounter(input) {
        const maxLength = input.getAttribute('maxlength') || 1000;
        const counter = document.createElement('small');
        counter.className = 'text-muted position-absolute';
        counter.style.bottom = '5px';
        counter.style.right = '80px';
        counter.style.fontSize = '0.75rem';

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - input.value.length;
            counter.textContent = `${remaining} characters left`;
            counter.style.color = remaining < 50 ? '#dc3545' : '#6c757d';
        }

        input.addEventListener('input', updateCounter);
        updateCounter(); // Initial call
    }

    setupTypingIndicator(input) {
        let typingTimer;
        const typingDelay = 1000; // 1 second delay

        input.addEventListener('input', function() {
            clearTimeout(typingTimer);

            // Show typing indicator
            const indicator = document.querySelector('.typing-indicator');
            if (indicator) {
                indicator.classList.add('show');
            }

            // Hide typing indicator after delay
            typingTimer = setTimeout(function() {
                const indicator = document.querySelector('.typing-indicator');
                if (indicator) {
                    indicator.classList.remove('show');
                }
            }, typingDelay);
        });
    }

    setupRealTimeUpdates() {
        // Set up periodic updates for new messages
        this.startMessagePolling();

        // Handle page visibility changes
        this.setupPageVisibility();
    }

    startMessagePolling() {
        // Poll for new messages every 5 seconds
        setInterval(() => {
            if (!document.hidden) {
                this.checkForNewMessages();
            }
        }, 5000);
    }

    checkForNewMessages() {
        // This would check for new messages via AJAX
        // For now, just a placeholder
        console.log('Checking for new messages...');
    }

    setupPageVisibility() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.onPageHidden();
            } else {
                this.onPageVisible();
            }
        });
    }

    onPageHidden() {
        // Pause real-time updates when page is not visible
        console.log('Page hidden - pausing updates');
    }

    onPageVisible() {
        // Resume real-time updates when page becomes visible
        console.log('Page visible - resuming updates');
        this.checkForNewMessages(); // Immediate check
    }

    showWelcomeMessage() {
        // Show welcome toast or notification
        const welcomeToast = document.createElement('div');
        welcomeToast.className = 'toast align-items-center text-white bg-success border-0 position-fixed';
        welcomeToast.style.top = '20px';
        welcomeToast.style.right = '20px';
        welcomeToast.style.zIndex = '9999';
        welcomeToast.setAttribute('role', 'alert');

        welcomeToast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>
                    Welcome to ChatApp! Enjoy your conversation.
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(welcomeToast);

        const bsToast = new bootstrap.Toast(welcomeToast);
        bsToast.show();

        // Remove toast after it's hidden
        welcomeToast.addEventListener('hidden.bs.toast', () => {
            welcomeToast.remove();
        });
    }

    // Utility methods
    static formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static showNotification(title, message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';

        notification.innerHTML = `
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    static copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Copied!', 'Text copied to clipboard', 'success');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('Copied!', 'Text copied to clipboard', 'success');
        }
    }
}

// Utility functions for AJAX requests
function ajaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        body: null,
    };

    const config = { ...defaultOptions, ...options };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX Error:', error);
            ChatApp.showNotification('Error', 'Failed to complete request', 'danger');
            throw error;
        });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatApp = new ChatApp();

    // Add copy functionality to message IDs
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-id') ||
            e.target.closest('.copy-id')) {
            const element = e.target.classList.contains('copy-id') ?
                          e.target : e.target.closest('.copy-id');
            const textToCopy = element.dataset.copyText || element.textContent;
            ChatApp.copyToClipboard(textToCopy);
        }
    });

    // Add tooltips to elements with data-bs-toggle="tooltip"
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Export for use in other scripts
window.ChatApp = ChatApp;
window.ajaxRequest = ajaxRequest;
