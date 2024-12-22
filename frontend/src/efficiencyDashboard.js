import Chart from 'chart.js/auto';

document.addEventListener("DOMContentLoaded", function () {
    // Element references based on updated IDs
    const processedTodayElement = document.querySelector('#processedToday');
    const meanConfidenceElement = document.querySelector('#meanConfidence');
    const processingTimeElement = document.querySelector('#processing_last_6');

    const renderLineChart = (canvasId, labels, data, label) => {
        const ctx = document.getElementById(canvasId).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label,
                    data,
                    borderColor: '#00E396',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true, position: 'bottom' },
                    tooltip: { mode: 'index', intersect: false },
                },
                scales: {
                    x: { title: { display: true, text: 'Date' } },
                    y: { title: { display: true, text: label } },
                },
            },
        });
    };

    fetch('http://127.0.0.1:5000/api/inference_requests')
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                throw new Error('Unexpected API response format. Expected an array of requests.');
            }

            console.log("All Requests:", data);

            const now = new Date();
            const past24Hours = new Date(now.getTime() - (24 * 60 * 60 * 1000)); // 24 hours ago
            const past30Days = new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000)); // 30 days ago

            // Filter requests
            const last24HoursRequests = data.filter(request => new Date(request.request_creation) > past24Hours);
            const last30DaysRequests = data.filter(request => new Date(request.request_creation) > past30Days);

            console.log("Last 24 Hours Requests:", last24HoursRequests);
            console.log("Last 30 Days Requests:", last30DaysRequests);

            // Processed today (requests processed today)
            const processedToday = last24HoursRequests.length;
            processedTodayElement.textContent = processedToday;

            // Mean confidence rate
            const totalConfidence = last30DaysRequests.reduce(
                (sum, request) => sum + (request.confidence_level || 0),
                0
            );
            const meanConfidence = last30DaysRequests.length > 0
                ? (totalConfidence / last30DaysRequests.length * 100).toFixed(2)
                : 0;
            meanConfidenceElement.textContent = `${meanConfidence}%`;

            console.log("Processed Today (Last 24hr):", processedToday);
            console.log("Mean Confidence Level (Last 30 Days):", meanConfidence);

            // Average processing time
            const processingTimes = last30DaysRequests.map(request => {
                const requestCreationTime = new Date(request.request_creation).getTime();
                const answerTime = new Date(request.answer_time).getTime();
                return answerTime - requestCreationTime;
            });
            const totalProcessingTime = processingTimes.reduce((sum, time) => sum + time, 0);
            const avgProcessingTimeInSeconds = processingTimes.length > 0
                ? (totalProcessingTime / processingTimes.length / 1000).toFixed(2)
                : 0;
            processingTimeElement.textContent = `${avgProcessingTimeInSeconds}s`;

            // Daily averages for the last 30 days (Processing Rate)
            const dailyProcessingAverages = {};
            last30DaysRequests.forEach(request => {
                const creationDate = new Date(request.request_creation).toISOString().split('T')[0];
                if (!dailyProcessingAverages[creationDate]) {
                    dailyProcessingAverages[creationDate] = { count: 0 };
                }
                dailyProcessingAverages[creationDate].count += 1;
            });

            const processingLabels = Object.keys(dailyProcessingAverages).sort();
            const processingDataPoints = processingLabels.map(date => dailyProcessingAverages[date].count);

            // Daily averages for the last 30 days (Confidence Level)
            const dailyConfidenceAverages = {};
            last30DaysRequests.forEach(request => {
                const creationDate = new Date(request.request_creation).toISOString().split('T')[0];
                if (!dailyConfidenceAverages[creationDate]) {
                    dailyConfidenceAverages[creationDate] = { count: 0, total: 0 };
                }
                dailyConfidenceAverages[creationDate].count += 1;
                dailyConfidenceAverages[creationDate].total += (request.confidence_level || 0);
            });

            const confidenceLabels = Object.keys(dailyConfidenceAverages).sort();
            const confidenceDataPoints = confidenceLabels.map(date => {
                const { count, total } = dailyConfidenceAverages[date];
                return (total / count * 100).toFixed(2); // Daily average confidence
            });

            // Render line charts
            renderLineChart('processingChart', processingLabels, processingDataPoints, 'Daily Processing Rate');
            renderLineChart('confidenceChart', confidenceLabels, confidenceDataPoints, 'Mean Confidence Level (%)');
        })
        .catch(error => {
            console.error('Error fetching or processing inference request data:', error);
        });
});
