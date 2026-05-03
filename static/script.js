// ============================================
// CYBHER - Healthcare Security Dashboard
// ============================================

// --- Global State ---
let soundEnabled = true;
let notificationsEnabled = false;
let updateIntervalMs = 1000;
let maxPoints = 50;
let dataInterval = null;
let statsInterval = null;
let analyticsInterval = null;
let previousValues = { hr: 0, temp: 0, spo2: 0, bp: 0, resp: 0 };
let threatCount = 0;
let sessionStartTime = Date.now();
let currentTab = 'dashboard';

// --- Chart Setup ---
const ctx = document.getElementById('mainChart').getContext('2d');

// Gradient Fills
const gradientHr = ctx.createLinearGradient(0, 0, 0, 400);
gradientHr.addColorStop(0, 'rgba(239, 68, 68, 0.4)');
gradientHr.addColorStop(1, 'rgba(239, 68, 68, 0)');

const gradientSpo2 = ctx.createLinearGradient(0, 0, 0, 400);
gradientSpo2.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
gradientSpo2.addColorStop(1, 'rgba(59, 130, 246, 0)');

const vitalsChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Heart Rate',
                borderColor: '#ef4444',
                backgroundColor: gradientHr,
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                data: [],
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'Temperature (×10)',
                borderColor: '#f59e0b',
                borderWidth: 2,
                pointRadius: 0,
                borderDash: [5, 5],
                data: [],
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'SpO2',
                borderColor: '#3b82f6',
                backgroundColor: gradientSpo2,
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                data: [],
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'BP Systolic',
                borderColor: '#10b981',
                borderWidth: 2,
                pointRadius: 0,
                data: [],
                tension: 0.4,
                yAxisID: 'y'
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: { 
                labels: { 
                    color: '#94a3b8', 
                    font: { family: 'Outfit' },
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleColor: '#f8fafc',
                bodyColor: '#94a3b8',
                borderColor: 'rgba(148, 163, 184, 0.2)',
                borderWidth: 1,
                padding: 12,
                displayColors: true
            }
        },
        scales: {
            x: { 
                display: false 
            },
            y: {
                grid: { color: 'rgba(30, 41, 59, 0.5)' },
                ticks: { color: '#64748b' },
                min: 0,
                max: 200
            }
        },
        animation: { duration: 300 }
    }
});

// --- Federated Learning Chart ---
let flChart = null;

