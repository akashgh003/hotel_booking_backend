from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from src.config import MODEL_PATH
from src.data.db_manager import Booking, Hotel, Country

class TextEmbedder:
    def __init__(self, model_path: str = MODEL_PATH):

        self.model = SentenceTransformer(model_path)
    
    def embed_text(self, text: str) -> np.ndarray:

        return self.model.encode(text)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:

        return self.model.encode(texts)


def generate_booking_documents(session: Session) -> List[Dict[str, Any]]:

    query = session.query(
        Booking.id,
        Booking.arrival_date,
        Booking.departure_date,
        Booking.lead_time,
        Booking.is_canceled,
        Booking.adr,
        Booking.total_nights,
        Hotel.name.label('hotel_name'),
        Hotel.type.label('hotel_type'),
        Country.name.label('country_name')
    ).join(
        Hotel, Booking.hotel_id == Hotel.id
    ).join(
        Country, Booking.country_id == Country.id
    )
    
    df = pd.read_sql(query.statement, session.bind)
    
    documents = []
    for _, row in df.iterrows():
        revenue = row['adr'] * row['total_nights']
        
        text = f"""
        Booking ID: {row['id']}
        Hotel: {row['hotel_name']}
        Hotel Type: {row['hotel_type']}
        Country: {row['country_name']}
        Arrival Date: {row['arrival_date']}
        Departure Date: {row['departure_date']}
        Lead Time: {row['lead_time']} days
        Total Nights: {row['total_nights']}
        Average Daily Rate: ${row['adr']:.2f}
        Total Revenue: ${revenue:.2f}
        Status: {"Canceled" if row['is_canceled'] else "Confirmed"}
        """
        
        document = {
            'id': str(row['id']),
            'text': text,
            'metadata': {
                 'id': row['id'],
                'hotel_name': row['hotel_name'],
                'hotel_type': row['hotel_type'],
                'country': row['country_name'],
                'arrival_date': row['arrival_date'].strftime('%Y-%m-%d'),
                'departure_date': row['departure_date'].strftime('%Y-%m-%d') if row['departure_date'] else None,
                'lead_time': row['lead_time'],
                'total_nights': row['total_nights'],
                'adr': float(row['adr']),
                'revenue': float(revenue),
                'is_canceled': bool(row['is_canceled'])
            }
        }
        documents.append(document)
    
    return documents