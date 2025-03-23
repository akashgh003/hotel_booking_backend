import pandas as pd
import io
import base64
from sqlalchemy.orm import Session
from src.analytics.revenue import get_revenue_trends, get_revenue_by_hotel_type
from src.analytics.cancellation import get_cancellation_rate, get_cancellation_by_country, get_cancellation_by_month
from src.analytics.geographic import get_geographic_distribution
from src.analytics.lead_time import get_lead_time_distribution, get_lead_time_vs_cancellation

def generate_analytics_report(session: Session):

    report = {
        'revenue': {
            'trends': get_revenue_trends(session, 'monthly'),
            'by_hotel_type': get_revenue_by_hotel_type(session)
        },
        'cancellation': {
            'overall_rate': get_cancellation_rate(session),
            'by_country': get_cancellation_by_country(session),
            'by_month': get_cancellation_by_month(session)
        },
        'geography': {
            'distribution': get_geographic_distribution(session)
        },
        'lead_time': {
            'distribution': get_lead_time_distribution(session),
            'vs_cancellation': get_lead_time_vs_cancellation(session)
        }
    }
    
    return report