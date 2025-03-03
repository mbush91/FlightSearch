from fast_flights import FlightData, Passengers, Result, get_flights_from_filter, create_filter
from time import sleep
import datetime
import pickle
import os

Leave = "2025-05-23"  # Friday
Return = "2025-05-31"  # Saturday

"""
Trains: 
OUIGO 7851 -> Paris to Toulon ~ $100
"""

From = ["DTW", "ORD", "YYZ"]
To = ["NCE", "MRS", "CDG"]
MaxStops = 2
MaxDuration = "13 hr"
People = 2

def parse_duration(duration_str):
    """Convert a duration string like '12 hr 58 min' or '13 hr' into minutes."""
    hours = 0
    minutes = 0
    parts = duration_str.split()
    # Loop through parts and convert numbers before "hr" and "min"
    for i, part in enumerate(parts):
        if part.startswith("hr"):
            try:
                hours = int(parts[i - 1])
            except ValueError:
                pass
        elif part.startswith("min"):
            try:
                minutes = int(parts[i - 1])
            except ValueError:
                pass
    return hours * 60 + minutes

def get_flights():
    today = datetime.date.today()
    folder = "flight_data"
    if not os.path.exists(folder):
        os.makedirs(folder)

    results = []

    for f in From:
        for t in To:

            filter = create_filter(
                flight_data=[
                    FlightData(date=Leave, from_airport=f, to_airport=t, max_stops=MaxStops),
                    FlightData(date=Return, from_airport=t, to_airport=f, max_stops=MaxStops)
                ],
                trip="round-trip",
                seat="economy",
                passengers=Passengers(adults=People),
                max_stops=MaxStops)
            
            b64 = filter.as_b64().decode('utf-8')
            url = f"https://www.google.com/travel/flights?tfs={b64}"

            data_filename = f"{folder}/{today.year}{today.month}{today.day}_flight_data_{f}_{t}_{Leave}_{Return}.pkl"
            if os.path.exists(data_filename):
                with open(data_filename, "rb") as fd:
                    result = pickle.load(fd)
                print(f"Loaded cached result for {f} to {t}")
            else:
                print(f"Searching flights from {f} to {t}...")
                # Fetch flights from the US to France
                while True:
                    try:
                        result = get_flights_from_filter(filter, mode="fallback")

                        # Save the result to a file
                        with open(data_filename, "wb") as fd:
                            pickle.dump(result, fd)
                        print(f"Saved result to {data_filename}")
                        break
                    except Exception as e:
                        print(f"Error fetching flights: {e}")
                        sleep(5)
                    
            flights = []
            for flight in result.flights:
                flight.From = f
                flight.To = t
                flight.url = url
                flights.append(flight)

            results += result.flights
            #sleep(5)  # Sleep for 1 second to avoid hitting the API too hard

    # Convert the max duration (e.g., "13 hr") to minutes.
    max_duration_minutes = parse_duration(MaxDuration)

    # Filter the flight results based on duration.
    filtered_results = [flight for flight in results if parse_duration(flight.duration) <= max_duration_minutes]

    # Sort the filtered results by price from low to high.
    filtered_results = sorted(filtered_results, key=lambda flight: flight.price)

def main():
    results = get_flights()
    print("\n\n")

    for x in range(30) :
        cheapest = results[x]
        price_per_person = float(cheapest.price.strip('$')) / People
        print(f"Cheapest Flights from {cheapest.From} to {cheapest.To}:")
        print(f"\tURL: {cheapest.url}")
        print(f"\tPrice: {cheapest.price}(%{price_per_person}/person)")
        print(f"\tDeparture: {cheapest.departure}")
        print(f"\tArrival: {cheapest.arrival}")
        print(f"\tDuration: {cheapest.duration}")
        print(f"\tStops: {cheapest.stops}")

main()
