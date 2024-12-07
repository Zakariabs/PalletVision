document.addEventListener("DOMContentLoaded", function () {
    // Fetch and update station info
    fetch('/api/station-dashboard') // Replace with your actual API endpoint
        .then(response => response.json())
        .then(data => {
            // Update Station Name
            document.getElementById('station-name').textContent = data.station_name;

            // Update Station Status
            const statusBox = document.getElementById('station-status');
            statusBox.classList.add(data.status.class);
            statusBox.querySelector('.status-indicator').textContent = data.status.text;

            // Populate Inference Requests Table
            const tableBody = document.getElementById('inference-requests');
            tableBody.innerHTML = ''; // Clear existing rows
            data.inference_requests.forEach(request => {
                const row = `
                    <tr>
                        <td>${request.answer_timestamp}</td>
                        <td>${request.pallet_type}</td>
                        <td>
                            ${request.initial_image
                                ? `<img src="${request.initial_image}" alt="Initial Image" class="table-image">`
                                : '<span class="text-muted">No Image</span>'}
                        </td>
                        <td>
                            ${request.inferred_image
                                ? `<img src="${request.inferred_image}" alt="Inferred Image" class="table-image">`
                                : '<span class="text-muted">No Image</span>'}
                        </td>
                        <td>${request.confidence_level}%</td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
        })
        .catch(error => console.error('Error fetching station dashboard data:', error));
});
