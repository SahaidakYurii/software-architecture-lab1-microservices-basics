from flask import Flask, request, jsonify
import requests
import uuid
import grpc
import logging_service_pb2
import logging_service_pb2_grpc
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

app = Flask(__name__)

channel = grpc.insecure_channel('localhost:5001')
stub = logging_service_pb2_grpc.LoggingServiceStub(channel)

MESSAGES_SERVICE_URL = "http://localhost:5002"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def log_message(message_id, msg):
    print(f"FACEDE:\tSent[message:{msg}, id: {message_id}]")
    request = logging_service_pb2.LogRequest(id=message_id, msg=msg)
    response = stub.LogMessage(request)
    if response.status == "Duplicate message":
        raise RetryError("Duplicate message detected")
    return response

@app.route("/", methods=["POST"])
def handle_post():
    data = request.json
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Message is required"}), 400

    message_id = str(uuid.uuid4())

    try:
        log_message(message_id, msg)  # Retry logic is applied here
    except RetryError:
        return jsonify({"error": "Failed to log message after retries"}), 500

    return jsonify({"status": "Message logged"}), 201


@app.route("/", methods=["GET"])
def handle_get():
    log_response = stub.GetLogs(logging_service_pb2.Empty()).status
    msg_response = requests.get(f"{MESSAGES_SERVICE_URL}/message").text
    return log_response + ": " + msg_response

if __name__ == "__main__":
    app.run(port=5000)
