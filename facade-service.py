from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

LOGGING_SERVICE_URL = "http://localhost:5001"
MESSAGES_SERVICE_URL = "http://localhost:5002"

@app.route("/", methods=["POST"])
def handle_post():
    data = request.json
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Message is required"}), 400

    message_id = str(uuid.uuid4())
    log_data = {"id": message_id, "msg": msg}
    requests.post(f"{LOGGING_SERVICE_URL}/log", json=log_data)

    return jsonify({"status": "Message logged"}), 201


@app.route("/", methods=["GET"])
def handle_get():
    log_response = requests.get(f"{LOGGING_SERVICE_URL}/log").text
    msg_response = requests.get(f"{MESSAGES_SERVICE_URL}/message").text
    return log_response + ": " + msg_response


if __name__ == "__main__":
    app.run(port=5000)
