
document.addEventListener("DOMContentLoaded", function () {
    // Fetch and render pallet count chart
    const token = localStorage.getItem('jwtToken');
    fetch('http://127.0.0.1:5000/api/pallet_count', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch chart data');
            }
            return response.json();
        })
        .then(data => {
            console.log('Pallet Count API Response:', data);

            // Prepare data for last 7 days
            const last7DaysData = data.last_7_days.map(item => item.count);
            const last7DaysLabels = data.last_7_days.map(item => item.pallet_type ?? 'Unknown');

            // Prepare data for last 30 days
            const last30DaysData = data.last_30_days.map(item => item.count);
            const last30DaysLabels = data.last_30_days.map(item => item.pallet_type ?? 'Unknown');
            // Chart options for last 7 days
            const options7Days = {
                chart: {
                    type: 'donut',
                    height: 250,
                },
                series: last7DaysData,
                labels: last7DaysLabels,
                title: {
                    text: 'Pallet Count - Last 7 Days',
                    align: 'center',
                },
                colors: ['#008FFB', '#00E396', '#000000', '#FF4560'],
            };
        // Prepare data for last 30 days
        const last30DaysData = data.last_30_days.map(item => item.count);
        const last30DaysLabels = data.last_30_days.map(item => item.pallet_type ?? 'Unknown');
        // Chart options for last 7 days
        const options7Days = {
            chart: {
                type: 'donut',
                height: 250,
            },
            series: last7DaysData,
            labels: last7DaysLabels,
            title: {
                text: 'Pallet Count - Last 7 Days',
                align: 'center',
            },
            colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560'],
        };

            // Chart options for last 30 days
            const options30Days = {
                chart: {
                    type: 'donut',
                    height: 250,
                },
                series: last30DaysData,
                labels: last30DaysLabels,
                title: {
                    text: 'Pallet Count - Last 30 Days',
                    align: 'center',
                },
                colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560'],
            };

        // Render charts
        const chart7Days = new ApexCharts(document.querySelector("#palletCountChart7Days"), options7Days);
        const chart30Days = new ApexCharts(document.querySelector("#palletCountChart30Days"), options30Days);

        chart7Days.render();
        chart30Days.render();
    })
    .catch(error => {
        console.error('Error fetching chart data:', error);
    });

    // Fetch and render station statuses
    fetch('http://127.0.0.1:5000/api/stations', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch station data');
            }
            return response.json();
        })
        .then(stations => {
            console.log('Stations API Response:', stations); // Log the received data for debugging

            const stationTableBody = document.querySelector("#stationStatusTable tbody");
            stationTableBody.innerHTML = ''; // Clear any existing rows

            stations.forEach(station => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${station.station_name}</td>
                    <td class="${station.status_class}">${station.station_status}</td>
                    <td>
                        <a href="stationDetails.html?station_id=${station.station_id}" class="btn btn-primary btn-sm">View Details</a>
                    </td>
                `;
                stationTableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching station data:', error);
        });
});
