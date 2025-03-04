import requests
import os 
from dotenv import load_dotenv


load_dotenv()

# https://developers.google.com/maps/documentation/places/web-service/place-id
# https://developers.google.com/maps/documentation/routes/specify_location#place_id
# https://developers.google.com/maps/documentation/routes/transit-rm

def get_place_id(name):
    """
    Get the place ID for a given location name.
    """
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "X-Goog-FieldMask": 'places.id,places.displayName,places.formattedAddress'
    }

    params = {
        "textQuery" : name,
    }

    response = requests.post(url, headers=headers, params=params)
    data = response.json()
    
    return data['places'][0]['id']


def get_transit_route(origin, desitination, departure_time=None):
    """
    Get the transit routes between two locations.
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_MAPS_API_KEY"),
        # "X-Goog-FieldMask": 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
        "X-Goog-FieldMask": 'routes.duration,routes.distanceMeters,routes.routeLabels,routes.legs'
    }

    params = {
        "origin" : {"placeId" : origin} ,
        "destination" : {"placeId" : desitination},
        "travelMode" : "TRANSIT",
        #"computeAlternativeRoutes" : True,
    }

    if departure_time:
        params["departureTime"] = departure_time

    print(params)

    response = requests.post(url, headers=headers, json=params)

    if response.status_code != 200:
        print(response.text)

    data = response.json()

    return data



if __name__ == "__main__":
    paris_id = get_place_id("CDG")
    bnb_id = get_place_id("309 Bis Bcle de Bellevue, 83140 Six-Fours-les-Plages, France")

    routes = get_transit_route(paris_id, bnb_id)

    print(routes)
