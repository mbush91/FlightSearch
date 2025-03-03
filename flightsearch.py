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

# Updated arrays: Each tuple is (Airport Code, Airport Name)
From = [
    ("DTW", "Detroit Metropolitan"),
    ("ORD", "Chicago O'Hare"),
    ("YYZ", "Toronto Pearson")
]

To = [
    ("NCE", "Nice Côte d'Azur"),
    ("MRS", "Marseille Provence"),
    ("CDG", "Charles de Gaulle")
]

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

    # Loop over the tuple arrays for From and To
    for f_code, f_name in From:
        for t_code, t_name in To:

            filter = create_filter(
                flight_data=[
                    FlightData(date=Leave, from_airport=f_code, to_airport=t_code, max_stops=MaxStops),
                    FlightData(date=Return, from_airport=t_code, to_airport=f_code, max_stops=MaxStops)
                ],
                trip="round-trip",
                seat="economy",
                passengers=Passengers(adults=People),
                max_stops=MaxStops)
            
            b64 = filter.as_b64().decode('utf-8')
            url = f"https://www.google.com/travel/flights?tfs={b64}"

            data_filename = f"{folder}/{today.year}{today.month}{today.day}_flight_data_{f_code}_{t_code}_{Leave}_{Return}.pkl"
            if os.path.exists(data_filename):
                with open(data_filename, "rb") as fd:
                    result = pickle.load(fd)
                print(f"Loaded cached result for {f_code} to {t_code}")
            else:
                print(f"Searching flights from {f_code} to {t_code}...")
                # Fetch flights from the US to France
                while True:
                    try:
                        result = get_flights_from_filter(filter, mode="fallback")
                        # Save the result to a file
                        with open(data_filename, "wb") as fd:
                            pickle.dump(result, fd)
                        print(f"Saved result to {data_filename}")
                        sleep(1)
                        break
                    except Exception as e:
                        print(f"Error fetching flights: {e}")
                        sleep(5)
                    
            flights = []
            for flight in result.flights:
                # Use the display names for From and To
                flight.From = f_name
                flight.To = t_name
                flight.url = url
                flight.return_date = Return
                # Calculate price per person
                try:
                    flight.price_per_person = float(flight.price.strip('$')) / People
                except Exception:
                    flight.price_per_person = "N/A"
                flights.append(flight)

            results += flights

    # Convert the max duration (e.g., "13 hr") to minutes.
    max_duration_minutes = parse_duration(MaxDuration)
    
    # Filter the flight results based on duration.
    filtered_results = [flight for flight in results if parse_duration(flight.duration) <= max_duration_minutes]

    # Sort by price
    filtered_results.sort(key=lambda x: float(x.price.strip('$')))

    group_airports = { f"{flight.From} -> {flight.To}": [] for flight in filtered_results }
    for flight in filtered_results:
        group_airports[f"{flight.From} -> {flight.To}"].append(flight)

    # Sort the flights by price for each route.
    for key in group_airports:
        group_airports[key].sort(key=lambda x: float(x.price.strip('$')))

    return group_airports

def main():
    results = get_flights()
    print("\n\n")

    for route, flights in results.items():
        cheapest = flights[0]
        print(f"Cheapest Flight {route}")
        print(f"\tURL: {cheapest.url}")
        print(f"\tPrice: {cheapest.price}  (${cheapest.price_per_person:.2f} per person)")
        print(f"\tDeparture: {cheapest.departure}")
        print(f"\tArrival: {cheapest.arrival}")
        print(f"\tDuration: {cheapest.duration}")
        print(f"\tStops: {cheapest.stops}")

if __name__ == "__main__":
    main()
