import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
import io
import base64
from src.data.db_manager import Booking, Country

def get_geographic_distribution(session: Session, top_n: int = 15):

    country_stats = session.query(
        Country.name.label('country'),
        func.count(Booking.id).label('bookings')
    ).join(
        Booking, Country.id == Booking.country_id
    ).group_by(
        Country.name
    ).order_by(
        desc('bookings')
    ).limit(top_n).all()
    
    df = pd.DataFrame(country_stats)
    
    total_bookings = df['bookings'].sum()
    df['percentage'] = (df['bookings'] / total_bookings * 100).round(2)
    
    plt.figure(figsize=(10, 8))
    bars = plt.barh(df['country'], df['bookings'])
    
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(df)))
    for i, bar in enumerate(bars):
        bar.set_color(colors[i])
    
    plt.title(f'Geographical Distribution of Bookings (Top {top_n} Countries)')
    plt.xlabel('Number of Bookings')
    plt.ylabel('Country')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    # Create pie chart 
    plt.figure(figsize=(10, 8))
    top5 = df.head(5).copy()
    others = pd.DataFrame([{
        'country': 'Others',
        'bookings': df.iloc[5:]['bookings'].sum(),
        'percentage': df.iloc[5:]['percentage'].sum()
    }])
    pie_data = pd.concat([top5, others])
    
    plt.pie(
        pie_data['bookings'],
        labels=pie_data['country'],
        autopct='%1.1f%%',
        startangle=90,
        colors=plt.cm.Paired(np.linspace(0, 1, len(pie_data)))
    )
    plt.title('Top 5 Countries by Booking Volume')
    plt.axis('equal')
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    pie_image_base64 = base64.b64encode(buffer2.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': df.to_dict(orient='records'),
        'bar_plot': f"data:image/png;base64,{image_base64}",
        'pie_plot': f"data:image/png;base64,{pie_image_base64}"
    }