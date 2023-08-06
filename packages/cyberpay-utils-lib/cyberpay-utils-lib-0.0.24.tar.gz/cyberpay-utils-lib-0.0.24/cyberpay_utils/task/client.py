import grpc

from .proto import task_service_pb2, task_service_pb2_grpc


class TaskServiceGrpcClient:
    def __init__(self, service_host: str) -> None:
        self.service_host = service_host

    def get_tasks(
        self, request: task_service_pb2.GetTasksRequest
    ) -> task_service_pb2.GetTasksResponse:
        with grpc.insecure_channel(self.service_host) as channel:
            stub = task_service_pb2_grpc.TaskControllerStub(channel)
            response = stub.GetTasks(request)
            return response
