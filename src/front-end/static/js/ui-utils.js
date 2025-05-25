/**
 * UI Utilities for Mini RAG Application
 * Enhances user interface with modern interactions and feedback
 */

// Toast notification system
const Toast = {
  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - Type of notification: 'success', 'error', 'warning', or 'info'
   * @param {number} duration - Duration in ms before the toast disappears
   */
  show: function(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      toastContainer.style.position = 'fixed';
      toastContainer.style.bottom = '20px';
      toastContainer.style.right = '20px';
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style the toast
    toast.style.padding = '10px 16px';
    toast.style.borderRadius = '6px';
    toast.style.marginTop = '10px';
    toast.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '500';
    toast.style.minWidth = '200px';
    toast.style.animation = 'fadeInUp 0.3s ease, fadeOut 0.3s ease forwards';
    toast.style.animationDelay = `0s, ${(duration-300)/1000}s`;
    
    // Set colors based on type
    if (type === 'success') {
      toast.style.backgroundColor = 'var(--success)';
      toast.style.color = 'white';
    } else if (type === 'error') {
      toast.style.backgroundColor = 'var(--error)';
      toast.style.color = 'white';
    } else if (type === 'warning') {
      toast.style.backgroundColor = 'var(--warning)';
      toast.style.color = 'white';
    } else {
      toast.style.backgroundColor = 'var(--primary-color)';
      toast.style.color = 'white';
    }
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, duration);
  },
  
  // Convenience methods
  success: function(message, duration) {
    this.show(message, 'success', duration);
  },
  
  error: function(message, duration) {
    this.show(message, 'error', duration);
  },
  
  warning: function(message, duration) {
    this.show(message, 'warning', duration);
  },
  
  info: function(message, duration) {
    this.show(message, 'info', duration);
  }
};

// Loading indicator management
const LoadingIndicator = {
  /**
   * Initialize loading indicator
   * @param {string} containerId - The ID of the container element
   */
  init: function(containerId = 'loading-indicator') {
    // Create loading indicator if it doesn't exist
    const container = document.getElementById(containerId) || this._createIndicator(containerId);
    this.container = container;
    this.isVisible = false;
  },
  
  /**
   * Create loading indicator element
   * @private
   */
  _createIndicator: function(id) {
    const container = document.createElement('div');
    container.id = id;
    container.className = 'loading-indicator';
    container.style.display = 'none';
    
    const text = document.createElement('span');
    text.className = 'loading-text';
    text.textContent = 'Thinking';
    
    const dots = document.createElement('div');
    dots.className = 'loading-dots';
    
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('span');
      dots.appendChild(dot);
    }
    
    container.appendChild(text);
    container.appendChild(dots);
    
    document.body.appendChild(container);
    return container;
  },
  
  /**
   * Show loading indicator
   * @param {string} message - Optional custom loading message
   */
  show: function(message = 'Thinking') {
    if (!this.container) this.init();
    
    const textEl = this.container.querySelector('.loading-text');
    if (textEl) textEl.textContent = message;
    
    this.container.style.display = 'flex';
    this.isVisible = true;
  },
  
  /**
   * Hide loading indicator
   */
  hide: function() {
    if (!this.container) return;
    
    this.container.style.display = 'none';
    this.isVisible = false;
  },
  
  /**
   * Toggle loading indicator visibility
   */
  toggle: function(message) {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show(message);
    }
  }
};

// Mobile responsive enhancements
const MobileUI = {
  /**
   * Initialize mobile UI enhancements
   */
  init: function() {
    this._createSidebarToggle();
    this._setupMobileResponsiveness();
  },
  
  /**
   * Create sidebar toggle button for mobile
   * @private
   */
  _createSidebarToggle: function() {
    // Check if button already exists
    if (document.querySelector('.sidebar-toggle')) return;
    
    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'sidebar-toggle';
    toggleBtn.innerHTML = '<span>≡</span>';
    
    // Add click event
    toggleBtn.addEventListener('click', () => {
      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebar.classList.toggle('show');
        toggleBtn.classList.toggle('active');
      }
    });
    
    document.body.appendChild(toggleBtn);
  },
  
  /**
   * Setup mobile responsive behavior
   * @private
   */
  _setupMobileResponsiveness: function() {
    // Add click event to close sidebar when clicking outside
    document.addEventListener('click', (e) => {
      const sidebar = document.querySelector('.sidebar');
      const toggleBtn = document.querySelector('.sidebar-toggle');
      
      if (sidebar?.classList.contains('show') && 
          !sidebar.contains(e.target) && 
          e.target !== toggleBtn && 
          !toggleBtn?.contains(e.target)) {
        sidebar.classList.remove('show');
        toggleBtn?.classList.remove('active');
      }
    });
    
    // Initial check for mobile view
    this._checkMobileView();
    
    // Listen for window resize
    window.addEventListener('resize', () => {
      this._checkMobileView();
    });
  },
  
  /**
   * Check if we're in mobile view and adjust UI accordingly
   * @private
   */
  _checkMobileView: function() {
    const isMobile = window.innerWidth < 768;
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    
    if (isMobile) {
      sidebar?.classList.remove('show');
      toggleBtn?.style.display = 'flex';
    } else {
      sidebar?.classList.add('show');
      toggleBtn?.style.display = 'none';
    }
  }
};

