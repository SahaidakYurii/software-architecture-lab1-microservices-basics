import grpc
from concurrent import futures
import logging_service_pb2
import logging_service_pb2_grpc

logs = {}
logged_ids = set()


class LoggingService(logging_service_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        if request.id in logged_ids:
            context.set_details("Duplicate message")
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            return logging_service_pb2.LogResponse(status="Duplicate message")

        logs[request.id] = request.msg
        logged_ids.add(request.id)
        print(f"LOGGER:\tLogged[message: {request.msg}, id: {request.id}]")
        return logging_service_pb2.LogResponse(status="Logged")

    def GetLogs(self, request, context):
        return logging_service_pb2.LogResponse(status=" | ".join(logs.values()))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_service_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    print("LOGGER:\tgRPC server running on port 5001")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
