#!/bin/bash

echo "Stopping all services..."
pkill -f facade-service.py
pkill -f logging-service.py
pkill -f messages-service.py

echo "All services stopped!"