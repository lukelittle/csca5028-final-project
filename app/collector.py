import requests
import datetime
import json
import os
import logging
from typing import Generator, Optional, Any
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from app.models.visibility_data import VisibilityData, Base
from iron_mq import IronMQ

logging.basicConfig(level=logging.DEBUG)

class QueueService:
    def __init__(self, mq_client: IronMQ, queue_name: str) -> None:
        self.mq_client = mq_client
        self.queue_name = queue_name

    def publish(self, message: str) -> None:
        response = self.mq_client.queue(self.queue_name).post(message)
        if response['msg'] == 'Messages put on queue.':
            logging.info(f"Message sent to queue {self.queue_name} successfully.")
        else:
            logging.error(f"Failed to send message to queue {self.queue_name}.")

    def subscribe(self) -> Generator[str, None, None]:
        response = self.mq_client.queue(self.queue_name).get()
        messages = response['messages']
        for message in messages:
            logging.info(f"Processing message: {message['body']}")
            yield message['body']
            self.mq_client.queue(self.queue_name).delete(message['id'])

class DataCollector:
    def __init__(self, queue_service: QueueService, session_factory: sessionmaker) -> None:
        self.queue_service = queue_service
        self.session_factory = session_factory

    @staticmethod
    def get_visibility(station_code: str) -> Optional[float]:
        url = f'https://api.weather.gov/stations/{station_code}/observations/latest'
        headers = {
            'User-Agent': 'csca5028-final-project/1.0 (halp@lukelittle.com)'  # Adjusted User-Agent
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            data = response.json()
            visibility = data['properties']['visibility']['value']
            return visibility
        except requests.RequestException as e:
            logging.error(f"Error fetching data for station {station_code}: {e}")
            return None

    def send_station_code_to_queue(self, station_code: str) -> None:
        message_body = json.dumps({'station_code': station_code})
        self.queue_service.publish(message_body)

    def add_or_update_visibility(self, station_code: str, visibility: Optional[float]) -> None:
        session: Any = self.session_factory()
        try:
            current_date = datetime.date.today()
            record = session.query(VisibilityData).filter(
                and_(VisibilityData.station == station_code, VisibilityData.date == current_date)
            ).first()

            if record:
                if record.visibility != visibility:
                    record.visibility = visibility
            else:
                session.add(VisibilityData(station=station_code, date=current_date, visibility=visibility))

            session.commit()
        except Exception as e:
            logging.error(f"Database error for station {station_code}: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    ironmq_client = IronMQ(
        host=os.environ["IRON_MQ_HOST"],
        project_id=os.environ["IRON_MQ_PROJECT_ID"],
        token=os.environ["IRON_MQ_TOKEN"]
    )

    queue_name = "csca5028"
    queue_service = QueueService(ironmq_client, queue_name)

    data_collector = DataCollector(queue_service, Session)

    station_codes = [
        'KATL', 'KDFW', 'KDEN', 'KORD', 'KLAX', 'KJFK', 'KLAS', 'KMCO', 'KMIA', 'KCLT', 
        'KSEA', 'KPHX', 'KEWR', 'KSFO', 'KIAH', 'KBOS', 'KFLL', 'KMSP', 'KLGA', 'KDTW'
    ]

    for code in station_codes:
        visibility = DataCollector.get_visibility(code)
        if visibility is not None:
            data_collector.add_or_update_visibility(code, visibility)
            data_collector.send_station_code_to_queue(code)