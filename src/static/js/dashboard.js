// ===== DASHBOARD METRICS UPDATE =====
function updateMetrics() {
    // Simulate real-time data updates
    const metrics = {
        uptime: Math.random() * 0.5 + 99.5,
        responseTime: Math.random() * 20 + 35,
        hashrate: Math.random() * 0.5 + 2.5,
        miners: Math.floor(Math.random() * 100 + 1200),
        xmrPrice: Math.random() * 10 + 160,
        difficulty: Math.random() * 50 + 420,
        meshNodes: Math.floor(Math.random() * 10 + 35),
        meshCoverage: Math.random() * 10 + 80,
        agentTasks: Math.floor(Math.random() * 20 + 140),
        agentMemory: Math.random() * 0.5 + 2.0,
        agentCredits: Math.floor(Math.random() * 50 + 150)
    };

    // Update DOM elements safely
    const updateElement = (id, value) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    };

    updateElement('uptime', metrics.uptime.toFixed(1) + '%');
    updateElement('response-time', Math.floor(metrics.responseTime) + 'ms');
    updateElement('total-hashrate', metrics.hashrate.toFixed(1) + ' GH/s');
    updateElement('active-miners', metrics.miners.toLocaleString());
    updateElement('xmr-price', '$' + metrics.xmrPrice.toFixed(2));
    updateElement('difficulty', metrics.difficulty.toFixed(1) + 'B');
    updateElement('mesh-nodes', metrics.meshNodes);
    updateElement('mesh-coverage', Math.floor(metrics.meshCoverage) + '%');
    updateElement('agent-tasks', metrics.agentTasks);
    updateElement('agent-memory', metrics.agentMemory.toFixed(1) + 'GB');
    updateElement('agent-credits', metrics.agentCredits);
}

// ===== CHAT FUNCTIONALITY =====
class ChatManager {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.messagesContainer = document.getElementById('messages');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
    }
    
    sendMessage() {
        if (!this.messageInput || !this.messagesContainer) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();

        // Send to backend API
        this.sendToAPI(message);
    }
    
    addMessage(content, type = 'eliza') {
        if (!this.messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);
        
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message eliza-message typing-indicator';
        typingDiv.innerHTML = '<div class="message-content">Eliza is typing...</div>';
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        
        return typingDiv;
    }
    
    removeTypingIndicator() {
        const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    sendToAPI(message) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            this.removeTypingIndicator();
            const response = data.success ? (typeof data.reply === 'object' ? JSON.stringify(data.reply, null, 2) : data.reply) : 'Error processing command.';
            this.addMessage(response, 'eliza');
        })
        .catch(error => {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.addMessage('Connection error. Please try again.', 'eliza');
        });
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
}

// ===== MINING CALCULATOR =====
class MiningCalculator {
    constructor() {
        this.initializeElements();
        this.initializeEventListeners();
        this.updateCalculations();
    }
    
    initializeElements() {
        this.elements = {
            hashrateSlider: document.getElementById('hashrate-slider'),
            devicesSlider: document.getElementById('devices-slider'),
            uptimeSlider: document.getElementById('uptime-slider'),
            xmrPriceSlider: document.getElementById('xmr-price-slider'),
            advancedProcessorsToggle: document.getElementById('advanced-processors-toggle'),
            solidStateBatteryToggle: document.getElementById('solid-state-battery-toggle'),
            
            hashrateValue: document.getElementById('hashrate-value'),
            devicesValue: document.getElementById('devices-value'),
            uptimeValue: document.getElementById('uptime-value'),
            xmrPriceValue: document.getElementById('xmr-price-value'),
            
            totalHashrate: document.getElementById('total-hashrate'),
            networkShare: document.getElementById('network-share'),
            xmrPriceDisplay: document.getElementById('xmr-price-display'),
            networkHashrate: document.getElementById('network-hashrate'),
            
            dailyXmr: document.getElementById('daily-xmr'),
            dailyUsd: document.getElementById('daily-usd'),
            monthlyXmr: document.getElementById('monthly-xmr'),
            monthlyUsd: document.getElementById('monthly-usd'),
            yearlyXmr: document.getElementById('yearly-xmr'),
            yearlyUsd: document.getElementById('yearly-usd')
        };
    }
    
