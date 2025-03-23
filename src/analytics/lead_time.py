import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session
import io
import base64
from src.data.db_manager import Booking, Hotel

def get_lead_time_distribution(session: Session):

    lead_times = session.query(Booking.lead_time).all()
    
    lead_times = [lt[0] for lt in lead_times]
    
    stats = {
        'mean': np.mean(lead_times),
        'median': np.median(lead_times),
        'min': np.min(lead_times),
        'max': np.max(lead_times),
        'std': np.std(lead_times),
        'quantiles': {
            '25%': np.percentile(lead_times, 25),
            '50%': np.percentile(lead_times, 50),
            '75%': np.percentile(lead_times, 75),
            '90%': np.percentile(lead_times, 90),
        }
    }
    
    plt.figure(figsize=(12, 6))
    sns.histplot(lead_times, bins=30, kde=True)
    plt.title('Distribution of Booking Lead Time')
    plt.xlabel('Lead Time (days)')
    plt.ylabel('Count')
    plt.grid(True, alpha=0.3)
    plt.axvline(stats['mean'], color='r', linestyle='--', label=f"Mean: {stats['mean']:.1f} days")
    plt.axvline(stats['median'], color='g', linestyle='-.', label=f"Median: {stats['median']:.1f} days")
    plt.legend()
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    histogram_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    lead_by_hotel = session.query(
        Hotel.type.label('hotel_type'),
        Booking.lead_time
    ).join(
        Booking, Hotel.id == Booking.hotel_id
    ).all()
    
    lead_by_hotel_df = pd.DataFrame(lead_by_hotel)
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='hotel_type', y='lead_time', data=lead_by_hotel_df)
    plt.title('Lead Time Distribution by Hotel Type')
    plt.xlabel('Hotel Type')
    plt.ylabel('Lead Time (days)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    boxplot_base64 = base64.b64encode(buffer2.read()).decode('utf-8')
    plt.close()
    
    return {
        'stats': stats,
        'histogram': f"data:image/png;base64,{histogram_base64}",
        'boxplot': f"data:image/png;base64,{boxplot_base64}"
    }

def get_lead_time_vs_cancellation(session: Session):

    cancellation_data = session.query(
        Booking.lead_time,
        Booking.is_canceled
    ).all()
    
    df = pd.DataFrame(cancellation_data, columns=['lead_time', 'is_canceled'])
    
    lead_time_bins = [0, 7, 30, 90, 180, 365, float('inf')]
    bin_labels = ['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days', '>365 days']
    df['lead_time_group'] = pd.cut(df['lead_time'], bins=lead_time_bins, labels=bin_labels)
    
    cancellation_by_leadtime = df.groupby('lead_time_group').agg(
        total_bookings=('is_canceled', 'count'),
        canceled_bookings=('is_canceled', 'sum')
    )
    cancellation_by_leadtime['cancellation_rate'] = (
        cancellation_by_leadtime['canceled_bookings'] / cancellation_by_leadtime['total_bookings'] * 100
    ).round(2)
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(
        cancellation_by_leadtime.index,
        cancellation_by_leadtime['cancellation_rate'],
        color=plt.cm.RdYlGn_r(np.linspace(0, 0.8, len(cancellation_by_leadtime)))
    )
    plt.title('Cancellation Rate by Lead Time')
    plt.xlabel('Lead Time Group')
    plt.ylabel('Cancellation Rate (%)')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save plot to base64 encoded string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return {
        'data': cancellation_by_leadtime.reset_index().to_dict(orient='records'),
        'plot': f"data:image/png;base64,{image_base64}"
    }