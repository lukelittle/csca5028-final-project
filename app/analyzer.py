# import os
# import logging
# from datetime import date, timedelta
# from typing import Any, Optional
# from sqlalchemy import create_engine, func, and_
# from sqlalchemy.orm import sessionmaker, Session
# from iron_mq import IronMQ
# from app.models.visibility_data import VisibilityData, Base
# from app.models.three_day_avg_visibility import ThreeDayAverageVisibility

# logging.basicConfig(level=logging.DEBUG)

# class DatabaseService:
#     def __init__(self, session_factory: sessionmaker) -> None:
#         self.session_factory = session_factory

#     def update_three_day_avg_visibility(self) -> None:
#         with self.session_factory() as session:
#             try:
#                 end_date = date.today()
#                 start_date = end_date - timedelta(days=3)
#                 for station in session.query(VisibilityData.station).distinct():
#                     avg_visibility = self.calculate_avg_visibility(session, station.station, start_date, end_date)
#                     self.update_or_create_avg_visibility(session, station.station, avg_visibility)
#                 session.commit()
#             except Exception as e:
#                 logging.error(f"Database error during average visibility update: {e}")

#     @staticmethod
#     def calculate_avg_visibility(session: Session, station_code: str, start_date: date, end_date: date) -> Optional[float]:
#         return session.query(func.avg(VisibilityData.visibility))\
#             .filter(and_(VisibilityData.station == station_code, VisibilityData.date >= start_date, VisibilityData.date <= end_date))\
#             .scalar()

#     @staticmethod
#     def update_or_create_avg_visibility(session: Session, station_code: str, avg_visibility: float) -> None:
#         avg_vis_entry = session.query(ThreeDayAverageVisibility)\
#             .filter_by(station=station_code).first()
#         if avg_vis_entry:
#             avg_vis_entry.average_visibility = avg_visibility
#         else:
#             session.add(ThreeDayAverageVisibility(station=station_code, average_visibility=avg_visibility))

# class AverageVisibilityQueueService:
#     def __init__(self, mq_client: IronMQ, queue_name: str, database_service: DatabaseService) -> None:
#         self.mq_client = mq_client
#         self.queue_name = queue_name
#         self.database_service = database_service

#     def listen_for_messages(self) -> None:
#         while True:
#             for message_body in self.subscribe():
#                 logging.info(f"Processing message: {message_body}")
#                 self.database_service.update_three_day_avg_visibility()

#     def subscribe(self) -> Any:
#         response = self.mq_client.queue(self.queue_name).get()
#         messages = response.get('messages', [])
#         for message in messages:
#             yield message['body']
#             self.mq_client.queue(self.queue_name).delete(message['id'])

# if __name__ == "__main__":
#     DATABASE_URL = os.environ["DATABASE_URL"]
#     engine = create_engine(DATABASE_URL)
#     Session = sessionmaker(bind=engine)

#     Base.metadata.create_all(engine)

#     ironmq_client = IronMQ(
#         host=os.environ["IRON_MQ_HOST"],
#         project_id=os.environ["IRON_MQ_PROJECT_ID"],
#         token=os.environ["IRON_MQ_TOKEN"]
#     )

#     queue_name = "csca5028"
#     database_service = DatabaseService(Session)
#     avg_visibility_service = AverageVisibilityQueueService(ironmq_client, queue_name, database_service)

#     avg_visibility_service.listen_for_messages()