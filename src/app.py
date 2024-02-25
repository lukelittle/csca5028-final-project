#!/usr/bin/env python3

from flask import Flask, render_template, request
import os
import psycopg2
from iron_mq import IronMQ

app = Flask(__name__)

@app.route("/")
def main():
    test_postgres = check_postgres_connection()
    test_ironmq = check_ironmq_connection()
    return render_template('index.html', test_postgres=test_postgres, test_ironmq=test_ironmq)

def check_postgres_connection():
    try:
        DATABASE_URL = os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return "Successful"
    except Exception as e:
        return f"Failed - {e}"

def check_ironmq_connection():
    try:
        ironmq = IronMQ(host="mq-aws-eu-west-1-1.iron.io", project_id=os.environ.get("IRONMQ_PROJECT_ID"), token=os.environ.get("IRONMQ_TOKEN"))
        queue = ironmq.queue("csca5028")
        queue.post("Test message")
        info = queue.info()
        return "Successful" if info else "Failed"
    except Exception as e:
        return f"Failed - {e}"