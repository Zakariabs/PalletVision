import React, { useEffect, useState } from 'react';

const InferenceRequestList = () => {
    const [requests, setRequests] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/inference_requests')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => setRequests(data))
            .catch(error => {
                console.error('Error fetching data:', error);
                setError(error.message);
            });
    }, []);
    return (
        <div>
            <h1>Inference Requests</h1>
            {error ? (
                <div>Error: {error}</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Request ID</th>
                            <th>Station Name</th>
                            <th>Initial Image ID</th>
                            <th>Inferred Image ID</th>
                            <th>Request Creation</th>
                            <th>Answer Time</th>
                            <th>Status</th>
                            <th>Confidence Level</th>
                            <th>Pallet Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {requests.map(request => (
                            <tr key={request.id}>
                                <td>{request.request_id}</td>
                                <td>{request.station_name}</td>
                                <td>{request.initial_image_id}</td>
                                <td>{request.inferred_image_id}</td>
                                <td>{request.request_creation}</td>
                                <td>{request.answer_time}</td>
                                <td>{request.status_name}</td>
                                <td>{request.confidence_level ? request.confidence_level.toFixed(2) : 'N/A'}</td>
                                <td>{request.pallet_type}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default InferenceRequestList;