// Handle document button events
function setupDocumentButtons() {
  // Initialize the document selector button
  const docSelectorBtn = document.getElementById('show-doc-selector');
  const docSelectorPanel = document.getElementById('document-selector-panel');
  const closeSelectorBtn = document.getElementById('close-doc-selector');
  
  if (docSelectorBtn && docSelectorPanel) {
    docSelectorBtn.addEventListener('click', function() {
      if (docSelectorPanel.style.display === 'block') {
        docSelectorPanel.style.display = 'none';
      } else {
        docSelectorPanel.style.display = 'block';
        
        // Load documents if needed
        if (typeof window.loadDocuments === 'function') {
          window.loadDocuments();
        }
      }
    });
  }
  
  if (closeSelectorBtn && docSelectorPanel) {
    closeSelectorBtn.addEventListener('click', function() {
      docSelectorPanel.style.display = 'none';
    });
  }
  
  // Handle events for Clear Focus buttons
  const clearFocusButtons = [
    document.getElementById('clear-focus-btn'),
    document.getElementById('dialog-clear-focus-btn')
  ];
  
  clearFocusButtons.forEach(btn => {
    if (btn) {
      btn.addEventListener('click', function() {
        if (typeof window.clearDocumentFocus === 'function') {
          window.clearDocumentFocus();
          Toast.info('Document focus cleared');
        } else {
          console.error('clearDocumentFocus function not available');
          Toast.error('Unable to clear document focus');
        }
      });
    }
  });
}

