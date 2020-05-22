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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return ('''
        Available Routes: <br/>
        <li><a href='/api/v1.0/precipitation' target='_blank'>/api/v1.0/precipitation</a></li>
        <li><a href='/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a></li>
        <li><a href='/api/v1.0/tobs' target='_blank'>/api/v1.0/tobs</a></li>
        <li><a href='/api/v1.0/<start>' target='_blank'>/api/v1.0/&lt;start&gt;</a> OR 
        <a href='/api/v1.0/<start>/<end>' target='_blank'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a> </li>
    ''')


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipation values for 12 months prior to the last date in the dataset."""
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0],"%Y-%m-%d") - dt.timedelta(days=365)

    precipitations = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date > one_year_ago).all()
    
    results = dict()
    for _date, _precip in precipitations:
        results[_date] = _precip
    
    session.close()
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    """Return details of all stations in the database."""
    session = Session(engine)
    
    stations = session.query(Station).all()

    results = list()
    for station in stations:
        stations_dict = {
            "station": station.station,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation
        }
        results.append(stations_dict)
    
    session.close()
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature values for 12 months prior to the last date in the dataset."""
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0],"%Y-%m-%d") - dt.timedelta(days=365)

    temperatures = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date > one_year_ago).all()
    
    results = dict()
    for _date, _temp in temperatures:
        results[_date] = _temp
    
    session.close()
    return jsonify(results)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    session = Session(engine)

    start_date = start
    end_date = end
    if end_date:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).all()

    results = {
        "TMIN": temp_stats[0][0],
        "TAVG": round(temp_stats[0][1],2),
        "TMAX": temp_stats[0][2]
    }
    
    session.close()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
