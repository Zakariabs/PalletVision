document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem('jwtToken');
    const past30DayRequestElement = document.querySelector('.card-body h3.text-warning');
    const confidenceRateElement = document.querySelectorAll('.card-body h3.text-warning')[1];
    const processingTimeElement = document.querySelector('.gauge-box p.display-4');

    fetch('http://127.0.0.1:5000/api/inference_requests', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                throw new Error('Unexpected API response format. Expected an array of requests.');
            }


            const now = new Date();
            const past30DaysRequests = data.filter(request => {
                const requestCreationTime = new Date(request.request_creation);
                return (now - requestCreationTime) <= (30 * 24 * 60 * 60 * 1000); // 30 days in ms
            });
            const requestCount = past30DaysRequests.length;
            past30DayRequestElement.textContent = requestCount;

            const recognizedPalletTypeCount = past30DaysRequests.filter(request => request.pallet_type).length;
            const recognizedPalletTypeRate = requestCount > 0 ? ((recognizedPalletTypeCount / requestCount) * 100).toFixed(2) : 0;


            const processingTimes = past30DaysRequests.map(request => {
                const requestCreationTime = new Date(request.request_creation).getTime();
                const answerTime = new Date(request.answer_time).getTime();
                return answerTime - requestCreationTime;
            });

            const confidenceLevels = past30DaysRequests.map(request => request.confidence_level);
            const totalConfidenceLevel = confidenceLevels.reduce((sum, level) => sum + level, 0);
            const avgConfidenceRate = confidenceLevels.length > 0
                ? (totalConfidenceLevel / confidenceLevels.length *100).toFixed(2)
                : 0;

            const totalProcessingTime = processingTimes.reduce((sum, time) => sum + time, 0);
            const avgProcessingTime = processingTimes.length > 0
                ? (totalProcessingTime / processingTimes.length).toFixed(2)
                : 0;


            const avgProcessingTimeInSeconds = (avgProcessingTime / 1000).toFixed(2);
            processingTimeElement.textContent = `${avgProcessingTimeInSeconds}s`;
            confidenceRateElement.textContent = `${avgConfidenceRate}%`;
            // Debug log for review
            console.log({
                requestCount,
                confidenceRateElement,
                avgProcessingTime,
                avgProcessingTimeInSeconds,
                totalProcessingTime
            });
        })
        .catch(error => {
            console.error('Error fetching or processing inference request data:', error);
        });
});
