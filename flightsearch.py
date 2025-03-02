from fast_flights import FlightData, Passengers, Result, get_flights

Leave = "2025-05-23" # Friday
Return = "2025-05-31" # Saturday

From = "DTW"
To = "NCE"

result: Result = get_flights(
    flight_data=[
        FlightData(date=Leave, from_airport=From, to_airport=To),
        FlightData(date=Return, from_airport=To, to_airport=From)
    ],
    trip="round-trip",
    seat="economy",
    passengers=Passengers(adults=2),
    fetch_mode="fallback",
)

print(result)

# The price is currently... low/typical/high
print("The price is currently", result.current_price)