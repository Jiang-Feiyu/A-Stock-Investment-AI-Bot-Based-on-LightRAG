#!/bin/bash

# Store PIDs in a file for easier cleanup
PID_FILE="/tmp/app_pids.txt"
touch $PID_FILE

# Cleanup function to handle script termination
cleanup() {
    echo "Cleaning up all processes..."
    
    # Kill all python and uvicorn processes started by this script
    pkill -f "python main.py"
    pkill -f "uvicorn backend:app"
    pkill -f "python server.py"
    
    # Additional cleanup using stored PIDs
    if [ -f $PID_FILE ]; then
        while read pid; do
            kill -9 $pid 2>/dev/null
        done < $PID_FILE
        rm $PID_FILE
    fi
    
    echo "All processes terminated."
    exit
}

# Set up trap for cleanup on script termination
trap cleanup SIGINT SIGTERM EXIT

# Start Backend
echo "Starting Backend..."
cd backend
uvicorn backend:app --reload &
echo $! >> $PID_FILE

# Wait for 5 seconds before starting Middle Desk
sleep 5
echo "Starting Middle Desk..."
cd ../LightRAG
python main.py &
echo $! >> $PID_FILE

# Wait for 60 seconds to ensure both Backend and Middle Desk are ready
echo "Waiting 60 seconds for Backend and Middle Desk to initialize..."
for i in {1..60}
do
    echo -ne "Waiting... $i/60 seconds\r"
    sleep 1
done
echo -e "\nStarting Frontend..."

# Start Frontend
cd ../
python server.py