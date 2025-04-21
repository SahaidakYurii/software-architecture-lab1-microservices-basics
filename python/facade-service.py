import argparse
import random
from flask import Flask, request, jsonify
import requests
import uuid
from confluent_kafka import Producer
from consul import Consul
import socket

app = Flask(__name__)

def register_service(service_name, port):
    consul = Consul()
    service_id = f"{service_name}-{socket.gethostname()}-{port}"
    consul.agent.service.register(service_name,
                                  service_id=service_id,
                                  port=port,
                                  tags=["microservice"])


def discover_service(service_name):
    consul = Consul()
    index, nodes = consul.catalog.service(service_name)
    return [f"http://{node['ServiceAddress']}:{node['ServicePort']}" for node in nodes]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Facade Service")
    parser.add_argument("-p", "--port", type=int, default=5005, help="Port to run the facade-service on")
    parser.add_argument("-c", "--config_port", type=int, default=5000, help="Port where config-server instance is running")
    parser.add_argument("-m", "--messages_port",
        type=int,
        nargs="+",
        default=[5011, 5012, 5013],
        help="List of ports where messages-service instances are running")
    parser.add_argument(
        "-l", "--logging_ports",
        type=int,
        nargs="+",
        default=[5021, 5022, 5023],  # Default ports
        help="List of ports where logging-service instances are running"
    )
    return parser.parse_args()

args = parse_arguments()
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092,localhost:9093,localhost:9094"
KAFKA_TOPIC = "messages"

producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
producer = Producer(producer_conf)

@app.route("/", methods=["POST"])
def handle_post():
    data = request.json
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Message is required"}), 400

    message_id = str(uuid.uuid4())
    log_data = {"id": message_id, "msg": msg}

    logging_services = discover_service("logging-service")
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
    logging_services = discover_service("logging-service")
    message_services = discover_service("messages-service")

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
    register_service('facade-service', args.port)
    app.run(port=args.port)
