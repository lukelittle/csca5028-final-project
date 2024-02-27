#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
import os

# from app.models.three_day_avg_visibility import ThreeDayAverageVisibility

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or 'sqlite:///:memory:'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

@app.route("/")
def main():
    return render_template('index.html')

# @app.route("/query", methods=["GET"])
# def query_visibility():
#     station_code = request.args.get('station')
#     if station_code:
#         results = ThreeDayAverageVisibility.query.filter_by(station=station_code).all()
#         return render_template('results.html', results=results, station=station_code)
#     else:
#         return redirect(url_for('main'))

if __name__ == "__main__":
    # db.create_all()  
    app.run(debug=True) 