// Initialize sidebar charts and expanded view
function initSidebarCharts() {
    console.log('Initializing sidebar charts');
    
    const sidebarCharts = document.getElementById('sidebar-charts');
    const expandBtn = document.getElementById('expand-charts-btn');
    const expandedPanel = document.getElementById('expanded-charts-panel');
    const closeExpandedBtn = document.getElementById('close-expanded-btn');
    
    if (!sidebarCharts || !expandBtn) {
        console.error('Sidebar charts elements not found');
        return;
    }
    
    // Initialize expanded view
    if (expandBtn && expandedPanel && closeExpandedBtn) {
        // Expand button click handler
        expandBtn.addEventListener('click', () => {
            expandedPanel.style.display = 'flex';
            
            // Copy charts to expanded view
            setTimeout(() => {
                copyChartsToExpandedView();
            }, 100);
        });
        
        // Close expanded view
        closeExpandedBtn.addEventListener('click', () => {
            expandedPanel.style.display = 'none';
        });
    }
    
    // Function to copy charts to expanded view
    function copyChartsToExpandedView() {
        // Clone charts to expanded view for better performance
        copyChartToExpanded('llmGeneratedChart', 'expanded-main-chart');
        copyChartToExpanded('revenueChart', 'expanded-revenue-chart');
        copyChartToExpanded('miniPriceChart', 'expanded-price-chart');
        copyChartToExpanded('miniVolumeChart', 'expanded-volume-chart');
        
        // Copy financial table
        const sourceTable = document.getElementById('financial-table');
        const targetTable = document.getElementById('expanded-financial-table');
        
        if (sourceTable && targetTable) {
            targetTable.innerHTML = sourceTable.innerHTML;
        }
    }
    
    // Helper function to clone chart data to expanded view
    function copyChartToExpanded(sourceId, targetId) {
        const sourceChart = Chart.getChart(sourceId);
        const targetCanvas = document.getElementById(targetId);
        
        if (!sourceChart || !targetCanvas) {
            console.error(`Could not copy chart from ${sourceId} to ${targetId}`);
            return;
        }
        
        // Destroy existing chart if it exists
        const existingChart = Chart.getChart(targetId);
        if (existingChart) {
            existingChart.destroy();
        }
        
        // Clone chart config
        const newConfig = JSON.parse(JSON.stringify(sourceChart.config));
        
        // Adjust for larger display
        if (newConfig.options) {
            // Increase font sizes
            if (newConfig.options.scales) {
                Object.values(newConfig.options.scales).forEach(scale => {
                    if (scale.ticks) {
                        scale.ticks.font = { size: 12 };
                    }
                });
            }
            
            // Larger legend
            if (newConfig.options.plugins && newConfig.options.plugins.legend) {
                newConfig.options.plugins.legend.labels = {
                    ...(newConfig.options.plugins.legend.labels || {}),
                    font: { size: 14 }
                };
            }
        }
        
        // Create new chart with cloned config
        new Chart(targetCanvas, newConfig);
    }
    
    // Make sidebar charts section resizable
    let isResizing = false;
    let initialHeight, startY;
    
    // Detect resize from bottom edge of charts section
    sidebarCharts.addEventListener('mousedown', function(e) {
        // Only if click is near the bottom edge
        const rect = sidebarCharts.getBoundingClientRect();
        if (e.clientY > rect.bottom - 10) {
            isResizing = true;
            initialHeight = sidebarCharts.offsetHeight;
            startY = e.clientY;
            
            sidebarCharts.classList.add('resizing');
            e.preventDefault();
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const deltaY = e.clientY - startY;
        const newHeight = Math.max(100, Math.min(window.innerHeight * 0.8, initialHeight + deltaY));
        
        sidebarCharts.style.height = newHeight + 'px';
        
        // Update charts to fit new size
        updateAllSidebarCharts();
    });
    
    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            sidebarCharts.classList.remove('resizing');
            
            // Save height to localStorage
            localStorage.setItem('sidebarChartsHeight', sidebarCharts.style.height);
        }
    });
    
    // Restore saved height
    const savedHeight = localStorage.getItem('sidebarChartsHeight');
    if (savedHeight) {
        sidebarCharts.style.height = savedHeight;
    }
    
    // Initialize charts with data
    setTimeout(() => {
        initializeSidebarCharts();
    }, 500);
}

// Initialize all charts in sidebar
function initializeSidebarCharts() {
    console.log('Initializing sidebar charts with data');
    
    try {
        // Sample data for main chart (pie chart)
        const mainChartData = {
            type: 'doughnut',
            data: {
                labels: ['Borrowings', 'Govt. charges', 'Derivatives', 'Deferred income', 'Put option'],
                datasets: [{
                    data: [4678577, 3008990, 354689, 501508, 198166],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(139, 92, 246, 0.8)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 9 },
                            boxWidth: 10,
                            padding: 8
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(29, 16, 57, 0.95)',
                        callbacks: {
                            label: function(context) {
                                let value = context.raw;
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M (' + context.parsed.toFixed(1) + '%)';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(1) + 'K (' + context.parsed.toFixed(1) + '%)';
                                } else {
                                    return value;
                                }
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        };
        
        // Sample data for revenue chart (line chart)
        const revenueChartData = {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [5300, 5900, 6200, 5800, 6400, 6700],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { 
                            color: 'rgba(255, 255, 255, 0.6)', 
                            font: { size: 8 },
                            maxRotation: 0
                        }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { 
                            color: 'rgba(255, 255, 255, 0.6)', 
                            font: { size: 8 } 
                        }
                    }
                }
            }
        };
        
        // Sample data for price chart (mini)
        const priceChartData = {
            type: 'line',
            data: {
                labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    data: [12, 13, 14, 13.5, 15],
                    borderColor: 'rgba(139, 92, 246, 1)',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.3,
                    pointRadius: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        display: false,
                        grid: { display: false }
                    }
                },
                elements: {
                    line: { borderWidth: 1.5 }
                }
            }
        };
        
        // Sample data for volume chart (mini)
        const volumeChartData = {
            type: 'bar',
            data: {
                labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    data: [120, 150, 180, 130, 200],
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderWidth: 0,
                    borderRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        display: false,
                        grid: { display: false }
                    }
                }
            }
        };
        
        // Render all charts
        renderSidebarChart('llmGeneratedChart', mainChartData);
        renderSidebarChart('revenueChart', revenueChartData);
        renderSidebarChart('miniPriceChart', priceChartData);
        renderSidebarChart('miniVolumeChart', volumeChartData);
        
    } catch (e) {
        console.error('Error initializing sidebar charts:', e);
    }
}

