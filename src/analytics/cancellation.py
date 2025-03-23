import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import func, desc, extract
from sqlalchemy.orm import Session
import io
import base64
from src.data.db_manager import Booking, Country, Hotel

def get_cancellation_rate(session: Session):

    total_bookings = session.query(func.count(Booking.id)).scalar()
    canceled_bookings = session.query(func.count(Booking.id)).filter(Booking.is_canceled == True).scalar()
    
    cancellation_rate = (canceled_bookings / total_bookings) * 100 if total_bookings > 0 else 0
    
    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        [canceled_bookings, total_bookings - canceled_bookings],
        labels=['Canceled', 'Confirmed'],
        autopct='%1.1f%%',
        startangle=90,
        colors=['#ff9999', '#66b3ff']
    )
    plt.title('Booking Cancellation Rate')
    plt.axis('equal')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': {
            'total_bookings': total_bookings,
            'canceled_bookings': canceled_bookings,
            'confirmed_bookings': total_bookings - canceled_bookings,
            'cancellation_rate': cancellation_rate
        },
        'plot': f"data:image/png;base64,{image_base64}"
    }

def get_cancellation_by_country(session: Session, top_n: int = 10):

    country_stats = session.query(
        Country.name.label('country'),
        func.count(Booking.id).label('total_bookings'),
        func.sum(func.cast(Booking.is_canceled, 'integer')).label('canceled_bookings')
    ).join(
        Booking, Country.id == Booking.country_id
    ).group_by(
        Country.name
    ).having(
        func.count(Booking.id) > 10  
    ).order_by(
        desc('total_bookings')
    ).limit(top_n).all()
    
    df = pd.DataFrame(country_stats)
    
    df['cancellation_rate'] = (df['canceled_bookings'] / df['total_bookings'] * 100).round(2)
    
    df = df.sort_values('cancellation_rate', ascending=False)
    
    # Create visualization
    plt.figure(figsize=(12, 6))
    bars = plt.bar(df['country'], df['cancellation_rate'])
    
    for i, bar in enumerate(bars):
        if df['cancellation_rate'].iloc[i] > 50:
            bar.set_color('#ff6666')  
        elif df['cancellation_rate'].iloc[i] > 30:
            bar.set_color('#ffcc66') 
        else:
            bar.set_color('#66cc66') 
    
    plt.title(f'Cancellation Rate by Country (Top {top_n})')
    plt.xlabel('Country')
    plt.ylabel('Cancellation Rate (%)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': df.to_dict(orient='records'),
        'plot': f"data:image/png;base64,{image_base64}"
    }

def get_cancellation_by_month(session: Session):

    monthly_stats = session.query(
        extract('month', Booking.arrival_date).label('month'),
        func.count(Booking.id).label('total_bookings'),
        func.sum(func.cast(Booking.is_canceled, 'integer')).label('canceled_bookings')
    ).group_by(
        extract('month', Booking.arrival_date)
    ).order_by(
        'month'
    ).all()
    
    df = pd.DataFrame(monthly_stats)
    
    df['cancellation_rate'] = (df['canceled_bookings'] / df['total_bookings'] * 100).round(2)
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['month_name'] = df['month'].apply(lambda x: month_names[int(x)-1])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['month_name'], df['cancellation_rate'], marker='o', linestyle='-', color='#3366cc')
    plt.title('Cancellation Rate by Month')
    plt.xlabel('Month')
    plt.ylabel('Cancellation Rate (%)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': df.to_dict(orient='records'),
        'plot': f"data:image/png;base64,{image_base64}"
    }