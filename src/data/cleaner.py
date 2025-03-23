import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    df_clean = df.copy()
    

    if 'children' in df_clean.columns:
        df_clean['children'] = df_clean['children'].fillna(0)
    
    if 'country' in df_clean.columns:
        df_clean['country'] = df_clean['country'].fillna('UNK')
    
    if 'adr' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['adr'])
    
    if 'children' in df_clean.columns:
        df_clean['children'] = df_clean['children'].astype(int)
    
    if 'babies' in df_clean.columns:
        df_clean['babies'] = df_clean['babies'].astype(int)
    
    if 'is_canceled' in df_clean.columns:
        df_clean['is_canceled'] = df_clean['is_canceled'].astype(bool)
    
    if all(col in df_clean.columns for col in ['arrival_date_year', 'arrival_date_month', 'arrival_date_day_of_month']):
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        if df_clean['arrival_date_month'].dtype == 'object':
            df_clean['arrival_date_month'] = df_clean['arrival_date_month'].map(month_map)
        
        df_clean['arrival_date'] = pd.to_datetime(
            dict(
                year=df_clean['arrival_date_year'],
                month=df_clean['arrival_date_month'],
                day=df_clean['arrival_date_day_of_month']
            )
        )
    
    if all(col in df_clean.columns for col in ['stays_in_weekend_nights', 'stays_in_week_nights']):
        df_clean['total_nights'] = df_clean['stays_in_weekend_nights'] + df_clean['stays_in_week_nights']
    
    if 'arrival_date' in df_clean.columns and 'total_nights' in df_clean.columns:
        df_clean['departure_date'] = df_clean.apply(
            lambda row: row['arrival_date'] + timedelta(days=int(row['total_nights'])),
            axis=1
        )
    
    if 'total_nights' in df_clean.columns:
        df_clean = df_clean[df_clean['total_nights'] > 0]
    
    if 'adr' in df_clean.columns:
        df_clean = df_clean[df_clean['adr'] > 0]
    
    return df_clean