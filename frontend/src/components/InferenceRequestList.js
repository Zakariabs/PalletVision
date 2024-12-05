import React, { useEffect, useState } from 'react';

const InferenceRequestList = () => {
    const [requests, setRequests] = useState([]);

    useEffect(() => {
        fetch('http://backend:5000/api/inference_requests')
            .then(response => response.json())
            .then(data => setRequests(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    return (
        <div>
            <h1>Inference Requests</h1>
            <table>
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Station ID</th>
                        <th>Initial Image ID</th>
                        <th>Inferred Image ID</th>
                        <th>Request Creation</th>
                        <th>Answer Time</th>
                        <th>Status ID</th>
                        <th>Confidence Level</th>
                        <th>Pallet Type</th>
                    </tr>
                </thead>
                <tbody>
                    {requests.map(request => (
                        <tr key={request.request_id}>
                            <td>{request.request_id}</td>
                            <td>{request.station_id}</td>
                            <td>{request.initial_image_id}</td>
                            <td>{request.inferred_image_id}</td>
                            <td>{request.request_creation}</td>
                            <td>{request.answer_time}</td>
                            <td>{request.status_id}</td>
                            <td>{request.confidence_level}</td>
                            <td>{request.pallet_type}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default InferenceRequestList;
