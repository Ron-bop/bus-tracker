import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime

# API dictionary
url = "https://gtfsrt.api.translink.com.au/api/realtime/SEQ/TripUpdates/Bus"

# Allows us to request the API from the website (updates constantly)
api_response = requests.get(url)

# Parse the GTFS-RT feed
bus_feed = gtfs_realtime_pb2.FeedMessage()
bus_feed.ParseFromString(api_response.content)

# Variables: grabbed from Translink GTFS data
bus_340 = "340-4158"
beams_rd_bus_stop = "4069"

# current time
time_now = datetime.now().replace(second = 0, microsecond = 0)

# timestamp - only show minutes
def minute_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).replace(second=0, microsecond=0)

# track soonest upcoming bus arrival
next_time_difference = None
closest_bus = None
closest_stop_time_update = None
closest_estimated_arrival = None

# Loop through trip updates and print info
for bus_route in bus_feed.entity:
    if bus_route.HasField('trip_update'):
        bus_update = bus_route.trip_update
        if bus_update.trip.route_id == bus_340:

            for stop_time_update in bus_update.stop_time_update:
                if (
                    stop_time_update.stop_id == beams_rd_bus_stop and
                    stop_time_update.HasField('arrival') and
                    stop_time_update.arrival.HasField('time')
                    ):

                    estimated_arrival = minute_timestamp(stop_time_update.arrival.time)
                    time_difference = estimated_arrival - time_now

                    if (estimated_arrival > time_now and
                        ((next_time_difference is None) or (time_difference < next_time_difference))):
                            next_time_difference = time_difference
                            closest_bus = bus_update
                            closest_stop_time_update = stop_time_update
                            closest_estimated_arrival = estimated_arrival

if closest_bus and closest_stop_time_update:
    print(f"Trip ID: {closest_bus.trip.trip_id}")
    print(f"Route ID: {closest_bus.trip.route_id}")
    time_difference_miunutes = int(next_time_difference.total_seconds() // 60)
    if time_difference_miunutes > 1:
        print(f"Your Bus will be arriving in {time_difference_miunutes} minutes")
    else:
        print(f"Your Bus will be arriving in {time_difference_miunutes} minute")
    print(f"ETA: {closest_estimated_arrival}")
    print(f"Stop ID: Beams Rd {closest_stop_time_update.stop_id}")
    print(f"Arrival delay: {closest_stop_time_update.arrival.delay}")



