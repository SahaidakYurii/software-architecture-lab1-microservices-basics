from flask import Flask

app = Flask(__name__)

@app.route("/message", methods=["GET"])
def get_message():
    return "not implemented yet\n"

if __name__ == "__main__":
    app.run(port=5002)
