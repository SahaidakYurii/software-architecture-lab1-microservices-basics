start_node() {
  local port=$1
  hz start -c config.xml -p $port &
  local pid=$!
  echo "Started node on port $port with PID: $pid"

  # Register Hazelcast node information in Consul (use key-value store)
  local node_name="hazelcast-node-$port"
  local node_address=$(hostname -I | awk '{print $1}')  # Assuming the first IP is the desired one
  consul kv put "hazelcast/$node_name/address" "$node_address"
  consul kv put "hazelcast/$node_name/port" "$port"
}

start_services() {
  echo "Starting config-server"
  python3 ./python/config-server.py -p 5000 -m 5001 -l 5002 5003 5004 &

  echo "Starting messages-service..."
  python3 ./python/messages-service.py -p 5001 &

  echo "Starting logging-service..."
  python3 ./python/logging-service.py -i -p 5002 &
  python3 ./python/logging-service.py -i -p 5003 &
  python3 ./python/logging-service.py -i -p 5004 &

  echo "Starting facade-service..."
  python3 ./python/facade-service.py -p 5005 &

  echo "All services started!"
}

stop_services() {
  echo "Stopping all services..."
  pkill -9 -f ./python/facade-service.py
  pkill -9 -f ./python/logging-service.py
  pkill -9 -f ./python/messages-service.py
  pkill -9 -f ./python/server-config.py

  echo "All services stopped!"
}

case "$1" in
  -s|--start)
    echo "Starting Hazelcast nodes..."

    start_node 5701
    start_node 5702
    start_node 5703

    echo "Hazelcast nodes started."

    start_services
    ;;

  -hs | --hazelcast_start)
    echo "Starting Hazelcast nodes..."

    start_node 5701
    start_node 5702
    start_node 5703

    echo "Hazelcast nodes started."
    ;;

  -ss | --services_start)
    start_services
    ;;
  -k|--kill)
    echo "Killing Hazelcast nodes..."

    pkill -f 'hazelcast'

    echo "Hazelcast nodes killed."

    stop_services
    ;;
  -hk|--hazelcast_kill)
    echo "Killing Hazelcast nodes..."

    pkill -f 'hazelcast'

    echo "Hazelcast nodes killed."
    ;;
  -sk|--services_kill)
    stop_services
    ;;
  -h|--help)
    echo "
The bash script to control Hazelcast nodes and microservices

Usage: $0 [OPTION]

Options:
-s  | --start            Start Hazelcast nodes and services
-ss | --services_start   Start only services
-hs | --hazelcast_start  Start only Hazelcast nodes
-k  | --kill             Kill Hazelcast nodes and services
-sk | --services_kill    Kill only services
-hk | --hazelcast_kill   Kill only Hazelcast nodes
-h  | --help             Show this help message
"
    ;;
  *)
    echo "Usage: $0 [-s|--start | -k|--kill | -ss|--services_start | -hs|--hazelcast_start | -sk|--services_kill | -hk|--hazelcast_kill]"
    exit 1
    ;;
esac