function initFlChart() {
    const flCtx = document.getElementById('flChart');
    if (!flCtx) return;
    
    flChart = new Chart(flCtx.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Hospital A',
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    data: [],
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Hospital B',
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    data: [],
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Global Model',
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    data: [],
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    labels: { color: '#94a3b8', font: { family: 'Outfit' } }
                }
            },
            scales: {
                x: { 
                    grid: { color: 'rgba(30, 41, 59, 0.3)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { color: 'rgba(30, 41, 59, 0.3)' },
                    ticks: { color: '#64748b' },
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Accuracy %',
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

// --- Analytics Charts ---
let threatPieChart = null;
let timelineChart = null;

function initAnalyticsCharts() {
    // Threat Distribution Pie Chart
    const pieCtx = document.getElementById('threatPieChart');
    if (pieCtx && !threatPieChart) {
        threatPieChart = new Chart(pieCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Spike', 'Flatline', 'Noise', 'Spoof', 'Replay', 'MITM'],
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#f59e0b',
                        '#ef4444',
                        '#a855f7',
                        '#10b981',
                        '#3b82f6',
                        '#ec4899'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', font: { family: 'Outfit' } }
                    }
                }
            }
        });
    }

    // Timeline Chart
    const timeCtx = document.getElementById('timelineChart');
    if (timeCtx && !timelineChart) {
        timelineChart = new Chart(timeCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Threats Detected',
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                return `${value} threat${value !== 1 ? 's' : ''} detected`;
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        grid: { display: false, color: 'rgba(30, 41, 59, 0.3)' },
                        ticks: { 
                            color: '#64748b',
                            font: { size: 11 },
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        grid: { color: 'rgba(30, 41, 59, 0.3)' },
                        ticks: { 
                            color: '#64748b',
                            font: { size: 11 },
                            stepSize: 1,
                            precision: 0
                        },
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Threats',
                            color: '#94a3b8',
                            font: { size: 12 }
                        }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
}

// --- Tab Switching ---
function switchTab(tabId) {
    // Nav active state
    document.querySelectorAll('.nav-links li').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active');

    // View switching
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.getElementById(`view-${tabId}`).classList.add('active');

    // Header title update
    const titles = { 
        'dashboard': 'Live Monitoring', 
        'attacks': 'Attack Injection Hub', 
        'federated': 'Federated Learning Lab',
        'analytics': 'Threat Analytics',
        'settings': 'Settings'
    };
    document.getElementById('page-title').textContent = titles[tabId];

    // Update current tab
    currentTab = tabId;
    
    // Initialize charts when switching to their tabs
    if (tabId === 'federated') {
        initFlChart();
        if (analyticsInterval) clearInterval(analyticsInterval);
    } else if (tabId === 'analytics') {
        initAnalyticsCharts();
        fetchThreatIntel();
        // Auto-refresh analytics every 5 seconds
        if (analyticsInterval) clearInterval(analyticsInterval);
        analyticsInterval = setInterval(fetchThreatIntel, 5000);
    } else if (tabId === 'settings') {
        fetchModelStatus();
        if (analyticsInterval) clearInterval(analyticsInterval);
    } else {
        if (analyticsInterval) clearInterval(analyticsInterval);
    }
}

// --- Realtime Data Loop ---
async function fetchData() {
    try {
        const res = await fetch('/stream');
        const data = await res.json();

        // Update Chart
        const time = new Date().toLocaleTimeString();
        if (vitalsChart.data.labels.length > maxPoints) {
            vitalsChart.data.labels.shift();
            vitalsChart.data.datasets.forEach(d => d.data.shift());
        }
        vitalsChart.data.labels.push(time);
        vitalsChart.data.datasets[0].data.push(data.heart_rate);
        vitalsChart.data.datasets[1].data.push(data.temperature * 10); // Scale for visibility
        vitalsChart.data.datasets[2].data.push(data.spo2);
        vitalsChart.data.datasets[3].data.push(data.bp_systolic || 120);
        vitalsChart.update('none');

        // Update Metrics with trends
        updateMetricWithTrend('hr', data.heart_rate, 'metric-hr', 'trend-hr', 'card-hr');
        updateMetricWithTrend('temp', data.temperature, 'metric-temp', 'trend-temp', 'card-temp');
        updateMetricWithTrend('spo2', data.spo2, 'metric-spo2', 'trend-spo2', 'card-spo2');
        
        document.getElementById('metric-bp').textContent = data.blood_pressure || '--/--';
        document.getElementById('metric-resp').textContent = data.respiratory_rate || '--';

        // Security Status & Anomaly Handling
        const isAnomaly = data.anomaly_detected || data.is_anomaly_injected;
        updateSecurityStatus(isAnomaly, data);

        if (isAnomaly) {
            threatCount++;
            document.getElementById('threats-blocked').textContent = threatCount;
            logAlert(data);
            showThreatBanner(data);
            playAlertSound();
            highlightAnomalyCards(data);
            
            // Update timeline chart if on analytics tab
            if (currentTab === 'analytics' && timelineChart) {
                // Refresh threat intel to get updated timeline data
                setTimeout(() => fetchThreatIntel(), 500);
            }
        }

    } catch (e) { 
        console.error('Stream error:', e); 
    }
}

function updateMetricWithTrend(key, value, metricId, trendId, cardId) {
    const metricEl = document.getElementById(metricId);
    const trendEl = document.getElementById(trendId);
    const cardEl = document.getElementById(cardId);
    
    metricEl.textContent = value;
    
    const prev = previousValues[key];
    if (value > prev) {
        trendEl.innerHTML = '<i class="fa-solid fa-arrow-trend-up"></i>';
        trendEl.className = 'stat-trend up';
    } else if (value < prev) {
        trendEl.innerHTML = '<i class="fa-solid fa-arrow-trend-down"></i>';
        trendEl.className = 'stat-trend down';
    } else {
        trendEl.innerHTML = '<i class="fa-solid fa-minus"></i>';
        trendEl.className = 'stat-trend stable';
    }
    
    previousValues[key] = value;
}

function updateSecurityStatus(isAnomaly, data) {
    const statusEl = document.getElementById('security-status');
    const iconEl = document.getElementById('status-icon');
    const cardEl = document.getElementById('card-status');
    const iconBox = cardEl.querySelector('.icon-box');
    
    if (isAnomaly) {
        statusEl.textContent = data.severity?.toUpperCase() || 'THREAT';
        statusEl.className = 'value status-text danger';
        iconEl.className = 'fa-solid fa-shield-xmark';
        iconBox.className = 'icon-box status-danger';
        cardEl.classList.add('threat-active');
    } else {
        statusEl.textContent = 'SECURE';
        statusEl.className = 'value status-text';
        iconEl.className = 'fa-solid fa-shield-check';
        iconBox.className = 'icon-box status-ok';
        cardEl.classList.remove('threat-active');
    }
}

function highlightAnomalyCards(data) {
    const cards = ['card-hr', 'card-temp', 'card-spo2', 'card-bp', 'card-resp'];
    cards.forEach(id => {
        const card = document.getElementById(id);
        card.classList.add('anomaly-flash');
        setTimeout(() => card.classList.remove('anomaly-flash'), 2000);
    });
}

function showThreatBanner(data) {
    const banner = document.getElementById('threat-banner');
    const text = document.getElementById('threat-banner-text');
    text.textContent = `${data.severity?.toUpperCase() || 'THREAT'}: ${data.threat_details || data.attack_type + ' attack detected!'}`;
    banner.style.display = 'flex';
    banner.className = `threat-banner ${data.severity || 'high'}`;
}

function dismissThreatBanner() {
    document.getElementById('threat-banner').style.display = 'none';
}

async function fetchStats() {
    try {
        const res = await fetch('/system-stats');
        const stats = await res.json();
        document.getElementById('cpu-bar').style.width = stats.cpu + '%';
        document.getElementById('ram-bar').style.width = stats.memory + '%';
        document.getElementById('network-bar').style.width = stats.network_load + '%';
        
        // Update uptime
        const uptime = Math.floor((Date.now() - sessionStartTime) / 1000);
        const mins = Math.floor(uptime / 60);
        const secs = uptime % 60;
        document.getElementById('stat-uptime').textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    } catch (e) { }
}

async function fetchSessionStats() {
    try {
        const res = await fetch('/session-stats');
        const stats = await res.json();
        
        document.getElementById('stat-packets').textContent = stats.total_packets || 0;
        document.getElementById('stat-anomalies').textContent = stats.anomalies_detected || 0;
        document.getElementById('stat-rate').textContent = (stats.anomaly_rate || 0) + '%';
        document.getElementById('accuracy-value').textContent = Math.round(stats.model_accuracy || 0);
    } catch (e) { }
}

function logAlert(data) {
    const feed = document.getElementById('security-log');
    if (feed.querySelector('.empty-log')) feed.innerHTML = '';

    const severityClass = data.severity || 'high';
    const item = document.createElement('div');
    item.className = `alert-item ${severityClass}`;
    item.innerHTML = `
        <div class="alert-header">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <strong>${data.attack_type || 'Unknown'}</strong>
            <span class="severity-badge ${severityClass}">${severityClass}</span>
        </div>
        <div class="alert-body">${data.threat_details || 'Anomaly detected in vital signs'}</div>
        <div class="alert-time">${new Date().toLocaleTimeString()}</div>
    `;
    feed.insertBefore(item, feed.firstChild);
    
    // Keep only last 50 logs
    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
}

function playAlertSound() {
    if (!soundEnabled) return;
    const audio = document.getElementById('alert-sound');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
    }
}

