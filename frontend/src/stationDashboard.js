let inferenceRequestsData = [];
let stationsData = [];
const token = localStorage.getItem('jwtToken');
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

// Function to filter and display station details
const updateStationDetails = (selectedStationName) => {
    const stationNameElement = document.getElementById('station-name');
    const stationInfoElement = document.getElementById('station-info');
    const stationStatusElement = document.getElementById('station-status');
    const statusIndicatorElement = stationStatusElement.querySelector('.status-indicator');

    if (selectedStationName) {
        const selectedStationData = stationsData.find(station => station.station_name === selectedStationName);
        if (selectedStationData) {
            stationNameElement.textContent = selectedStationData.station_name;
            statusIndicatorElement.textContent = selectedStationData.station_status;
            stationStatusElement.className = `status-box p-3 rounded text-white ${selectedStationData.status_class}`;

            stationNameElement.style.display = 'block';
            stationInfoElement.style.display = 'flex';
            statusIndicatorElement.style.display = 'inline';
        }
    } else {
        stationNameElement.textContent = 'Stations';
        stationNameElement.style.display = 'block';
        stationInfoElement.style.display = 'none';
        statusIndicatorElement.style.display = 'none'; // Hide the status text
    }
};

// Event listener for the station dropdown change
const onStationChange = (event) => {
    const selectedStationName = event.target.value;

    // Update station details
    updateStationDetails(selectedStationName);

    // Filter and display the inference requests
    const filteredRequests = selectedStationName
        ? inferenceRequestsData.filter(request => request.station_name === selectedStationName)
        : inferenceRequestsData;

    populateTable(filteredRequests);
};

// Fetch stations and populate the dropdown
fetch('http://127.0.0.1:5000/api/stations', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
    .then(response => {
        if (!response.ok) throw new Error('Failed to fetch station data');
        return response.json();
    })
    .then(stations => {
        stationsData = stations; // Store the data in a global variable
        const stationSelect = document.getElementById('station-select');
        stationSelect.innerHTML = '<option value="">All Stations</option>'; // Add default option

        stations.forEach(station => {
            const option = document.createElement('option');
            option.value = station.station_name;
            option.textContent = `${station.station_name} (${station.station_status})`;
            stationSelect.appendChild(option);
        });

        // Attach event listener once after stations are loaded
        stationSelect.addEventListener('change', onStationChange);
    })
    .catch(error => console.error('Error fetching station data:', error));

// Fetch inference requests and populate the table

fetch('http://127.0.0.1:5000/api/inference_requests', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
    .then(response => {
        if (!response.ok) throw new Error('Failed to fetch inference requests');
        return response.json();
    })
    .then(data => {
        inferenceRequestsData = data; // Store the data in a global variable

        // Populate table with all requests
        populateTable(data);
    })
    .catch(error => console.error('Error fetching inference requests data:', error));
