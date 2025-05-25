/**
 * Chart Functions for Financial Dashboard
 * Handle chart initialization, rendering, and data processing
 */

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
    
    // Check if Chart is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not available. Cannot render charts.');
        return;
    }
    
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
        
        // Display fallback message in chart containers
        const chartContainers = document.querySelectorAll('.chart-container');
        chartContainers.forEach(container => {
            const canvas = container.querySelector('canvas');
            if (canvas) {
                // Create a fallback message
                const fallbackDiv = document.createElement('div');
                fallbackDiv.style.width = '100%';
                fallbackDiv.style.height = '100%';
                fallbackDiv.style.display = 'flex';
                fallbackDiv.style.alignItems = 'center';
                fallbackDiv.style.justifyContent = 'center';
                fallbackDiv.style.color = '#ff6b6b';
                fallbackDiv.style.textAlign = 'center';
                fallbackDiv.style.padding = '20px';
                fallbackDiv.style.fontSize = '14px';
                fallbackDiv.innerHTML = '<div>⚠️ Chart visualization unavailable</div>';
                
                // Hide the canvas and append the message
                canvas.style.display = 'none';
                container.appendChild(fallbackDiv);
            }
        });
    }
}

// Helper function to safely destroy a chart
function safelyDestroyChart(chartId) {
    try {
        if (typeof Chart === 'undefined') return;
        
        const chart = Chart.getChart(chartId);
        if (chart) {
            chart.destroy();
            console.log(`Chart destroyed: ${chartId}`);
        }
    } catch (e) {
        console.error(`Error destroying chart ${chartId}:`, e);
    }
}

// Initialize charts with test data
function initializeChartsWithTestData() {
    renderAllCharts();
}

// Make the functions globally available
window.generateTestChartData = generateTestChartData;
window.renderAllCharts = renderAllCharts;
window.initializeChartsWithTestData = initializeChartsWithTestData;
window.safelyDestroyChart = safelyDestroyChart;

// Call renderAllCharts on load to initialize charts
document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded, if not, load it
    if (typeof Chart === 'undefined') {
        console.log('Chart.js not found, loading it dynamically');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js';
        script.onload = function() {
            console.log('Chart.js loaded successfully');
            setTimeout(renderAllCharts, 100);
        };
        script.onerror = function() {
            console.error('Failed to load Chart.js');
        };
        document.head.appendChild(script);
    } else {
        setTimeout(renderAllCharts, 500);
        console.log('Initial chart rendering triggered');
    }
}); 