// --- Start Data Loops ---
function startDataStreams() {
    if (dataInterval) clearInterval(dataInterval);
    if (statsInterval) clearInterval(statsInterval);
    
    dataInterval = setInterval(fetchData, updateIntervalMs);
    statsInterval = setInterval(() => {
        fetchStats();
        fetchSessionStats();
    }, 3000);
}

startDataStreams();

// --- Attack Injection ---
async function injectAttack(type) {
    const btn = event.currentTarget;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Injecting...';
    
    try {
    await fetch('/inject-attack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, duration: 10 })
        });
        
        logAlert({
            attack_type: 'COMMAND',
            severity: 'medium',
            threat_details: `Manually injecting ${type} attack sequence...`
        });
        
        // Auto switch to dashboard
        document.querySelector('.nav-links li').click();
        
    } catch (e) {
        console.error('Attack injection failed:', e);
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-play"></i> Inject Attack';
        }, 1000);
    }
}

async function clearAttack() {
    try {
        await fetch('/clear-attack', { method: 'POST' });
        logAlert({
            attack_type: 'SYSTEM',
            severity: 'low',
            threat_details: 'All active attacks have been cleared'
        });
    } catch (e) {
        console.error('Failed to clear attack:', e);
    }
}

// --- Patient Switching ---
async function switchPatient(patientId) {
    try {
        await fetch('/patients/switch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient_id: patientId })
        });
        
        // Clear chart for new patient
        clearChart();
        
    } catch (e) {
        console.error('Failed to switch patient:', e);
    }
}

// --- Federated Learning ---
async function startFederatedLearning() {
    const btn = document.getElementById('start-fl-btn');
    const viz = document.getElementById('fl-visualizer');
    const rounds = parseInt(document.getElementById('fl-rounds').value) || 5;

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Training...';
    viz.innerHTML = '<div class="fl-loading"><i class="fa-solid fa-circle-notch fa-spin"></i> Initializing federated learning...</div>';
    
    // Reset node statuses
    document.querySelectorAll('.node-card').forEach(n => n.classList.remove('active', 'training'));
    document.getElementById('status-node-a').textContent = 'Preparing...';
    document.getElementById('status-node-b').textContent = 'Preparing...';
    document.getElementById('status-global').textContent = 'Waiting...';

    try {
        const res = await fetch('/train-fl', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rounds: rounds })
        });
        const result = await res.json();

        viz.innerHTML = '';
        
        // Reset FL chart
        if (flChart) {
            flChart.data.labels = [];
            flChart.data.datasets.forEach(d => d.data = []);
        }

        // Animate rounds
        for (const round of result.history) {
            await new Promise(r => setTimeout(r, 800));

            // Update nodes
            document.getElementById('node-a').classList.add('training');
            document.getElementById('node-b').classList.add('training');
            document.getElementById('status-node-a').textContent = 'Training...';
            document.getElementById('status-node-b').textContent = 'Training...';
            
            await new Promise(r => setTimeout(r, 400));
            
            document.getElementById('node-global').classList.add('active');
            document.getElementById('status-global').textContent = 'Aggregating...';

            // Add round info
            const row = document.createElement('div');
            row.className = 'fl-progress-row';
            row.innerHTML = `
                <span class="round-num">Round ${round.round}</span>
                <span class="acc-a"><i class="fa-solid fa-hospital"></i> ${(round.hospital_a_accuracy * 100).toFixed(1)}%</span>
                <span class="acc-b"><i class="fa-solid fa-hospital-user"></i> ${(round.hospital_b_accuracy * 100).toFixed(1)}%</span>
                <span class="acc-global"><i class="fa-solid fa-server"></i> ${(round.global_model_accuracy * 100).toFixed(1)}%</span>
            `;
            viz.appendChild(row);

            // Update chart
            if (flChart) {
                flChart.data.labels.push(`Round ${round.round}`);
                flChart.data.datasets[0].data.push(round.hospital_a_accuracy * 100);
                flChart.data.datasets[1].data.push(round.hospital_b_accuracy * 100);
                flChart.data.datasets[2].data.push(round.global_model_accuracy * 100);
                flChart.update();
            }

            // Update accuracy displays
            document.getElementById('acc-node-a').textContent = (round.hospital_a_accuracy * 100).toFixed(1) + '%';
            document.getElementById('acc-node-b').textContent = (round.hospital_b_accuracy * 100).toFixed(1) + '%';
            document.getElementById('acc-global').textContent = (round.global_model_accuracy * 100).toFixed(1) + '%';

            await new Promise(r => setTimeout(r, 400));
            document.querySelectorAll('.node-card').forEach(n => n.classList.remove('training'));
        }

        // Final status
        document.getElementById('status-node-a').textContent = 'Complete';
        document.getElementById('status-node-b').textContent = 'Complete';
        document.getElementById('status-global').textContent = 'Trained';
        document.querySelectorAll('.node-card').forEach(n => n.classList.add('active'));

        const finalDiv = document.createElement('div');
        finalDiv.className = 'fl-complete';
        finalDiv.innerHTML = `
            <i class="fa-solid fa-check-circle"></i>
            <span>Training Complete! Final Global Accuracy: <strong>${(result.final_accuracy * 100).toFixed(1)}%</strong></span>
        `;
        viz.appendChild(finalDiv);

    } catch (e) {
        viz.innerHTML = `<div class="fl-error"><i class="fa-solid fa-exclamation-circle"></i> Error: ${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Start Training';
    }
}

// --- Analytics ---
async function fetchThreatIntel() {
    try {
        const res = await fetch('/threat-intel');
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const intel = await res.json();
        
        // Update threat intelligence summary
        document.getElementById('intel-total').textContent = intel.total_threats || 0;
        document.getElementById('intel-detected').textContent = intel.detected || 0;
        document.getElementById('intel-blocked').textContent = intel.blocked || 0;
        document.getElementById('intel-rate').textContent = (intel.detection_rate || 0) + '%';
        
        // Update pie chart
        if (threatPieChart && intel.by_type) {
            threatPieChart.data.datasets[0].data = [
                intel.by_type.spike || 0,
                intel.by_type.flatline || 0,
                intel.by_type.noise || 0,
                intel.by_type.spoof || 0,
                intel.by_type.replay || 0,
                intel.by_type.mitm || 0
            ];
            threatPieChart.update();
        }
        
        // Update timeline chart with recent threats
        if (timelineChart) {
            if (intel.recent && intel.recent.length > 0) {
                // Get last 50 threats for better timeline view
                const recent = intel.recent.slice(-50);
                const threatCounts = {};
                
                // Group threats by 1-minute intervals
                recent.forEach(t => {
                    if (t.timestamp) {
                        try {
                            const date = new Date(t.timestamp);
                            if (!isNaN(date.getTime())) {
                                // Round to nearest minute
                                const rounded = new Date(date);
                                rounded.setSeconds(0, 0);
                                
                                // Format as HH:MM
                                const hours = rounded.getHours().toString().padStart(2, '0');
                                const minutes = rounded.getMinutes().toString().padStart(2, '0');
                                const timeKey = `${hours}:${minutes}`;
                                
                                threatCounts[timeKey] = (threatCounts[timeKey] || 0) + 1;
                            }
                        } catch (e) {
                            console.warn('Invalid timestamp:', t.timestamp);
                        }
                    }
                });
                
                // Sort by time and get last 20 time buckets (or all if less than 20)
                const sortedEntries = Object.entries(threatCounts)
                    .sort((a, b) => {
                        const timeA = a[0].split(':').map(Number);
                        const timeB = b[0].split(':').map(Number);
                        const minutesA = timeA[0] * 60 + timeA[1];
                        const minutesB = timeB[0] * 60 + timeB[1];
                        return minutesA - minutesB;
                    });
                
                // If we have data, show it
                if (sortedEntries.length > 0) {
                    const displayEntries = sortedEntries.slice(-20); // Show last 20 buckets
                    const labels = displayEntries.map(([time]) => time);
                    const data = displayEntries.map(([, count]) => count);
                    
                    // Set colors based on threat count
                    const backgroundColors = data.map(count => {
                        if (count >= 5) return 'rgba(239, 68, 68, 0.8)'; // High - red
                        if (count >= 2) return 'rgba(245, 158, 11, 0.8)'; // Medium - orange
                        return 'rgba(59, 130, 246, 0.6)'; // Low - blue
                    });
                    
                    const borderColors = data.map(count => {
                        if (count >= 5) return '#ef4444';
                        if (count >= 2) return '#f59e0b';
                        return '#3b82f6';
                    });
                    
                    timelineChart.data.labels = labels;
                    timelineChart.data.datasets[0].data = data;
                    timelineChart.data.datasets[0].backgroundColor = backgroundColors;
                    timelineChart.data.datasets[0].borderColor = borderColors;
                    timelineChart.update('active');
                } else {
                    // No valid timestamps, show empty
                    timelineChart.data.labels = [];
                    timelineChart.data.datasets[0].data = [];
                    timelineChart.data.datasets[0].backgroundColor = [];
                    timelineChart.data.datasets[0].borderColor = [];
                    timelineChart.update();
                }
            } else {
                // No threats yet - show empty chart with placeholder
                timelineChart.data.labels = [];
                timelineChart.data.datasets[0].data = [];
                timelineChart.update();
            }
        }
    } catch (e) {
        console.error('Failed to fetch threat intel:', e);
        // Show error message
        const intelGrid = document.getElementById('intel-grid');
        if (intelGrid) {
            intelGrid.innerHTML = '<div style="color: var(--danger); text-align: center; padding: 20px;">Error loading threat intelligence</div>';
        }
    }
}

// --- Settings ---
async function fetchModelStatus() {
    try {
        const res = await fetch('/model/status');
        const status = await res.json();
        
        document.getElementById('setting-accuracy').textContent = status.accuracy + '%';
        document.getElementById('setting-retrain').textContent = status.last_retrain || 'Initial training';
    } catch (e) { }
}

async function retrainModel() {
    const btn = event.currentTarget;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Retraining...';
    
    try {
        const res = await fetch('/model/retrain', { method: 'POST' });
        const result = await res.json();
        
        document.getElementById('setting-accuracy').textContent = result.new_accuracy + '%';
        document.getElementById('accuracy-value').textContent = Math.round(result.new_accuracy);
        document.getElementById('setting-retrain').textContent = 'Just now';
        
        logAlert({
            attack_type: 'SYSTEM',
            severity: 'low',
            threat_details: `Model retrained successfully. New accuracy: ${result.new_accuracy}%`
        });
    } catch (e) {
        console.error('Retrain failed:', e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-rotate"></i> Retrain Model';
    }
}

function toggleSound() {
    soundEnabled = document.getElementById('sound-toggle').checked;
}

function toggleNotifications() {
    notificationsEnabled = document.getElementById('notif-toggle').checked;
    if (notificationsEnabled && Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
}

function updateInterval(value) {
    updateIntervalMs = parseInt(value);
    document.getElementById('interval-value').textContent = value + 'ms';
    startDataStreams();
}

function updateHistory(value) {
    maxPoints = parseInt(value);
    document.getElementById('history-value').textContent = value;
}

function clearChart() {
    vitalsChart.data.labels = [];
    vitalsChart.data.datasets.forEach(d => d.data = []);
    vitalsChart.update();
}

function toggleChartType() {
    const currentType = vitalsChart.config.type;
    vitalsChart.config.type = currentType === 'line' ? 'bar' : 'line';
    vitalsChart.update();
}

// --- Initialize ---
document.addEventListener('DOMContentLoaded', () => {
    fetchSessionStats();
    fetchModelStatus();
});
