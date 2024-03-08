import os
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")


def get_traffic_info(api_key, origin, destination):
    directions_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=driving&departure_time=now&key={api_key}'
    
    try:
        response = requests.get(directions_url)
        data = response.json()
        
        if response.status_code == 200 and data['status'] == 'OK':
            routes = data['routes']
            if routes:
                legs = routes[0]['legs']
                if legs:
                    duration = legs[0]['duration_in_traffic']['text']
                    print('Estimated travel time with traffic:', duration)
        else:
            print("Error:", data['error_message'])
    except Exception as e:
        print("Exception:", e)

# Example usage
if __name__ == "__main__":
    origin = 'UCLA'
    destination = 'LAX'
    
    get_traffic_info(api_key, origin, destination)