    initializeEventListeners() {
        const sliders = ['hashrateSlider', 'devicesSlider', 'uptimeSlider', 'xmrPriceSlider'];
        const toggles = ['advancedProcessorsToggle', 'solidStateBatteryToggle'];
        
        sliders.forEach(slider => {
            if (this.elements[slider]) {
                this.elements[slider].addEventListener('input', () => this.updateCalculations());
            }
        });
        
        toggles.forEach(toggle => {
            if (this.elements[toggle]) {
                this.elements[toggle].addEventListener('change', () => this.updateCalculations());
            }
        });
    }
    
    updateCalculations() {
        const hashrate = this.getSliderValue('hashrateSlider', 600);
        const devices = this.getSliderValue('devicesSlider', 100);
        const uptime = this.getSliderValue('uptimeSlider', 24);
        const xmrPrice = this.getSliderValue('xmrPriceSlider', 165);
        
        const advancedProcessors = this.getToggleValue('advancedProcessorsToggle');
        const solidStateBattery = this.getToggleValue('solidStateBatteryToggle');
        
        let effectiveHashrate = hashrate;
        let effectiveUptime = uptime;
        
        if (advancedProcessors) {
            effectiveHashrate *= 2.5;
        }
        
        if (solidStateBattery) {
            effectiveUptime *= 1.25;
            if (effectiveUptime > 24) effectiveUptime = 24;
        }
        
        const totalHashrate = effectiveHashrate * devices;
        const networkHashrate = 2800000000; // 2.8 GH/s in H/s
        const networkShare = (totalHashrate / networkHashrate) * 100;
        
        const dailyXMR = (totalHashrate / networkHashrate) * 720 * (effectiveUptime / 24);
        const monthlyXMR = dailyXMR * 30;
        const yearlyXMR = dailyXMR * 365;
        
        const dailyUSD = dailyXMR * xmrPrice;
        const monthlyUSD = monthlyXMR * xmrPrice;
        const yearlyUSD = yearlyXMR * xmrPrice;
        
        // Update displays
        this.updateElement('hashrateValue', hashrate + ' H/s');
        this.updateElement('devicesValue', devices.toLocaleString());
        this.updateElement('uptimeValue', uptime + ' hrs');
        this.updateElement('xmrPriceValue', '$' + xmrPrice);
        
        this.updateElement('totalHashrate', (totalHashrate / 1000).toFixed(1) + 'K H/s');
        this.updateElement('networkShare', networkShare.toFixed(4) + '%');
        this.updateElement('xmrPriceDisplay', '$' + xmrPrice);
        this.updateElement('networkHashrate', '2.8 GH/s');
        
        this.updateElement('dailyXmr', dailyXMR.toFixed(4) + ' XMR');
        this.updateElement('dailyUsd', '$' + dailyUSD.toFixed(2));
        this.updateElement('monthlyXmr', monthlyXMR.toFixed(2) + ' XMR');
        this.updateElement('monthlyUsd', '$' + monthlyUSD.toFixed(2));
        this.updateElement('yearlyXmr', yearlyXMR.toFixed(2) + ' XMR');
        this.updateElement('yearlyUsd', '$' + yearlyUSD.toFixed(2));
    }
    
    getSliderValue(elementKey, defaultValue) {
        const element = this.elements[elementKey];
        return element ? parseInt(element.value) : defaultValue;
    }
    
    getToggleValue(elementKey) {
        const element = this.elements[elementKey];
        return element ? element.checked : false;
    }
    
    updateElement(elementKey, value) {
        const element = this.elements[elementKey];
        if (element) {
            element.textContent = value;
        }
    }
}

// ===== UTILITY FUNCTIONS =====
function formatNumber(num, decimals = 2) {
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat manager
    const chatManager = new ChatManager();
    
    // Initialize mining calculator
    const miningCalculator = new MiningCalculator();
    
    // Start metrics updates
    updateMetrics();
    setInterval(updateMetrics, 5000); // Update every 5 seconds
    
    // Add smooth scrolling for better UX
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states for better UX
    const addLoadingState = (element) => {
        if (element) {
            element.classList.add('loading');
            setTimeout(() => {
                element.classList.remove('loading');
            }, 1000);
        }
    };
    
    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe dashboard sections
    document.querySelectorAll('.dashboard-section').forEach(section => {
        observer.observe(section);
    });
    
    console.log('XMRT-DAO Dashboard initialized successfully');
});

