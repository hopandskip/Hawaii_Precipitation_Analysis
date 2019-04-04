# import Flask
from flask import Flask, jsonify

# Create an app, being sure to pass __name__
app = Flask(__name__)

# Import SQL Alchemy and other dependencies
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Create engine to access the databases
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session (link) from Python to the DB
session = Session(engine)

# Flask Routes

# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the my Precipitation API!<br/>"
        f"On this page you will find data from various weather stations in Hawaii from 2010 - 2017 <br/>"
        f"<br/>Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/> API to get minimum, average, and maximum temperature starting from a specific date (yyyy-mm-dd)<br/>"
        f"/api/v1.0/start<br/><br/>"
        f"API to get data based on a date range (yyyy-mm-dd)<br/>"
        f"/api/v1.0/start/end<br/>"
    )


# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    Return the JSON representation of your dictionary."""

    one_year_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.asc()).all()
    prcp_info=[]
    for row in prcp:
        prcp_dict={}
        prcp_dict["date"]=row.date
        prcp_dict['prcp']=row.prcp
        prcp_info.append(prcp_dict)
    return jsonify(prcp_info)

# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    active_station = session.query(Station.station,Station.name,Station.latitude,\
        Station.longitude,Station.elevation).all()
    station_info=[]
    for row in active_station:
        station_dict={}
        station_dict["station"]=row.station
        station_dict['name']=row.name
        station_dict['latitude']=row.latitude
        station_dict['longitude']=row.longitude
        station_dict['elevation']=row.elevation
        station_info.append(station_dict)
    return jsonify(station_info)

# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""

    one_year_ago=dt.date(2017,8,23)-dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.asc()).all()
    temp_info=[]
    for row in temp:
        temp_dict={}
        temp_dict['date']=row.date
        temp_dict['tobs']=row.tobs
        temp_info.append(temp_dict)
    return jsonify(temp_info)

# /api/v1.0/stations/<start>
@app.route("/api/v1.0/<start>")
def calcstartdate(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    calc_start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    calc_start=[]
    for row in calc_start_date:
        calc_start_dict={}
        calc_start_dict['start date']=start
        calc_start_dict['minimum temp']=row[0]
        calc_start_dict['average temp']=row[1]
        calc_start_dict['maximum temp']=row[2]
        calc_start.append(calc_start_dict)
    return jsonify(calc_start)

# /api/v1.0/stations/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def calcdaterange(start,end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""
    calc_date_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    calc_range=[]
    for row in calc_date_range:
        calc_range_dict={}
        calc_range_dict['start date'] = start
        calc_range_dict['end date'] = end
        calc_range_dict['minimum temp']=row[0]
        calc_range_dict['average temp']=row[1]
        calc_range_dict['maximum temp']=row[2]
        calc_range.append(calc_range_dict)
    return jsonify(calc_range)

if __name__ == "__main__":
    app.run(debug=True)