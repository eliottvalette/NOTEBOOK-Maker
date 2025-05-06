"""
Utilities for extracting insights from datasets.
"""

import pandas as pd
from typing import List, Dict, Any
from .config import load_form_answers

def get_insights(df: pd.DataFrame, idx: int) -> str:
    """Get insights from a single dataset."""
    insights = f"Insights from dataset {idx}:\n"
    
    try:
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
        if 'YTarget' in df.columns:
            insights += f"Target distribution:\n"
            insights += f"Unique values: {df['YTarget'].nunique()}\n"
            insights += f"Value counts:\n{df['YTarget'].value_counts().to_string()}\n"
        
        return insights
    except Exception as e:
        return f"Error getting insights from dataset {idx}: {str(e)}\n"

def get_insights_and_answers(*dfs: pd.DataFrame) -> str:
    """Gather insights from all datasets and form answers."""
    insights = ""
    for i, df in enumerate(dfs, 1):
        insights += get_insights(df, i)
        insights += "\n"
    
    # Add form answers
    form_answers_preprocessing, _, _, _ = load_form_answers('A_1_one_csv')  # Default to first style
    insights += "User's form answers:\n"
    insights += str(form_answers_preprocessing)
    
    return insights

def get_insights_for_modelling(insights: str) -> str:
    """Prepare insights for the modelling phase."""
    _, form_answers_modelling, _, _ = load_form_answers('A_1_one_csv')  # Default to first style
    insights_modelling = insights + "\n\nUser's form answers for modelling:\n"
    insights_modelling += str(form_answers_modelling)
    return insights_modelling 