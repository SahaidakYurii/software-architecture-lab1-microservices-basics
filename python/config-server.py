import os
import argparse
from flask import Flask, jsonify

app = Flask(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Server config")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Port to run the config-server on")
    return parser.parse_args()

args = parse_arguments()

LOGGING_HOSTS = os.environ.get('LOGGING_HOSTS', 'localhost:5011,localhost:5012')
MESSAGES_HOSTS = os.environ.get('MESSAGES_HOSTS', 'localhost:5021,localhost:5022,localhost:5023')

services = {
    "logging-service": [f"http://{LOGGING_HOST}" for LOGGING_HOST in LOGGING_HOSTS.split(",")],
    "messages-service": [f"http://{MESSAGES_HOST}" for MESSAGES_HOST in MESSAGES_HOSTS.split(",")]
}

@app.route("/services/<service_name>", methods=["GET"])
def get_services(service_name):
    return jsonify(services.get(service_name, []))

if __name__ == "__main__":
    app.run(port=args.port)