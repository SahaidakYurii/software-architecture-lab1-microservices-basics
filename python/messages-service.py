import argparse
from flask import Flask, jsonify
from confluent_kafka import Consumer
import threading
import os

app = Flask(__name__)
messages = []

def parse_arguments():
    parser = argparse.ArgumentParser(description="Kafka-based Messages Service")
    parser.add_argument("-p", "--port", type=int, help="Port to run the messages service on")
    parser.add_argument("-g", "--group", type=str, default="msg-group", help="Kafka consumer group ID")
    parser.add_argument("-i", "--pid", action="store_true", help="Whether to print PID when started")
    return parser.parse_args()


KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092,localhost:9093,localhost:9094")
KAFKA_TOPIC = "messages"

def kafka_consumer_loop():
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': args.group + "-" + str(args.port),
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([KAFKA_TOPIC])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        decoded_msg = msg.value().decode("utf-8")
        print(f"Received message: {decoded_msg}")
        messages.append(decoded_msg)

@app.route("/messages", methods=["GET"])
def get_message():
    return jsonify(messages)

if __name__ == "__main__":
    args = parse_arguments()
    threading.Thread(target=kafka_consumer_loop, daemon=True).start()

    if args.pid:
        print(f"running with PID: {os.getpid()}")

    app.run(port=args.port)
