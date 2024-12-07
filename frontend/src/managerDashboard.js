document.addEventListener("DOMContentLoaded", function () {
    // Fetch and render pallet count chart
    fetch('/chart_data/pallet_count')
        .then(response => response.json())
        .then(data => {
            var options = {
                chart: {
                    type: 'bar',
                    height: 200,
                },
                series: [
                    { name: 'Last 7 Days', data: data.last_7_days },
                    { name: 'Last 30 Days', data: data.last_30_days },
                ],
                xaxis: {
                    categories: data.labels,
                },
                title: {
                    text: 'Pallet Count Per Type',
                },
            };

            var chart = new ApexCharts(document.querySelector("#palletCountChart"), options);
            chart.render();
        });

});
