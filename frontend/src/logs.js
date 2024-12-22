// Function to populate the logs table
const populateLogsTable = (logs) => {
    const tableBody = document.getElementById('logs');
    tableBody.innerHTML = ''; // Clear existing rows
    logs.forEach(log => {
        const row = `
            <tr>
                <td>${new Date(log.timestamp).toLocaleString()}</td>
                <td>${log.category}</td>
                <td>${log.message}</td>
                <td>
                    ${log.initial_image
                        ? `<img src="${log.initial_image.replace('/app/app/ai_service/images/', 'http://localhost:5000/images/')}" alt="Initial Image" class="table-image">`
                        : '<span class="text-muted">No Image</span>'}
                </td>

            
            </tr>
        `;
        tableBody.insertAdjacentHTML('beforeend', row);
    });
};

// Function to fetch logs
const fetchLogs = () => {
    const token = localStorage.getItem('jwtToken');
    fetch('http://127.0.0.1:5000/api/logs', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch logs');
            }
            return response.json();
        })
        .then(logs => {
            populateLogsTable(logs); // Populate the table with logs
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
        });
};

// Fetch logs when the page loads
fetchLogs();
