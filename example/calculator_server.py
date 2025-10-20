import calculator_pb2
import calculator_pb2_grpc


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        return calculator_pb2.Reply(res=request.x + request.y)

    def Sub(self, request, context):
        return calculator_pb2.Reply(res=request.x - request.y)

    def Multiply(self, request, context):
        return calculator_pb2.Reply(res=request.x * request.y)

    def Divide(self, request, context):
        return calculator_pb2.Reply(res=request.x / request.y)


# serve the server
def serve():
    import grpc
    from concurrent import futures

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()


serve()
