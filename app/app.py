#!/usr/bin/env python3

from flask import Flask, render_template, request
import os
import psycopg2
from iron_mq import IronMQ

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')