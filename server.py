import grpc
from concurrent import futures
import math
import fleet_pb2
import fleet_pb2_grpc

# Provided helper function


def haversine(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two GPS coordinates (in km)."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


class FleetMonitorServicer(fleet_pb2_grpc.FleetMonitorServicer):
    def __init__(self):
        # Maintain state: you any data structures
        self.van_state = {

        }

    def StreamTelemetry(self, request_iterator, context):
        # TODO: Implement logic to:
        # 1. Read telemetry from iterator
        iteration = 0

        for telemetry in request_iterator:
            van_id = telemetry.van_id
            latitude = telemetry.latitude
            longitude = telemetry.longitude
            speed = telemetry.speed

            # print the data first to see what im working with
            print("Current Data:", van_id, latitude, longitude, speed)
            print("self.van_state data", self.van_state)

            haversine_val = 0.0
            # compute haversine using the previous location
            if van_id in self.van_state:
                prev_lat, prev_lon, prev_distance = self.van_state[van_id]
                haversine_val = haversine(
                    prev_lat, prev_lon, latitude, longitude)
                print(f"Distance traveled by {van_id}: {haversine_val:.2f} KM")

            # speeding!!!
            if speed > 80:
                # send back an alert for speeding
                alert_message = f"Speeding alert for {van_id}: {speed:.2f} KM/h"
                yield fleet_pb2.Alert(message=alert_message)

            # send periodic movement updates
            # sends updates every 10 ticks from telemetry stream
            if van_id in self.van_state and iteration % 10 == 0 and haversine_val > 0:
                prev_lat, prev_lon, prev_distance = self.van_state[van_id]
                updated_distance = prev_distance + haversine_val
                dist_message = f"{van_id} moved {haversine_val:.2f} KM (Total:{updated_distance:.2f} KM)"
                yield fleet_pb2.Alert(message=dist_message)

            # update the van state with the current data for the next iteration
            self.van_state[van_id] = (latitude, longitude, self.van_state.get(
                van_id, (0, 0, 0))[2] + haversine_val)

            iteration += 1  # increment the iteration


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    fleet_pb2_grpc.add_FleetMonitorServicer_to_server(
        FleetMonitorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Fleet Monitoring Server running on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