// Render a single chart in the sidebar
function renderSidebarChart(chartId, chartData) {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        console.error(`Canvas element ${chartId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    const existingChart = Chart.getChart(chartId);
    if (existingChart) {
        existingChart.destroy();
    }
    
    try {
        // Create new chart
        new Chart(canvas, chartData);
    } catch (e) {
        console.error(`Error creating chart ${chartId}:`, e);
    }
}

// Update all sidebar charts to fit current size
function updateAllSidebarCharts() {
    if (typeof Chart === 'undefined') return;
    
    const chartIds = ['llmGeneratedChart', 'revenueChart', 'miniPriceChart', 'miniVolumeChart'];
    chartIds.forEach(id => {
        const chart = Chart.getChart(id);
        if (chart) {
            chart.resize();
        }
    });
}

// Update sidebar charts with new data (e.g., when changing time range)
function updateSidebarChartsData(timeRange) {
    // Generate appropriate labels based on time range
    let labels, priceData, volumeData, revenueData;
    
    switch(timeRange) {
        case '6D':
            labels = ['Feb 4', 'Feb 11', 'Feb 18', 'Feb 25', 'Mar 4', 'Mar 11'];
            break;
        case '1M':
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            break;
        case '3M':
            labels = ['Jan', 'Feb', 'Mar'];
            break;
        case '1Y':
            labels = ['Q1', 'Q2', 'Q3', 'Q4'];
            break;
        default:
            labels = ['Feb 4', 'Feb 11', 'Feb 18', 'Feb 25', 'Mar 4', 'Mar 11'];
    }
    
    // Generate random data for charts (would be real data in production)
    priceData = Array.from({length: labels.length}, () => Math.floor(Math.random() * 10) + 10);
    volumeData = Array.from({length: labels.length}, () => Math.floor(Math.random() * 100) + 100);
    revenueData = Array.from({length: labels.length}, () => Math.floor(Math.random() * 1000) + 5000);
    
    // Update charts with new data
    updateChartData('miniPriceChart', labels, priceData);
    updateChartData('miniVolumeChart', labels, volumeData);
    updateChartData('revenueChart', labels, revenueData);
    
    // If in expanded view, update those charts too
    if (document.getElementById('expanded-charts-panel').style.display === 'flex') {
        updateChartData('expanded-price-chart', labels, priceData);
        updateChartData('expanded-volume-chart', labels, volumeData);
        updateChartData('expanded-revenue-chart', labels, revenueData);
    }
    
    // Show toast notification
    if (window.Toast) {
        window.Toast.info(`Charts updated to ${timeRange} view`);
    }
}

// Helper function to update a chart with new data
function updateChartData(chartId, labels, data) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update('none'); // Use 'none' for smoother transitions
    }
}

// Generate test chart data function
function generateTestChartData(chartType) {
    let data = {};
    
    switch(chartType) {
        case 'pie':
        case 'doughnut':
            data = {
                labels: ['Borrowings', 'Govt. charges', 'Derivatives', 'Other'],
                datasets: [{
                    data: [4678000, 3009000, 354000, 699000],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }]
            };
            break;
            
        case 'line':
            data = {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [5300, 5900, 6200, 5800, 6400, 6700],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            };
            break;
            
        case 'bar':
            data = {
                labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                datasets: [{
                    label: 'Revenue',
                    data: [15000, 18000, 16500, 22000],
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 1
                }]
            };
            break;
            
        case 'radar':
            data = {
                labels: ['Revenue', 'Growth', 'Expenses', 'Profit', 'Customers'],
                datasets: [{
                    label: '2022',
                    data: [85, 70, 60, 75, 90],
                    backgroundColor: 'rgba(99, 102, 241, 0.3)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    pointBackgroundColor: 'rgba(99, 102, 241, 1)'
                }]
            };
            break;
            
        case 'polarArea':
            data = {
                labels: ['Sales', 'Marketing', 'Development', 'Support', 'Admin'],
                datasets: [{
                    data: [300, 180, 250, 120, 150],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(139, 92, 246, 0.8)'
                    ]
                }]
            };
            break;
            
        default:
            data = {
                labels: ['Borrowings', 'Govt. charges', 'Derivatives', 'Other'],
                datasets: [{
                    data: [4678000, 3009000, 354000, 699000],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }]
            };
    }
    
    return data;
}

// Render all charts function
function renderAllCharts() {
    console.log('Rendering all charts...');
    
    try {
        // Safely destroy any existing charts
        safelyDestroyChart('llmGeneratedChart');
        safelyDestroyChart('revenueChart');
        safelyDestroyChart('miniPriceChart');
        safelyDestroyChart('miniVolumeChart');
        
        // Create main chart (financial overview)
        const mainChartCanvas = document.getElementById('llmGeneratedChart');
        if (mainChartCanvas) {
            const mainChartData = generateTestChartData('doughnut');
            new Chart(mainChartCanvas, {
                type: 'doughnut',
                data: mainChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: 'rgba(255, 255, 255, 0.7)',
                                font: { size: 10 },
                                boxWidth: 12,
                                padding: 10
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(29, 16, 57, 0.95)'
                        }
                    },
                    cutout: '60%'
                }
            });
        }
        
        // Create revenue chart
        const revenueChartCanvas = document.getElementById('revenueChart');
        if (revenueChartCanvas) {
            const revenueData = generateTestChartData('line');
            new Chart(revenueChartCanvas, {
                type: 'line',
                data: revenueData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: 'rgba(255, 255, 255, 0.6)' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: 'rgba(255, 255, 255, 0.6)' }
                        }
                    }
                }
            });
        }
        
        // Create price chart
        const priceChartCanvas = document.getElementById('miniPriceChart');
        if (priceChartCanvas) {
            new Chart(priceChartCanvas, {
                type: 'line',
                data: {
                    labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        data: [12, 13, 14, 13.5, 15],
                        borderColor: 'rgba(139, 92, 246, 1)',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.3,
                        pointRadius: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } },
                    scales: {
                        x: { display: false, grid: { display: false } },
                        y: { display: false, grid: { display: false } }
                    },
                    elements: { line: { borderWidth: 1.5 } }
                }
            });
        }
        
        // Create volume chart
        const volumeChartCanvas = document.getElementById('miniVolumeChart');
        if (volumeChartCanvas) {
            new Chart(volumeChartCanvas, {
                type: 'bar',
                data: {
                    labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        data: [120, 150, 180, 130, 200],
                        backgroundColor: 'rgba(239, 68, 68, 0.7)',
                        borderWidth: 0,
                        borderRadius: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } },
                    scales: {
                        x: { display: false, grid: { display: false } },
                        y: { display: false, grid: { display: false } }
                    }
                }
            });
        }
        
        console.log('All charts rendered successfully');
    } catch (e) {
        console.error('Error rendering charts:', e);
    }
}

// Helper function to safely destroy a chart
function safelyDestroyChart(chartId) {
    try {
        const chart = Chart.getChart(chartId);
        if (chart) {
            chart.destroy();
            console.log(`[ui-utils.js] Destroyed existing chart: ${chartId}`);
        }
    } catch (e) {
        console.error(`[ui-utils.js] Error safely destroying chart ${chartId}:`, e);
    }
}

// Initialize charts with test data - alias for renderAllCharts
function initializeChartsWithTestData() {
    renderAllCharts();
}

// Make the functions globally available
window.generateTestChartData = generateTestChartData;
window.renderAllCharts = renderAllCharts;
window.initializeChartsWithTestData = initializeChartsWithTestData;
window.safelyDestroyChart = safelyDestroyChart;

// Document ready function to initialize all components
document.addEventListener('DOMContentLoaded', function() {
  // Initialize all basic UI components
  setupMobileUI();
  initDocumentSelector();
  initFilePreview();
  initChatModes();
  initChartTest();
  initChartTypeSelector();
  
  // Initialize the sidebar charts instead of draggable panel
  initSidebarCharts();
  
  // Setup time range buttons
  const timeButtons = document.querySelectorAll('.time-btn');
  if (timeButtons.length) {
      timeButtons.forEach(btn => {
          btn.addEventListener('click', function() {
              // Remove active class from all buttons
              timeButtons.forEach(b => b.classList.remove('active'));
              
              // Add active class to clicked button
              this.classList.add('active');
              
              // Update charts based on time range
              const timeRange = this.getAttribute('data-range');
              updateSidebarChartsData(timeRange);
          });
      });
  }
  
  // Make utilities globally available
  window.Toast = Toast;
  window.LoadingIndicator = LoadingIndicator;
  window.updateSidebarChartsData = updateSidebarChartsData;
  
  console.log('UI components initialized');
});