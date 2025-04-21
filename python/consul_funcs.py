from consul import Consul
import socket

def register_service(service_name, port, host="localhost"):
    consul = Consul()
    service_id = f"{service_name}-{socket.gethostname()}-{port}"
    consul.agent.service.register(name=service_name,
                                  service_id=service_id,
                                  address=host,
                                  port=port,
                                  tags=["microservice"])

def discover_service(service_name):
    consul = Consul()
    index, nodes = consul.catalog.service(service_name)
    return [f"http://{node['ServiceAddress']}:{node['ServicePort']}" for node in nodes]

def discover_kafka_brokers():
    consul = Consul()
    index, nodes = consul.catalog.service("kafka")
    brokers = [f"{node['ServiceAddress']}:{node['ServicePort']}" for node in nodes]
    return brokers

def get_hazelcast_nodes():
    consul = Consul()
    index, nodes = consul.kv.get('hazelcast')
    if nodes is None:
        raise Exception("No Hazelcast nodes found in Consul")

    # Assuming all nodes under 'hazelcast' are Hazelcast nodes with address and port information
    hz_nodes = []
    for key, value in nodes.items():
        if 'address' in key:
            address = value['Value'].decode('utf-8')
            port = consul.kv.get(key.replace('address', 'port'))[1]['Value'].decode('utf-8')
            hz_nodes.append(f"{address}:{port}")
    return hz_nodes