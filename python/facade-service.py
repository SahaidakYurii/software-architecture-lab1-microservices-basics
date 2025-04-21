import argparse
import os
import random
from flask import Flask, request, jsonify
import requests
import uuid
from confluent_kafka import Producer

app = Flask(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Facade Service")
    parser.add_argument("-p", "--port", type=int, default=5005, help="Port to run the facade-service on")
    return parser.parse_args()

CONFIG_HOST = os.environ.get("CONFIG_HOST", "localhost:5000")

args = parse_arguments()
CONFIG_SERVER_URL = f"http://{CONFIG_HOST}"
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka1:29092,kafka2:29093,kafka3:29094")
KAFKA_TOPIC = "messages"

producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
producer = Producer(producer_conf)

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
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to log message"}), 500

    try:
        producer.produce(KAFKA_TOPIC, value=msg.encode("utf-8"))
        producer.flush()
    except Exception as e:
        return jsonify({"error": f"Kafka send failed: {str(e)}"}), 500

    return jsonify({"status": "Message sent to Kafka"}), 201


@app.route("/", methods=["GET"])
def handle_get():
    logging_services = get_service_instances("logging-service")
    message_services = get_service_instances("messages-service")

    if not logging_services:
        return jsonify({"error": "No logging services available"}), 503
    if not message_services:
        return jsonify({"error": "No messages-service instances available"}), 503

    try:
        log_response = requests.get(f"{random.choice(logging_services)}/log").text
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to get message logs"}), 500

    try:
        msg_response = requests.get(f"{random.choice(message_services)}/messages").text
    except Exception as e:
        return jsonify({"error": f"Failed to contact messages-service: {str(e)}"}), 500

    return log_response + ": " + msg_response

if __name__ == "__main__":
    app.run(port=args.port)
