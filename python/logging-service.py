from flask import Flask, request, jsonify
import argparse
import hazelcast
import os

app = Flask(__name__)
logs = {}

hz_client = hazelcast.HazelcastClient()
log_map = hz_client.get_map("logs").blocking()

@app.route("/log", methods=["POST"])
def log_message():
    data = request.json
    log_map.put(data["id"], data["msg"])
    print(f"Logged[message: {data['msg']}, id: {data['id']}]")
    return jsonify({"status": "Logged"}), 201

@app.route("/log", methods=["GET"])
def get_logs():
    all_logs = log_map.entry_set()
    return " | ".join(value for key, value in all_logs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logging Service with Hazelcast")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to run the logging service on")
    parser.add_argument("-i", "--pid", action="store_true", help="Whether to print PID when started")

    args = parser.parse_args()

    if (args.pid) :
        print(f"running with PID: {os.getpid()}")

    app.run(port=args.port)
