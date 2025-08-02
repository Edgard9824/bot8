// Real-time updates for the trading bot dashboard
class TradingBotDashboard {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.isUpdating = false;
        this.init();
    }

    init() {
        // Start real-time updates
        this.startUpdates();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Initialize tooltips
        this.initTooltips();
    }

    setupEventListeners() {
        // Auto-refresh toggle
        const refreshToggle = document.getElementById('autoRefresh');
        if (refreshToggle) {
            refreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startUpdates();
                } else {
                    this.stopUpdates();
                }
            });
        }

        // Manual refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.updateStatus();
            });
        }

        // Settings form validation
        const settingsForm = document.querySelector('form[action*="update_settings"]');
        if (settingsForm) {
            settingsForm.addEventListener('submit', this.validateSettings);
        }
    }

    startUpdates() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        this.updateStatus();
        this.updateTimer = setInterval(() => {
            this.updateStatus();
        }, this.updateInterval);
    }

    stopUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        this.isUpdating = false;
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            this.updateUI(data);
            
        } catch (error) {
            console.error('Error updating status:', error);
            this.showError('Failed to update status');
        }
    }

    updateUI(data) {
        // Update status indicator
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = statusIndicator?.nextSibling;
        
        if (statusIndicator && statusText) {
            statusIndicator.className = `status-indicator ${data.running ? 'online' : 'offline'}`;
            statusText.textContent = data.running ? ' ONLINE' : ' OFFLINE';
        }

        // Update signal count
        const signalCount = document.getElementById('signalCount');
        if (signalCount) {
            signalCount.textContent = data.signal_count || 0;
        }

        // Update winrate
        const winrate = document.getElementById('winrate');
        if (winrate) {
            winrate.textContent = `${data.winrate?.toFixed(1) || 0}%`;
        }

        // Update button state
        const toggleBtn = document.querySelector('button[type="submit"]');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (data.running) {
                toggleBtn.className = 'btn btn-danger btn-lg w-100 mb-3';
                toggleBtn.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Bot';
            } else {
                toggleBtn.className = 'btn btn-success btn-lg w-100 mb-3';
                toggleBtn.innerHTML = '<i class="bi bi-play-circle"></i> Start Bot';
            }
        }

        // Update latest signal if available
        if (data.latest_signal && Object.keys(data.latest_signal).length > 0) {
            this.updateLatestSignal(data.latest_signal);
        }
    }

    updateLatestSignal(signal) {
        const latestSignalCard = document.querySelector('.latest-signal');
        if (!latestSignalCard) return;

        // Update signal data
        const pairElement = latestSignalCard.querySelector('.signal-pair');
        const timeElement = latestSignalCard.querySelector('.signal-time');
        const directionElement = latestSignalCard.querySelector('.signal-direction');
        const arrowElement = latestSignalCard.querySelector('.signal-arrow');
        const typeElement = latestSignalCard.querySelector('.signal-type');
        const confidenceElement = latestSignalCard.querySelector('.confidence-circle');

        if (pairElement) pairElement.textContent = signal.pair;
        if (timeElement) timeElement.textContent = signal.timestamp;
        if (arrowElement) arrowElement.textContent = signal.arrow;
        if (typeElement) typeElement.textContent = signal.direction;
        if (confidenceElement) confidenceElement.textContent = `${signal.confidence}%`;

        // Update direction styling
        if (directionElement) {
            directionElement.className = `signal-direction ${signal.direction === 'CALL' ? 'call' : 'put'}`;
        }

        // Update indicators
        const indicators = latestSignalCard.querySelectorAll('.indicator span');
        if (indicators.length >= 3) {
            indicators[0].textContent = signal.rsi;
            indicators[1].textContent = `${signal.stoch_k}/${signal.stoch_d}`;
            indicators[2].textContent = signal.trend;
        }

        // Add pulse animation
        latestSignalCard.style.animation = 'none';
        setTimeout(() => {
            latestSignalCard.style.animation = 'pulse 2s infinite';
        }, 10);
    }

    validateSettings(event) {
        const form = event.target;
        const chatId = form.querySelector('input[name="telegram_chat_id"]').value;
        const selectedPairs = form.querySelectorAll('input[name="pairs"]:checked');

        // Validate chat ID format (basic check)
        if (chatId && !/^-?\d+$/.test(chatId)) {
            alert('Please enter a valid Telegram Chat ID (numbers only)');
            event.preventDefault();
            return false;
        }

        // Ensure at least one pair is selected
        if (selectedPairs.length === 0) {
            alert('Please select at least one trading pair');
            event.preventDefault();
            return false;
        }

        // Validate RSI levels
        const rsiOverbought = parseInt(form.querySelector('input[name="rsi_overbought"]').value);
        const rsiOversold = parseInt(form.querySelector('input[name="rsi_oversold"]').value);

        if (rsiOverbought <= rsiOversold) {
            alert('RSI Overbought level must be higher than Oversold level');
            event.preventDefault();
            return false;
        }

        // Validate EMA periods
        const emaFast = parseInt(form.querySelector('input[name="ema_fast"]').value);
        const emaSlow = parseInt(form.querySelector('input[name="ema_slow"]').value);

        if (emaFast >= emaSlow) {
            alert('Fast EMA period must be less than Slow EMA period');
            event.preventDefault();
            return false;
        }

        return true;
    }

    showError(message) {
        // Create or update error toast
        let toast = document.getElementById('errorToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'errorToast';
            toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
            toast.style.zIndex = '9999';
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;
            document.body.appendChild(toast);
        } else {
            toast.querySelector('.toast-body').textContent = message;
        }

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Utility method to format numbers
    formatNumber(num, decimals = 2) {
        return parseFloat(num).toFixed(decimals);
    }

    // Utility method to format time
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.tradingBot = new TradingBotDashboard();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl+R or F5 for manual refresh
        if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
            event.preventDefault();
            window.tradingBot.updateStatus();
        }
        
        // Space bar to toggle bot (when not in input fields)
        if (event.code === 'Space' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
            event.preventDefault();
            const toggleBtn = document.querySelector('form[action*="toggle_bot"] button');
            if (toggleBtn) toggleBtn.click();
        }
    });
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        }, 0);
    });
}

// Service worker registration for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/static/sw.js');
    });
}
