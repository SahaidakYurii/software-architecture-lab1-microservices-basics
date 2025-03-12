import argparse
from flask import Flask

app = Flask(__name__)

@app.route("/message", methods=["GET"])
def get_message():
    return "not implemented yet\n"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logging Service with Hazelcast")
    parser.add_argument("-p", "--port", type=int, default=5001, help="Port to run the messages service on")
    args = parser.parse_args()

    app.run(port=args.port)
