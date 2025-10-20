import grpc
import calculator_pb2
import calculator_pb2_grpc
from calculator_pb2_grpc import CalculatorStub


def run():
    print("will try to calculate the math between 3 and 2.")

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)
        responseAdd = stub.Add(calculator_pb2.Request(x=3, y=2))
        print("Add: 3 + 2 = " + str(responseAdd.res))

        responseSub = stub.Sub(calculator_pb2.Request(x=3, y=2))
        print("Sub: 3 - 2 = " + str(responseSub.res))

        responseMul = stub.Multiply(calculator_pb2.Request(x=3, y=2))
        print("Multiply: 3 * 2 = " + str(responseMul.res))

        responseDiv = stub.Divide(calculator_pb2.Request(x=3, y=2))
        print("Divide: 3 / 2 = " + str(responseDiv.res))


run()
