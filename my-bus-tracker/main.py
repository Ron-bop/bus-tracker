import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime

# API dictionary
bus_url = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates/Bus"
train_url = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates/Rail"

# Allows us to request the API from the website (updates constantly)
bus_response = requests.get(bus_url)
train_response = requests.get(train_url)

# Parse the GTFS-RT feed
# BUS:
bus_feed = gtfs_realtime_pb2.FeedMessage()
bus_feed.ParseFromString(bus_response.content)

# TRAIN:
train_feed = gtfs_realtime_pb2.FeedMessage()
train_feed.ParseFromString(train_response.content)

# Variables: grabbed from Translink GTFS data
# BUS
bus_340 = "340-4158"
bus_stop = "4069" # Carseldine Station bound

# TRAIN
# 600450,600450,"Carseldine station, platform 2",, -27.347310,
# RPSP Springfield Central station, platform one 600443,600443,"Geebung station, platform 1",, -27.368740
train_route_id = "RPSP-4266"
station = "600443"



# timestamp - only show minutes
def minute_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).replace(second=0, microsecond=0)


def tracker(feed, vehicle_id, stop_number):
    # current time
    time_now = datetime.now().replace(second=0, microsecond=0)

    # track next upcoming vehicle
    next_time_difference = None
    closest_vehicle = None
    closest_stop_time_update = None
    closest_estimated_arrival = None

    # Loop through trip updates and print info
    for route in feed.entity:
        if route.HasField('trip_update'):
            vehicle_update = route.trip_update
            if vehicle_update.trip.route_id == vehicle_id:

                for stop_time_update in vehicle_update.stop_time_update:
                    if (
                        stop_time_update.stop_id == stop_number and
                        stop_time_update.HasField('arrival') and
                        stop_time_update.arrival.HasField('time')
                        ):

                        estimated_arrival = minute_timestamp(stop_time_update.arrival.time)
                        time_difference = estimated_arrival - time_now

                        if (estimated_arrival > time_now and
                            ((next_time_difference is None) or (time_difference < next_time_difference))):
                                next_time_difference = time_difference
                                closest_vehicle = vehicle_update
                                closest_stop_time_update = stop_time_update
                                closest_estimated_arrival = estimated_arrival

    if closest_vehicle and closest_stop_time_update:
        print(f"Trip ID: {closest_vehicle.trip.trip_id}")
        print(f"Route ID: {closest_vehicle.trip.route_id}")
        time_difference_minutes = int(next_time_difference.total_seconds() // 60)
        if time_difference_minutes > 1:
            print(f"Your Vehicle will be arriving in {time_difference_minutes} minutes")
        else: # "Vehicle" name is temporary
            print(f"Your Vehicle will be arriving in {time_difference_minutes} minute")
        print(f"ETA: {closest_estimated_arrival}")
        print(f"Stop ID: Beams Rd {closest_stop_time_update.stop_id}")
        print(f"Arrival delay: {closest_stop_time_update.arrival.delay}")
        print("-" * 40)


tracker(bus_feed, bus_340, bus_stop)
tracker(train_feed,train_route_id, station)
