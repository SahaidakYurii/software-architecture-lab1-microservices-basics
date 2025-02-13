from flask import Flask, request, jsonify

app = Flask(__name__)
logs = {}

@app.route("/log", methods=["POST"])
def log_message():
    data = request.json
    logs[data["id"]] = data["msg"]
    print(f"Logged[message:{data['msg']}, id: {data["id"]}]")
    return jsonify({"status": "Logged"}), 201

@app.route("/log", methods=["GET"])
def get_logs():
    return " | ".join(logs.values())

if __name__ == "__main__":
    app.run(port=5001)
