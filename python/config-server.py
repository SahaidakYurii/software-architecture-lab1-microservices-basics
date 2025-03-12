import argparse
from flask import Flask, jsonify

app = Flask(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Server config")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Port to run the config-server on")
    parser.add_argument("-m", "--messages_port", type=int, default=5001, help="Port where facade service instance is running")
    parser.add_argument("-l", "--logging_ports",
        type=int,
        nargs="+",
        default=[5002, 5003, 5004],  # Default ports
        help="List of ports where logging-service instances are running"
    )
    return parser.parse_args()

args = parse_arguments()

services = {
    "logging-service": ["http://localhost:" + str(port) for port in args.logging_ports],
    "messages-service": ["http://localhost:" + str(args.messages_port)]
}

@app.route("/services/<service_name>", methods=["GET"])
def get_services(service_name):
    return jsonify(services.get(service_name, []))

if __name__ == "__main__":
    app.run(port=args.port)