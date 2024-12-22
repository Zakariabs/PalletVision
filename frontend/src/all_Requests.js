let inferenceRequestsData = [];
let stationsData = [];



// Function to populate the table
const populateTable = (requests) => {
    const tableBody = document.getElementById('inference-requests');
    tableBody.innerHTML = ''; // Clear existing rows
    requests.forEach(request => {
        const row = `
            <tr>
                <td>${new Date(request.answer_time).toLocaleString()}</td>
                <td>${request.station_name}</td>           
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
        tableBody.insertAdjacentHTML('afterbegin', row);
    });
};


// Function to fetch and display inference requests
const fetchInferenceRequests =() => {
    fetch(`http://127.0.0.1:5000/api/inference_requests`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch inference requests');
            return response.json();
        })
        .then(requests => {
            populateTable(requests); // Populate table with requests
        })
        .catch(error => console.error('Error fetching inference requests:', error));
};



fetchInferenceRequests();
