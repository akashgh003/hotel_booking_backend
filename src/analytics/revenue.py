import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text, func, extract
from sqlalchemy.orm import Session
import io
import base64
from src.data.db_manager import Booking, Hotel

def get_revenue_trends(session: Session, period: str = 'monthly'):

    date_formats = {
        'daily': "YYYY-MM-DD",
        'weekly': "YYYY-WW",
        'monthly': "YYYY-MM",
        'yearly': "YYYY"
    }
    
    format_str = date_formats.get(period, 'monthly')
    
    if period == 'daily':
        query = session.query(
            func.to_char(Booking.arrival_date, 'YYYY-MM-DD').label('period'),
            func.sum(Booking.adr * Booking.total_nights).label('revenue')
        ).filter(
            Booking.is_canceled == False
        ).group_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM-DD')
        ).order_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM-DD')
        )
    elif period == 'weekly':
        query = session.query(
            func.to_char(Booking.arrival_date, 'YYYY-MM').label('month'),
            func.extract('week', Booking.arrival_date).label('week'),
            func.sum(Booking.adr * Booking.total_nights).label('revenue')
        ).filter(
            Booking.is_canceled == False
        ).group_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM'),
            func.extract('week', Booking.arrival_date)
        ).order_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM'),
            func.extract('week', Booking.arrival_date)
        )
    elif period == 'yearly':
        query = session.query(
            func.extract('year', Booking.arrival_date).label('period'),
            func.sum(Booking.adr * Booking.total_nights).label('revenue')
        ).filter(
            Booking.is_canceled == False
        ).group_by(
            func.extract('year', Booking.arrival_date)
        ).order_by(
            func.extract('year', Booking.arrival_date)
        )
    else:  
        query = session.query(
            func.to_char(Booking.arrival_date, 'YYYY-MM').label('period'),
            func.sum(Booking.adr * Booking.total_nights).label('revenue')
        ).filter(
            Booking.is_canceled == False
        ).group_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM')
        ).order_by(
            func.to_char(Booking.arrival_date, 'YYYY-MM')
        )
    
    revenue_data = pd.DataFrame(query.all())
    
    if period == 'weekly':
        revenue_data['period'] = revenue_data['month'] + '-W' + revenue_data['week'].astype(str).str.zfill(2)
        revenue_data = revenue_data[['period', 'revenue']]
    
    plt.figure(figsize=(12, 6))
    plt.plot(revenue_data['period'], revenue_data['revenue'], marker='o', linestyle='-')
    plt.title(f'Revenue Trends ({period.capitalize()})')
    plt.xlabel('Period')
    plt.ylabel('Revenue')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': revenue_data.to_dict(orient='records'),
        'plot': f"data:image/png;base64,{image_base64}"
    }

def get_revenue_by_hotel_type(session: Session):

    query = session.query(
        Hotel.type.label('hotel_type'),
        func.sum(Booking.adr * Booking.total_nights).label('revenue')
    ).join(
        Booking, Hotel.id == Booking.hotel_id
    ).filter(
        Booking.is_canceled == False
    ).group_by(
        Hotel.type
    )
    
    revenue_data = pd.DataFrame(query.all())
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(x='hotel_type', y='revenue', data=revenue_data)
    plt.title('Revenue by Hotel Type')
    plt.xlabel('Hotel Type')
    plt.ylabel('Revenue')
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': revenue_data.to_dict(orient='records'),
        'plot': f"data:image/png;base64,{image_base64}"
    }