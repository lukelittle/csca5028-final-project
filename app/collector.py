import requests
import datetime
import json
import os
import logging
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from iron_mq import IronMQ

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float

logging.basicConfig(level=logging.DEBUG)

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

class QueueService:
    def __init__(self, mq_client, queue_name):
        self.mq_client = mq_client
        self.queue_name = queue_name

    def publish_message(self, message):
        self.mq_client.queue(self.queue_name).post(message)

    def get_messages(self):
        return self.mq_client.queue(self.queue_name).get()['messages']

    def delete_message(self, message_id):
        self.mq_client.queue(self.queue_name).delete(message_id)

class DataCollector:
    def __init__(self, queue_service, db_session):
        self.queue_service = queue_service
        self.db_session = db_session

    def fetch_and_update_visibility(self, station_code):
        visibility = self.get_visibility(station_code)
        if visibility is not None:
            self.update_db(station_code, visibility)
            self.queue_service.publish_message(json.dumps({'station_code': station_code}))

    @staticmethod
    def get_visibility(station_code):
        url = f'https://api.weather.gov/stations/{station_code}/observations/latest'
        try:
            response = requests.get(url, headers={'User-Agent': 'your-user-agent'})
            data = response.json()
            return data['properties']['visibility']['value']
        except:
            return None

    def update_db(self, station_code, visibility):
        record = self.db_session.query(VisibilityData).filter_by(station=station_code, date=datetime.date.today()).first()
        if record:
            record.visibility = visibility
        else:
            self.db_session.add(VisibilityData(station=station_code, date=datetime.date.today(), visibility=visibility))
        self.db_session.commit()

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    ironmq_client = IronMQ(host="mq-aws-eu-west-1-1.iron.io", project_id=os.getenv("IRON_MQ_PROJECT_ID"), token=os.getenv("IRON_MQ_TOKEN"))
    queue_service = QueueService(ironmq_client, "your-queue-name")

    data_collector = DataCollector(queue_service, session)
    station_codes = ['KATL', 'KDFW', 'KDEN', 'KORD', 'KLAX', 'KJFK', 'KLAS', 'KMCO', 'KMIA', 'KCLT', 'KSEA', 'KPHX', 'KEWR', 'KSFO', 'KIAH', 'KBOS', 'KFLL', 'KMSP', 'KLGA', 'KDTW']

    for code in station_codes:
        data_collector.fetch_and_update_visibility(code)