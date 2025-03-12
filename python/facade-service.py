import argparse
import random
from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Facade Service")
    parser.add_argument("-p", "--port", type=int, default=5005, help="Port to run the facade-service on")
    parser.add_argument("-m", "--messages_port", type=int, default=5001, help="Port where messages-service instance is running")
    parser.add_argument("-c", "--config_port", type=int, default=5000, help="Port where config-server instance is running")
    parser.add_argument(
        "-l", "--logging_ports",
        type=int,
        nargs="+",
        default=[5002, 5003, 5004],  # Default ports
        help="List of ports where logging-service instances are running"
    )
    return parser.parse_args()

args = parse_arguments()
CONFIG_SERVER_URL = "http://localhost:" + str(args.config_port)

def get_service_instances(service_name):
    response = requests.get(f"{CONFIG_SERVER_URL}/services/{service_name}")
    return response.json() if response.status_code == 200 else []

@app.route("/", methods=["POST"])
def handle_post():
    data = request.json
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Message is required"}), 400

    message_id = str(uuid.uuid4())
    log_data = {"id": message_id, "msg": msg}

    logging_services = get_service_instances("logging-service")
    if not logging_services:
        return jsonify({"error": "No logging services available"}), 503

    try:
        requests.post(f"{random.choice(logging_services)}/log", json=log_data)
        return jsonify({"status": "Message logged"}), 201
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to log message"}), 500


@app.route("/", methods=["GET"])
def handle_get():
    logging_services = get_service_instances("logging-service")
    message_service = get_service_instances("messages-service")

    if not logging_services:
        return jsonify({"error": "No logging services available"}), 503

    try:
        log_response = requests.get(f"{random.choice(logging_services)}/log").text
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to get message logs"}), 500

    msg_response = requests.get(f"{message_service[0]}/message").text
    return log_response + ": " + msg_response

if __name__ == "__main__":
    app.run(port=args.port)
