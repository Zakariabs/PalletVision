#!/bin/bash
set -e

echo "Starting PalletVision..."

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h postgres -p 5432 -U pallet; do
    sleep 1
done
echo "Database is ready!"

# Start Python backend in background
echo "Starting backend service..."
python app.py &
BACKEND_PID=$!

# Start simple HTTP server for frontend
echo "Starting frontend service..."
cd /app/static
python -m http.server 3000 &
FRONTEND_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?