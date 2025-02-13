#!/bin/bash

echo "Starting logging-service..."
python3 logging-service.py &

echo "Starting messages-service..."
python3 messages-service.py &

echo "Starting facade-service..."
python3 facade-service.py &

echo "All services started!"