import os
import logging
from datetime import date, timedelta
from sqlalchemy import create_engine, func, and_
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

class DatabaseService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def update_avg_visibility(self):
        with self.session_factory() as session:
            try:
                end_date = date.today()
                start_date = end_date - timedelta(days=2)  # Adjusted to include today and the past two days
                stations = session.query(VisibilityData.station).distinct()
                for station in stations:
                    avg_visibility = self.calculate_avg(session, station.station, start_date, end_date)
                    self.update_or_create(session, station.station, avg_visibility)
                session.commit()
            except Exception as e:
                logging.error(f"Database error: {e}")

    @staticmethod
    def calculate_avg(session, station_code, start_date, end_date):
        return session.query(func.avg(VisibilityData.visibility))\
            .filter(VisibilityData.station == station_code, VisibilityData.date.between(start_date, end_date))\
            .scalar()

    @staticmethod
    def update_or_create(session, station_code, avg_visibility):
        record = session.query(ThreeDayAverageVisibility).filter_by(station=station_code).first()
        if record:
            record.average_visibility = avg_visibility
        else:
            session.add(ThreeDayAverageVisibility(station=station_code, average_visibility=avg_visibility))

class QueueService:
    def __init__(self, mq_client, queue_name, db_service):
        self.mq_client = mq_client
        self.queue_name = queue_name
        self.db_service = db_service

    def listen_and_update(self):
        while True:
            messages = self.get_messages()
            for message_body in messages:
                logging.info(f"Message: {message_body}")
                self.db_service.update_avg_visibility()

    def get_messages(self):
        response = self.mq_client.queue(self.queue_name).reserve(max=None, timeout=None, wait=None, delete=True)
        messages = response.get('messages', [])
        for message in messages:
            logging.info(f"Received message: {message['id']}")
            yield message['body']

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    ironmq_client = IronMQ(
        host="mq-aws-eu-west-1-1.iron.io",
        project_id=os.environ["IRON_MQ_PROJECT_ID"],
        token=os.environ["IRON_MQ_TOKEN"]
    )

    queue_name = "csca5028"
    database_service = DatabaseService(Session)
    queue_service = QueueService(ironmq_client, queue_name, database_service)

    queue_service.listen_and_update()