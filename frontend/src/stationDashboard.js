let inferenceRequestsData = [];
let stationsData = [];

// Utility function to get URL query parameters
const getQueryParam = (key) => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(key);
};

// Get the station_id from the URL query parameters
const stationId = getQueryParam('station_id');




// Function to populate the table
const populateTable = (requests) => {
    const tableBody = document.getElementById('inference-requests');
    tableBody.innerHTML = ''; // Clear existing rows
    requests.forEach(request => {
        const row = `
            <tr>
                <td>${new Date(request.answer_time).toLocaleString()}</td>
                <td>${request.pallet_type}</td>
                <td>
                    ${request.initial_image_path
                        ? `<img src="${request.initial_image_path.replace('/app/app/ai_service/images/', 'http://localhost:5000/images/')}" alt="Initial Image" class="table-image">`
                        : '<span class="text-muted">No Image</span>'}
                </td>
                <td>
                    ${request.inferred_image_path
                        ? `<img src="${request.inferred_image_path.replace('/app/app/ai_service/', 'http://localhost:5000/images/')}" alt="Inferred Image" class="table-image">`
                        : '<span class="text-muted">No Image</span>'}
                </td>
                <td>${(request.confidence_level * 100).toFixed(2)}%</td>
            </tr>
        `;
        tableBody.insertAdjacentHTML('beforeend', row);
    });
};

// Function to fetch and display station details
const fetchStationDetails = (stationId) => {
    fetch(`http://127.0.0.1:5000/api/stations/${stationId}`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch station details');
            return response.json();
        })

        .then(station => {
            // Update station details
            const stationNameElement = document.getElementById('station-name');
            const stationInfoElement = document.getElementById('station-info');
            const stationStatusElement = document.getElementById('station-status');
            const statusIndicatorElement = stationStatusElement.querySelector('.status-indicator');

            stationNameElement.textContent = station.station_name;
            statusIndicatorElement.textContent = station.station_status;
            stationStatusElement.className = `status-box p-3 rounded text-white ${station.status_class}`;

            stationInfoElement.style.display = 'flex';
            statusIndicatorElement.style.display = 'inline';
        })
        .catch(error => console.error('Error fetching station details:', error));
};

// Function to fetch and display inference requests for a specific station
const fetchInferenceRequests = (stationId) => {
    fetch(`http://127.0.0.1:5000/api/stations/${stationId}/inference_requests`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch inference requests');
            return response.json();
        })
        .then(requests => {
            populateTable(requests); // Populate table with filtered requests
        })
        .catch(error => console.error('Error fetching inference requests:', error));
};

// Check if station_id exists and fetch details
if (stationId) {
    fetchStationDetails(stationId); // Fetch and display station details
    fetchInferenceRequests(stationId); // Fetch and display inference requests
} else {
    console.error('No station_id provided in the URL');
}

