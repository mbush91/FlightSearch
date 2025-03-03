from flask import Flask, render_template
from flightsearch import get_flights  # Import your flight search module

app = Flask(__name__)

@app.route("/")
def index():
    # Get flight results grouped by route, then select the cheapest flight for each route.
    flight_groups = get_flights()  # returns a dict with key "FROM->TO" and value as a list of flights
    cheapest_flights = [flights[0] for flights in flight_groups.values()]
    return render_template("index.html", flights=cheapest_flights)

if __name__ == "__main__":
    app.run(debug=True)
