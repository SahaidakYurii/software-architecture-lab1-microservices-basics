# Lab1: Microservices Basics

## Task:
The architecture consists of three microservices: facade-service - accepts POST/GET requests from the client logging-service - stores in memory all the messages it receives and can return them messages-service - while acting as a stub, it returns a static message when addressed

## Usage
1. Create python venv using
```python3 -m venv venv```
2. Activate venv
   - Ubuntu: ```source venv/bin/activate```
   - Windows: ```./venv/activate```
3. Install requirements.txt<br>
    ```pip install -r requirements.txt```
4. Start services
   - Using bash script<br>
   `start-services.sh`<br>
   might need to `chmod +x start-services.sh`
   - Starting one-by-one
   ```bash
   python3 facade-service.py 
   python3 logging-service.py 
   python3 message-service.py
   ```
5. Send requests to services
6. Kill services
    - Using bash script<br>
    `stop-services.sh`<br>
    might need to `chmod +x stop-services.sh`
    - Killing one-by-one
    ```bash
    sudo lsof -i :5000
    sudo kill <PID>
    ```

## Structure
| Service  | Port  | Endpoints | Requests |
|----------|-------|----------|----------|
| Facade   | 5000  | /        | GET/POST |
| Logging  | 5001  |          |          |
| Messages | 5002  | /message | GET      |

## Request examples
| Service   | Type | URL                             | Header                           | Body              | Response                    |
|-----------|------|---------------------------------|----------------------------------|-------------------|-----------------------------|
| Facade    | POST | `http://localhost:5000/`        | `Content-Type: application/json` | `{"msg": "msg1"}` | {"status":"Message logged"} |
| Facade    | GET  | `http://localhost:5000/`        |                                  |                   | msg1: not implemented yet   |
| Logging   | gRPC |                                 |                                  |                   |                             |
| Messages  | GET  | `http://localhost:5002/message` |                                  |                   | not implemented yet         |

## Protocol
Commands
![](./Screenshot%20from%202025-02-15%2023-20-57.png)
Logs
![](./Screenshot%20from%202025-02-15%2023-22-05.png)