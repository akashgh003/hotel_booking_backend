from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
import datetime
from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Hotel(Base):
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  
    bookings = relationship("Booking", back_populates="hotel")
    
class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    bookings = relationship("Booking", back_populates="country")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    is_canceled = Column(Boolean)
    lead_time = Column(Integer)  
    arrival_date = Column(Date)
    departure_date = Column(Date)
    adults = Column(Integer)
    children = Column(Integer)
    babies = Column(Integer)
    country_id = Column(Integer, ForeignKey("countries.id"))
    market_segment = Column(String)
    distribution_channel = Column(String)
    is_repeated_guest = Column(Boolean)
    previous_cancellations = Column(Integer)
    previous_bookings_not_canceled = Column(Integer)
    reserved_room_type = Column(String)
    assigned_room_type = Column(String)
    booking_changes = Column(Integer)
    deposit_type = Column(String)
    days_in_waiting_list = Column(Integer)
    customer_type = Column(String)
    adr = Column(Float)  
    required_car_parking_spaces = Column(Integer)
    total_of_special_requests = Column(Integer)
    reservation_status = Column(String)
    reservation_status_date = Column(Date)
    total_nights = Column(Integer)
    
    hotel = relationship("Hotel", back_populates="bookings")
    country = relationship("Country", back_populates="bookings")

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    response_text = Column(Text)
    timestamp = Column(Date, default=datetime.datetime.now)
    execution_time_ms = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():

    print("Creating database tables...")
    
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully")
    
def close_db():
    engine.dispose()