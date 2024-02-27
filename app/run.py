#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

Base = declarative_base()

class VisibilityData(Base):
    __tablename__ = 'visibility_data'
    id = Column(Integer, primary_key=True)
    station = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    visibility = Column(Float)

    def __repr__(self):
        return f"<VisibilityData(station='{self.station}', date='{self.date}', visibility={self.visibility})>"

class ThreeDayAverageVisibility(Base):
    __tablename__ = 'three_day_average_visibility'
    id = Column(Integer, primary_key=True)
    station = Column(String, nullable=False)
    average_visibility = Column(Float)

    def __repr__(self):
        return f"<ThreeDayAverageVisibility(station='{self.station}', average_visibility={self.average_visibility})>"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/query", methods=["GET"])
def query_visibility():
    station_code = request.args.get('station')
    if station_code:
    
        results = ThreeDayAverageVisibility.query.filter_by(station=station_code).all()
        return render_template('results.html', results=results, station=station_code)
    else:
        return redirect(url_for('main'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)