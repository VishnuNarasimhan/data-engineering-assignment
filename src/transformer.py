import datetime
import json

def parse_message(raw_message):
    try:
        data = json.loads(raw_message)
        return data
    except Exception as e:
        print("Malformed message: ", raw_message)
        return None

def transform(data):

    user_id = data["id"]
    mail = data["mail"]
    name = data["name"] + " " + data["surname"]

    if "route" in data:
        route = data["route"]

        first = route[0]
        last = route[-1]

        depature = first["from"]
        destination = last["to"]

        start_date = datetime.datetime.strptime(
            first.get("started_at"), "%d/%m/%Y %H:%M:%S"
        )

        initial_end_date =  datetime.datetime.strptime(
            last.get("started_at") , "%d/%m/%Y %H:%M:%S"
        )

        duration = datetime.timedelta(minutes= last["duration"])

        end_date = initial_end_date + duration

    elif "locations" in data:
        locations = data["locations"]

        locations = sorted(locations, key=lambda x: x["timestamp"])

        first = locations[0]
        last = locations[-1]

        depature = first["location"]
        destination = last["location"]

        start_date = datetime.datetime.fromtimestamp(first["timestamp"])
        end_date = datetime.datetime.fromtimestamp(last["timestamp"])

    else:
        return None
    
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