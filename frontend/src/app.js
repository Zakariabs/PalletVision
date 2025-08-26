// PalletVision Frontend - Single Bundle Application

// Global state
let jwtToken = localStorage.getItem("jwtToken");
const API_BASE = 'http://127.0.0.1:5000';

// Utility functions
function loadPartial(id, file) {
    fetch(file)
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load ${file}`);
            return response.text();
        })
        .then(html => {
            document.getElementById(id).innerHTML = html;
        })
        .catch(error => console.error(`Error loading ${file}:`, error));
}

function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
    }
    
    return fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });
}

// Authentication functions
function login() {
    const username = document.getElementById('username')?.value;
    const password = document.getElementById('password')?.value;
    
    if (!username || !password) {
        alert('Please enter username and password');
        return;
    }
    
    apiRequest('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            jwtToken = data.access_token;
            localStorage.setItem("jwtToken", jwtToken);
            window.location.href = 'pages/managerDashboard.html';
        } else {
            alert('Login failed: ' + (data.msg || 'Invalid credentials'));
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        alert('Login failed. Please try again.');
    });
}

// Dashboard functions
function loadManagerDashboard() {
    // Load pallet count charts
    apiRequest('/api/pallet_count')
        .then(response => response.json())
        .then(data => {
            if (window.ApexCharts) {
                createPalletCharts(data);
            } else {
                console.warn('ApexCharts not loaded, using simple display');
                displayPalletData(data);
            }
        })
        .catch(error => console.error('Error loading pallet data:', error));
    
    // Load station status
    apiRequest('/api/stations')
        .then(response => response.json())
        .then(data => {
            displayStationStatus(data);
        })
        .catch(error => console.error('Error loading stations:', error));
}

function createPalletCharts(data) {
    // 7 days chart
    const chart7Days = {
        chart: { type: "donut", height: 250 },
        series: data.last_7_days.map(item => item.count),
        labels: data.last_7_days.map(item => item.pallet_type || "Unknown"),
        title: { text: "Pallet Count - Last 7 Days", align: "center" },
        colors: ["#008FFB", "#00E396", "#000000", "#FF4560"]
    };
    
    // 30 days chart
    const chart30Days = {
        chart: { type: "donut", height: 250 },
        series: data.last_30_days.map(item => item.count),
        labels: data.last_30_days.map(item => item.pallet_type || "Unknown"),
        title: { text: "Pallet Count - Last 30 Days", align: "center" },
        colors: ["#008FFB", "#00E396", "#FEB019", "#FF4560"]
    };
    
    try {
        new ApexCharts(document.querySelector("#palletCountChart7Days"), chart7Days).render();
        new ApexCharts(document.querySelector("#palletCountChart30Days"), chart30Days).render();
    } catch (error) {
        console.error('Chart rendering error:', error);
        displayPalletData(data);
    }
}

function displayPalletData(data) {
    // Fallback display without charts
    const chart7Element = document.querySelector("#palletCountChart7Days");
    const chart30Element = document.querySelector("#palletCountChart30Days");
    
    if (chart7Element) {
        chart7Element.innerHTML = `
            <h6>Last 7 Days</h6>
            ${data.last_7_days.map(item => `<p>${item.pallet_type}: ${item.count}</p>`).join('')}
        `;
    }
    
    if (chart30Element) {
        chart30Element.innerHTML = `
            <h6>Last 30 Days</h6>
            ${data.last_30_days.map(item => `<p>${item.pallet_type}: ${item.count}</p>`).join('')}
        `;
    }
}

function displayStationStatus(stations) {
    const tbody = document.querySelector("#stationStatusTable tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    stations.forEach(station => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${station.station_name}</td>
            <td class="${station.status_class}">${station.station_status}</td>
            <td>
                <a href="stationDetails.html?station_id=${station.station_id}" class="btn btn-primary btn-sm">View Details</a>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function loadStationDashboard() {
    const stationId = new URLSearchParams(window.location.search).get("station_id");
    if (!stationId) {
        console.error("No station_id provided in the URL");
        return;
    }
    
    // Load station details
    apiRequest(`/api/stations/${stationId}`)
        .then(response => response.json())
        .then(station => {
            updateStationInfo(station);
            return station;
        })
        .then(station => {
            updateStationImage(stationId, station.station_status);
        })
        .catch(error => console.error('Error loading station details:', error));
    
    // Load inference requests
    loadInferenceRequests(stationId);
}

function updateStationInfo(station) {
    const nameElement = document.getElementById("station-name");
    const statusElement = document.getElementById("station-status");
    const infoElement = document.getElementById("station-info");
    
    if (nameElement) nameElement.textContent = station.station_name;
    
    if (statusElement) {
        const statusIndicator = statusElement.querySelector(".status-indicator");
        if (statusIndicator) statusIndicator.textContent = station.station_status;
        statusElement.className = `status-box p-3 rounded text-white ${station.status_class}`;
    }
    
    if (infoElement) infoElement.style.display = "flex";
}

function updateStationImage(stationId, stationStatus) {
    const imageBox = document.querySelector(".image-box");
    const placeholder = document.querySelector(".image-placeholder");
    
    if (stationStatus === "Offline") {
        if (placeholder) placeholder.style.display = "none";
        return;
    }
    
    apiRequest(`/api/stations/${stationId}/current_image`)
        .then(response => response.json())
        .then(data => {
            if (data.image && imageBox) {
                imageBox.innerHTML = `
                    <img src="${data.image}" alt="Station Image" class="station-image">
                    <p class="text-muted">${stationStatus === "Processing" ? "Waiting for answer" : "Last processed image"}</p>
                `;
                if (placeholder) placeholder.style.display = "block";
            } else if (placeholder) {
                placeholder.style.display = "none";
            }
        })
        .catch(error => console.error('Error fetching station image:', error));
}

function loadInferenceRequests(stationId) {
    apiRequest(`/api/stations/${stationId}/inference_requests`)
        .then(response => response.json())
        .then(requests => {
            displayInferenceRequests(requests);
        })
        .catch(error => console.error('Error loading inference requests:', error));
}

function displayInferenceRequests(requests) {
    const tbody = document.getElementById("inference-requests");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    requests.forEach(request => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${request.answer_time ? new Date(request.answer_time).toLocaleString() : 'Processing...'}</td>
            <td>${request.pallet_type || 'Unknown'}</td>
            <td>
                ${request.initial_image_path ? 
                    `<img src="${request.initial_image_path}" alt="Initial Image" class="table-image">` :
                    '<span class="text-muted">No Image</span>'
                }
            </td>
            <td>
                ${request.inferred_image_path ? 
                    `<img src="${request.inferred_image_path}" alt="Inferred Image" class="table-image">` :
                    '<span class="text-muted">No Image</span>'
                }
            </td>
            <td>${request.confidence_level ? (request.confidence_level * 100).toFixed(2) + '%' : 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

function loadAllRequests() {
    apiRequest('/api/inference_requests')
        .then(response => response.json())
        .then(requests => {
            displayAllInferenceRequests(requests);
        })
        .catch(error => console.error('Error loading all requests:', error));
}

function displayAllInferenceRequests(requests) {
    const tbody = document.querySelector("#allInferenceRequestsTable tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    requests.forEach(request => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${new Date(request.request_creation).toLocaleString()}</td>
            <td>${request.station_name || 'Unknown'}</td>
            <td>${request.pallet_type || 'Unknown'}</td>
            <td>${request.status || 'Unknown'}</td>
            <td>${request.confidence_level ? (request.confidence_level * 100).toFixed(2) + '%' : 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

function loadLogs() {
    apiRequest('/api/logs')
        .then(response => response.json())
        .then(logs => {
            displayLogs(logs);
        })
        .catch(error => console.error('Error loading logs:', error));
}

function displayLogs(logs) {
    const tbody = document.querySelector("#logsTable tbody");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    logs.forEach(log => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${new Date(log.timestamp).toLocaleString()}</td>
            <td><span class="badge badge-info">${log.category}</span></td>
            <td>${log.message || 'No message'}</td>
            <td>${log.initial_image ? 
                `<img src="${log.initial_image}" alt="Log Image" class="table-image">` : 
                'No image'
            }</td>
        `;
        tbody.appendChild(row);
    });
}

// Page-specific initialization
document.addEventListener("DOMContentLoaded", function () {
    // Load partials
    loadPartial("header", "/partials/header.html");
    loadPartial("footer", "/partials/footer.html");
    
    // Check which page we're on and initialize accordingly
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'index.html';
    
    if (page.includes('manager')) {
        loadManagerDashboard();
    } else if (page.includes('station')) {
        loadStationDashboard();
    } else if (page.includes('requests')) {
        loadAllRequests();
    } else if (page.includes('logs')) {
        loadLogs();
    }
    
    // Bind login form if exists
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            login();
        });
    }
    
    // Bind login button if exists
    const loginButton = document.getElementById('loginButton');
    if (loginButton) {
        loginButton.addEventListener('click', login);
    }
});

// Make functions available globally for onclick handlers
window.login = login;
window.loadManagerDashboard = loadManagerDashboard;
window.loadStationDashboard = loadStationDashboard;
window.loadAllRequests = loadAllRequests;
window.loadLogs = loadLogs;