import pandas as pd
import os
from typing import Optional
from src.config import DEFAULT_DATASET, PROCESSED_DATA_DIR

def load_raw_data(file_path: Optional[str] = None) -> pd.DataFrame:

    file_path = file_path or DEFAULT_DATASET
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at {file_path}")
    
    print(f"Loading data from {file_path}")
    return pd.read_csv(file_path)

def save_processed_data(df: pd.DataFrame, file_name: str = "processed_bookings.csv") -> str:

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    output_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")
    return output_path