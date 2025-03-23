import sys
import os
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.loader import load_raw_data
from src.data.cleaner import clean_data
from src.data.db_manager import engine, SessionLocal, Hotel, Country, Booking

def load_data_to_db():
    print("Loading and processing the dataset...")
    
    df = load_raw_data()
    df_clean = clean_data(df)
    
    print(f"Processed {len(df_clean)} booking records")

    session = SessionLocal()
    
    try:
        print("Loading hotels...")
        hotels = {}
        for hotel_type in df_clean['hotel'].unique():
            hotel = Hotel(name=hotel_type, type=hotel_type)
            session.add(hotel)
            hotels[hotel_type] = hotel
        
        print("Loading countries...")
        countries = {}
        for country_name in df_clean['country'].unique():
            country = Country(name=country_name)
            session.add(country)
            countries[country_name] = country
        
        session.commit()
        
        print("Loading bookings...")
        batch_size = 1000
        total_rows = len(df_clean)
        
        for i in range(0, total_rows, batch_size):
            print(f"Processing batch {i//batch_size + 1}/{(total_rows//batch_size) + 1}")
            batch = df_clean.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                booking = Booking(
                    hotel_id=hotels[row['hotel']].id,
                    is_canceled=bool(row['is_canceled']),
                    lead_time=row['lead_time'],
                    arrival_date=row['arrival_date'],
                    departure_date=row['departure_date'],
                    adults=row['adults'],
                    children=row['children'],
                    babies=row['babies'],
                    country_id=countries[row['country']].id,
                    market_segment=row['market_segment'],
                    distribution_channel=row['distribution_channel'],
                    is_repeated_guest=bool(row['is_repeated_guest']),
                    previous_cancellations=row['previous_cancellations'],
                    previous_bookings_not_canceled=row['previous_bookings_not_canceled'],
                    reserved_room_type=row['reserved_room_type'],
                    assigned_room_type=row['assigned_room_type'],
                    booking_changes=row['booking_changes'],
                    deposit_type=row['deposit_type'],
                    days_in_waiting_list=row['days_in_waiting_list'],
                    customer_type=row['customer_type'],
                    adr=row['adr'],
                    required_car_parking_spaces=row['required_car_parking_spaces'],
                    total_of_special_requests=row['total_of_special_requests'],
                    reservation_status=row['reservation_status'],
                    reservation_status_date=pd.to_datetime(row['reservation_status_date']),
                    total_nights=row['total_nights']
                )
                session.add(booking)
            
            session.commit()
        
        print("Data loaded successfully to the database")
        
    except Exception as e:
        session.rollback()
        print(f"Error loading data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    load_data_to_db()