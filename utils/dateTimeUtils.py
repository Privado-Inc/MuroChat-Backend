from datetime import datetime

def convert_bson_datetime_to_string(bson_datetime):
    if isinstance(bson_datetime, dict) and '$date' in bson_datetime:
        timestamp = bson_datetime['$date'] / 1000  # Convert to seconds
        date_obj = datetime.utcfromtimestamp(timestamp)

        return date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return None
