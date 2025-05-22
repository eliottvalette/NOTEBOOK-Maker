"""
Utilities for extracting insights from datasets.
"""

import pandas as pd
from typing import List, Dict, Any
from .config import load_form_answers

def get_insights_on_df(df_path: str, idx: int, target_col_name: str = 'None') -> str:
    """Get insights from a single dataset."""

    df_path = str(df_path)  # Ensure df_path is a string
    if df_path.split('.')[-1] == 'csv':
        df = pd.read_csv(df_path)
    elif df_path.split('.')[-1] == 'xlsx':
        df = pd.read_excel(df_path)
    elif df_path.split('.')[-1] == 'parquet':
        df = pd.read_parquet(df_path)

    insights = f"Insights from dataset {idx}:\n"
    
    # Shape
    insights += f"Shape: {df.shape}\n"
    
    # Info about columns and data types
    insights += f"Columns: {list(df.columns)}\n"
    insights += f"Data types:\n{df.dtypes.to_string()}\n"
    
    # Missing values
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        insights += f"Missing values:\n{missing_values[missing_values > 0].to_string()}\n"
    else:
        insights += "No missing values found.\n"
    
    # Sample data
    insights += f"Sample data (first 3 rows):\n{df.head(3).to_string()}\n"
    
    # For target column if it exists
    if target_col_name != 'None':
        if target_col_name in df.columns:
            insights += f"Target distribution:\n"
            insights += f"Unique values: {df[target_col_name].nunique()}\n"
            insights += f"Value counts:\n{df[target_col_name].value_counts().to_string()}\n"
        else:
            insights += f"Target column '{target_col_name}' not found in the dataset.\n"
    
    return insights

def get_insights_and_answers(*dfs_paths: List[str], 
                            ans_preprocessing: str) -> str:
    """Gather insights from all datasets and form answers."""
    insights = ""
    for i, df_path in enumerate(dfs_paths, start=1):
        df_path_str = str(df_path)
        if df_path_str.split('.')[-1] in ['csv', 'xlsx', 'parquet']:
            insights += get_insights_on_df(df_path_str, i)
            insights += "\n"
    
    # Add form answers
    insights += "User's form answers:\n"
    insights += str(ans_preprocessing)
    
    return insights

def get_insights_for_modelling(insights: str, 
                               ans_modelling: str) -> str:
    """Prepare insights for the modelling phase."""
    insights_modelling = insights + "\n\nUser's form answers for modelling:\n"
    insights_modelling += str(ans_modelling)
    return insights_modelling 