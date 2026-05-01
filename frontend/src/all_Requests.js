let inferenceRequestsData = [];
let stationsData = [];
const token = localStorage.getItem('jwtToken');
const API_BASE = 'http://localhost:5000';

const toImageUrl = (p) => {
    if (!p) return null;
    if (/^https?:\/\//i.test(p)) return p;
    const idx = p.indexOf('/app/images/');
    const rel = idx >= 0 ? p.slice(idx + '/app/images/'.length) : p.replace(/^\/+/, '');
    return `${API_BASE}/images/${rel}`;
};

const reviewBadge = (flagged) => flagged
    ? '<span class="badge bg-warning text-dark">Review</span>'
    : '<span class="badge bg-success">OK</span>';

// Function to populate the table
const populateTable = (requests) => {
    const tableBody = document.getElementById('inference-requests');
    tableBody.innerHTML = ''; // Clear existing rows
    requests.forEach(request => {
        const initialUrl = toImageUrl(request.initial_image_path);
        const annotatedUrl = toImageUrl(request.inferred_image_path);
        const row = `
            <tr>
                <td>${new Date(request.answer_time).toLocaleString()}</td>
                <td>${request.station_name}</td>
                <td>${request.pallet_type}</td>
                <td>
                    ${initialUrl
                        ? `<img src="${initialUrl}" alt="Initial Image" class="table-image">`
                        : '<span class="text-muted">No Image</span>'}
                </td>
                <td>
                    ${annotatedUrl
                        ? `<img src="${annotatedUrl}" alt="Annotated Image" class="table-image">`
                        : '<span class="text-muted">No Image</span>'}
                </td>
                <td>${(request.confidence_level * 100).toFixed(2)}%</td>
                <td>${request.model_version || '<span class="text-muted">—</span>'}</td>
                <td>${reviewBadge(request.flagged_for_review)}</td>
            </tr>
        `;
        tableBody.insertAdjacentHTML('afterbegin', row);
    });
};


// Function to fetch and display inference requests
const fetchInferenceRequests =() => {
    fetch('http://127.0.0.1:5000/api/inference_requests',{
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
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
