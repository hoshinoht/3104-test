import grpc
import time
import random
import fleet_pb2
import fleet_pb2_grpc


def generate_telemetry(van_id):
    # TODO: Generate and yield multiple telemetry data points
    # Each point should include van_id, latitude, longitude, and random speed
    # simulate random gps updates (small variations in latiude and longitude)
    van_id = van_id
    latitude = 16  # starting seed
    longitude = 20  # starting seeds
    speed = 0  # starting speed

    # return a stream of telemetry data as an iterator
    while True:  # simulate data being sent
        latitude += random.uniform(-0.01, 0.01)
        longitude += random.uniform(-0.01, 0.01)
        speed = random.randint(40, 100)
        telemetry = fleet_pb2.TelemetryData(
            van_id=van_id,
            latitude=latitude,
            longitude=longitude,
            speed=speed
        )
        yield telemetry
        time.sleep(1)  # 1 sec delay


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = fleet_pb2_grpc.FleetMonitorStub(channel)

    responses = stub.StreamTelemetry(generate_telemetry("VAN-001"))
    for response in responses:
        print("Alert received:", response.message)


if __name__ == '__main__':
    run()
