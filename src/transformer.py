import datetime
import json

def parse_message(raw_message):
    # Convert the raw JSON message string into a Python dictionary.
    try:
        data = json.loads(raw_message)
        return data
    except Exception as e:
        # Return None when the message is not valid JSON.
        # print("Malformed message: ", raw_message)
        return None

def transform(data):
    # Extract common user details from the input message.
    user_id = data["id"]
    mail = data["mail"]
    name = data["name"] + " " + data["surname"]

    # Handle messages that contain a route made of travel segments.
    if "route" in data:
        route = data["route"]

        # Use the first and last route segments to determine the full trip.
        first = route[0]
        last = route[-1]

        depature = first["from"]
        destination = last["to"]

        # Parse the trip start time from the first route segment.
        start_date = datetime.datetime.strptime(
            first.get("started_at"), "%d/%m/%Y %H:%M:%S"
        )

        # Parse the final segment start time and add its duration to get trip end.
        initial_end_date =  datetime.datetime.strptime(
            last.get("started_at") , "%d/%m/%Y %H:%M:%S"
        )

        duration = datetime.timedelta(minutes= last["duration"])

        end_date = initial_end_date + duration

    # Handle messages that contain timestamped locations instead of route segments.
    elif "locations" in data:
        locations = data["locations"]

        # Sort locations by timestamp so the earliest and latest points are known.
        locations = sorted(locations, key=lambda x: x["timestamp"])

        first = locations[0]
        last = locations[-1]

        depature = first["location"]
        destination = last["location"]

        # Convert Unix timestamps into datetime objects.
        start_date = datetime.datetime.fromtimestamp(first["timestamp"])
        end_date = datetime.datetime.fromtimestamp(last["timestamp"])

    else:
        # Ignore messages that do not contain trip information.
        return None
    
    # Return the normalized user and trip data.
    return {
        "id": user_id,
        "mail": mail,
        "name": name,
        "trip": {
            "departure": depature,
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }