import requests
import datetime
import json
import os
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from app.models.visibility_data import VisibilityData, Base
from iron_mq import IronMQ

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
    engine = create_engine(os.getenv("DATABASE_URL"))
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    ironmq_client = IronMQ(host=os.getenv("IRON_MQ_HOST"), project_id=os.getenv("IRON_MQ_PROJECT_ID"), token=os.getenv("IRON_MQ_TOKEN"))
    queue_service = QueueService(ironmq_client, "your-queue-name")

    data_collector = DataCollector(queue_service, session)
    station_codes = ['KATL', 'KDFW', 'KDEN', 'KORD', 'KLAX', 'KJFK', 'KLAS', 'KMCO', 'KMIA', 'KCLT', 'KSEA', 'KPHX', 'KEWR', 'KSFO', 'KIAH', 'KBOS', 'KFLL', 'KMSP', 'KLGA', 'KDTW']

    for code in station_codes:
        data_collector.fetch_and_update_visibility(code)