from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class ThreeDayAverageVisibility(Base):
    __tablename__ = 'three_day_average_visibility'
    id = Column(Integer, primary_key=True)
    station = Column(String, nullable=False)
    average_visibility = Column(Float)

    def __repr__(self):
        return f"<ThreeDayAverageVisibility(station='{self.station}', average_visibility={self.average_visibility})>"