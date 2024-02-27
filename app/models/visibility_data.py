from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float

Base = declarative_base()

class VisibilityData(Base):
    __tablename__ = 'visibility_data'
    id = Column(Integer, primary_key=True)
    station = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    visibility = Column(Float)

    def __repr__(self):
        return f"<VisibilityData(station='{self.station}', date='{self.date}', visibility={self.visibility})>"