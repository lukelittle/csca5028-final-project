#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class VisibilityData(db.Model):
    __tablename__ = 'visibility_data'
    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    visibility = db.Column(db.Float)

    def __repr__(self):
        return f"<VisibilityData(station='{self.station}', date='{self.date}', visibility={self.visibility})>"

class ThreeDayAverageVisibility(db.Model):
    __tablename__ = 'three_day_average_visibility'
    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String, nullable=False)
    average_visibility = db.Column(db.Float)

    def __repr__(self):
        return f"<ThreeDayAverageVisibility(station='{self.station}', average_visibility={self.average_visibility})>"

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