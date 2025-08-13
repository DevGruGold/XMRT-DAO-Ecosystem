/**
 * Real-Time Activity Widget for XMRT Ecosystem
 * ============================================
 * 
 * This JavaScript widget can be embedded in any of the three XMRT DAO pillars
 * to display real-time activities from the other systems in the ecosystem.
 * 
 * Author: Manus AI
 * Date: 2025-08-13
 */

class XMRTEcosystemActivityWidget {
    constructor(options = {}) {
        this.containerId = options.containerId || 'xmrt-activity-widget';
        this.apiEndpoint = options.apiEndpoint || '/api/activity/feed';
        this.updateInterval = options.updateInterval || 15000; // 15 seconds
        this.maxActivities = options.maxActivities || 10;
        this.showSystemIcons = options.showSystemIcons !== false;
        this.autoRefresh = options.autoRefresh !== false;
        
        this.activities = [];
        this.isInitialized = false;
        this.refreshTimer = null;
        
        this.systemIcons = {
            'boardroom': '🏛️',
            'hub': '💬',
            'dashboard': '📊'
        };
        
        this.eventTypeIcons = {
            'growth_update': '📈',
            'system_status': '🔧',
            'agent_discussion': '💬',
            'mining_update': '⛏️',
            'meshnet_update': '📡',
            'default': '🔔'
        };
    }
    
    async init() {
        if (this.isInitialized) return;
        
        try {
            this.createWidget();
            await this.loadActivities();
            
            if (this.autoRefresh) {
                this.startAutoRefresh();
            }
            
            this.isInitialized = true;
            console.log('✅ XMRT Ecosystem Activity Widget initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize XMRT Activity Widget:', error);
            this.showError('Failed to initialize activity widget');
        }
    }
    
