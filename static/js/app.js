// CiviX Frontend JavaScript

// Global app object
const CiviX = {
    init() {
        this.setupEventListeners();
        this.updateTimestamps();
    },

    setupEventListeners() {
        // Auto-refresh functionality
        const refreshButtons = document.querySelectorAll('[data-refresh]');
        refreshButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.refreshPage();
            });
        });

        // API status checker
        this.checkApiStatus();

        // Set up periodic status check
        setInterval(() => {
            this.checkApiStatus();
        }, 30000); // Check every 30 seconds
    },

    async checkApiStatus() {
        try {
            const response = await fetch('/api/hello');
            const data = await response.json();

            // Update status indicator if exists
            const statusIndicator = document.querySelector('.navbar-text .bi-circle-fill');
            if (statusIndicator) {
                statusIndicator.className = 'bi bi-circle-fill text-success';
            }
        } catch (error) {
            console.error('API status check failed:', error);

            const statusIndicator = document.querySelector('.navbar-text .bi-circle-fill');
            if (statusIndicator) {
                statusIndicator.className = 'bi bi-circle-fill text-danger';
            }
        }
    },

    refreshPage() {
        // Add loading state
        document.body.classList.add('loading');

        // Reload after short delay for UX
        setTimeout(() => {
            location.reload();
        }, 500);
    },

    updateTimestamps() {
        // Update any relative timestamps
        const timestamps = document.querySelectorAll('[data-timestamp]');
        timestamps.forEach(element => {
            const timestamp = element.getAttribute('data-timestamp');
            const date = new Date(timestamp);
            element.textContent = this.formatRelativeTime(date);
        });
    },

    formatRelativeTime(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return 'agora mesmo';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minuto${minutes > 1 ? 's' : ''} atrás`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hora${hours > 1 ? 's' : ''} atrás`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} dia${days > 1 ? 's' : ''} atrás`;
        }
    },

    // Utility function for API calls
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API call to ${endpoint} failed:`, error);
            throw error;
        }
    },

    // Show notification (using Bootstrap toast if available)
    showNotification(message, type = 'info') {
        // Simple alert fallback
        if (type === 'error') {
            alert(`Erro: ${message}`);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    CiviX.init();
});

// Export for potential use in other scripts
window.CiviX = CiviX;
