import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
       Convert the query results to a Dictionary using date as the key and tobs as the value.
       Return the JSON representation of your dictionary."""
    # Query all measument
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement).filter(Measurement.date >= query_date).all()

    # Create a dictionary from the row data and append to a list of date_temp
    date_temp = []
    for temp in results:
        temp_dict = {}
        # temp_dict["date"] = temp.date
        # temp_dict["precipitation"] = temp.prcp
        temp_dict[temp.date] = temp.prcp
        date_temp.append(temp_dict)

    return jsonify(date_temp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # Query all tobs
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.date >= query_date).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def summary(start):
    """Return a JSON list of the minimum temperature, the average temperature,
       and the max temperature for a given start or start-end range, or a 404 if not."""

    if len(start) == 8:
        year = int(start[:4])
        month = int(start[4:6])
        day = int(start[6:8])
        start_date = dt.datetime(year, month, day)

        query = [func.min(Measurement.tobs),
                 func.avg(Measurement.tobs),
                 func.max(Measurement.tobs)]
        results = session.query(*query).filter(Measurement.date >= start_date).all()

        summary = list(np.ravel(results))

        return jsonify(summary)

    return jsonify({"error": f"Start date with {start} not found. Please specify a date with 'YYYYMMDD' format."})


@app.route("/api/v1.0/<start>/<end>")
def summary_period(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
       and the max temperature for a given start or start-end range, or a 404 if not."""

    if len(start) == 8 and len(end) == 8:
        year_start = int(start[:4])
        month_start = int(start[4:6])
        day_start = int(start[6:8])
        start_date = dt.datetime(year_start, month_start, day_start)

        year_end = int(end[:4])
        month_end = int(end[4:6])
        day_end = int(end[6:8])
        end_date = dt.datetime(year_end, month_end, day_end)

        query = [func.min(Measurement.tobs),
                 func.avg(Measurement.tobs),
                 func.max(Measurement.tobs)]
        results = session.query(*query).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

        summary = list(np.ravel(results))

        return jsonify(summary)

    return jsonify({"error": f"Start date with {start} and end date with {end} not found. Please specify a date with 'YYYYMMDD' format."})


# @app.route("/api/v1.0/<start>/<end>")
# def summary(start, end):
#     """Return a JSON list of the minimum temperature, the average temperature,
#        and the max temperature for a given start or start-end range, or a 404 if not."""
#
#     canonicalized = superhero.replace(" ", "").lower()
#     for character in justice_league_members:
#         search_term = character["superhero"].replace(" ", "").lower()
#
#         if search_term == canonicalized:
#             return jsonify(character)
#
#     return jsonify({"error": "Character not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