    createWidget() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            throw new Error(`Container with ID '${this.containerId}' not found`);
        }
        
        container.innerHTML = `
            <div class="xmrt-activity-widget">
                <div class="widget-header">
                    <h3>🌐 Ecosystem Activity</h3>
                    <div class="widget-controls">
                        <button class="refresh-btn" onclick="window.xmrtWidget.refresh()">🔄</button>
                        <span class="status-indicator" id="widget-status">●</span>
                    </div>
                </div>
                <div class="activity-list" id="activity-list">
                    <div class="loading">Loading ecosystem activities...</div>
                </div>
                <div class="widget-footer">
                    <small>Last updated: <span id="last-updated">Never</span></small>
                </div>
            </div>
        `;
        
        this.injectStyles();
        
        // Make widget globally accessible for controls
        window.xmrtWidget = this;
    }
    
    injectStyles() {
        if (document.getElementById('xmrt-widget-styles')) return;
        
        const styles = `
            <style id="xmrt-widget-styles">
                .xmrt-activity-widget {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                
                .widget-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding-bottom: 10px;
                }
                
                .widget-header h3 {
                    margin: 0;
                    color: #fff;
                    font-size: 1.1em;
                }
                
                .widget-controls {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .refresh-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    color: white;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.3s ease;
                }
                
                .refresh-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                .status-indicator {
                    font-size: 12px;
                    color: #4ade80;
                    animation: pulse 2s infinite;
                }
                
                .status-indicator.error {
                    color: #ef4444;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                .activity-list {
                    max-height: 300px;
                    overflow-y: auto;
                    margin-bottom: 10px;
                }
                
                .activity-item {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 8px;
                    border-left: 3px solid #4ade80;
                    transition: all 0.3s ease;
                    animation: slideIn 0.5s ease-out;
                }
                
                .activity-item:hover {
                    background: rgba(255, 255, 255, 0.1);
                    transform: translateX(2px);
                }
                
                .activity-item.new {
                    border-left-color: #fbbf24;
                    background: rgba(251, 191, 36, 0.1);
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .activity-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 5px;
                }
                
                .activity-title {
                    font-weight: bold;
                    color: #fff;
                    font-size: 0.9em;
                }
                
                .activity-time {
                    font-size: 0.8em;
                    color: rgba(255, 255, 255, 0.7);
                }
                
                .activity-description {
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 0.85em;
                    line-height: 1.4;
                }
                
                .activity-source {
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 0.7em;
                    margin-top: 5px;
                    color: #fff;
                }
                
                .loading, .error {
                    text-align: center;
                    padding: 20px;
                    color: rgba(255, 255, 255, 0.7);
                    font-style: italic;
                }
                
                .error {
                    color: #ef4444;
                }
                
                .widget-footer {
                    text-align: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    padding-top: 8px;
                }
                
                .widget-footer small {
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 0.75em;
                }
                
                /* Scrollbar styling */
                .activity-list::-webkit-scrollbar {
                    width: 6px;
                }
                
                .activity-list::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 3px;
                }
                
                .activity-list::-webkit-scrollbar-thumb {
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 3px;
                }
                
                .activity-list::-webkit-scrollbar-thumb:hover {
                    background: rgba(255, 255, 255, 0.5);
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    async loadActivities() {
        try {
            this.setStatus('loading');
            
            const response = await fetch(this.apiEndpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.activities) {
                const newActivities = data.activities.slice(-this.maxActivities);
                this.updateActivities(newActivities);
                this.setStatus('online');
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error('Failed to load activities:', error);
            this.setStatus('error');
            this.showError('Failed to load ecosystem activities');
        }
    }
    
    updateActivities(newActivities) {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;
        
        // Check for new activities
        const existingIds = this.activities.map(a => a.id);
        const hasNewActivities = newActivities.some(a => !existingIds.includes(a.id));
        
        this.activities = newActivities;
        
        if (this.activities.length === 0) {
            activityList.innerHTML = '<div class="loading">No ecosystem activities yet...</div>';
            return;
        }
        
        const activitiesHtml = this.activities.map(activity => {
            const isNew = hasNewActivities && !existingIds.includes(activity.id);
            const icon = this.eventTypeIcons[activity.type] || this.eventTypeIcons.default;
            const systemIcon = this.showSystemIcons ? this.systemIcons[activity.source] || '🔗' : '';
            
            return `
                <div class="activity-item ${isNew ? 'new' : ''}" data-id="${activity.id}">
                    <div class="activity-header">
                        <div class="activity-title">
                            ${icon} ${activity.title}
                        </div>
                        <div class="activity-time">
                            ${this.formatTime(activity.timestamp)}
                        </div>
                    </div>
                    <div class="activity-description">
                        ${activity.description}
                    </div>
                    <div class="activity-source">
                        ${systemIcon} ${activity.source.toUpperCase()}
                    </div>
                </div>
            `;
        }).join('');
        
        activityList.innerHTML = activitiesHtml;
        
        // Update last updated time
        document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
        
        // Remove 'new' class after animation
        setTimeout(() => {
            document.querySelectorAll('.activity-item.new').forEach(item => {
                item.classList.remove('new');
            });
        }, 3000);
    }
    
    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
            return date.toLocaleDateString();
            
        } catch (error) {
            return 'Unknown';
        }
    }
    
    setStatus(status) {
        const indicator = document.getElementById('widget-status');
        if (!indicator) return;
        
        indicator.className = 'status-indicator';
        
        switch (status) {
            case 'online':
                indicator.style.color = '#4ade80';
                break;
            case 'loading':
                indicator.style.color = '#fbbf24';
                break;
            case 'error':
                indicator.style.color = '#ef4444';
                indicator.classList.add('error');
                break;
        }
    }
    
    showError(message) {
        const activityList = document.getElementById('activity-list');
        if (activityList) {
            activityList.innerHTML = `<div class="error">${message}</div>`;
        }
    }
    
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            this.loadActivities();
        }, this.updateInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    async refresh() {
        await this.loadActivities();
    }
    
    destroy() {
        this.stopAutoRefresh();
        
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = '';
        }
        
        const styles = document.getElementById('xmrt-widget-styles');
        if (styles) {
            styles.remove();
        }
        
        if (window.xmrtWidget === this) {
            delete window.xmrtWidget;
        }
        
        this.isInitialized = false;
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('xmrt-activity-widget')) {
        const widget = new XMRTEcosystemActivityWidget();
        widget.init();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = XMRTEcosystemActivityWidget;
}

