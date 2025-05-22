# manual_load.py

import os
import pandas as pd
from pathlib import Path
from typing import List

def get_datasets_paths(dataset_style : str) -> List[str]:
    """Load datasets based on the dataset style or a custom path."""
    print(f"Loading datasets for style: {dataset_style}")
    if dataset_style == 'A_1_one_csv':
        # Single CSV with target
        df_path = Path('datasets') / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset1_with_target.csv'
        return [df_path]
    elif dataset_style == 'B_2_joinable_csvs':
        # Two joinable CSVs
        df1_path = Path('datasets') / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset1_with_target.csv'
        df2_path = Path('datasets') / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset2_features_only.csv'
        
        return [df1_path, df2_path]
        
    elif dataset_style == 'C_1_csv_time_series':
        # Time series CSV
        df_path = Path('datasets') / 'Tabular' / 'Time_series' / 'csv' / 'dataset_time_series.csv'
        if not df_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {df_path}")
        return [df_path]
    
    elif dataset_style == 'test':
        # Test dataset
        df_path = Path('datasets') / 'Tabular' / 'Binary_pred' / 'excel' / 'dataset1_with_target.xlsx'
        return [df_path]
        
    else:
        raise ValueError(f"Unknown dataset style: {dataset_style}")