"""
Data loading and preprocessing module.
Handles all data loading and initial preprocessing operations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Union, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Class for loading and preprocessing data."""
    
    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """
        Load a CSV file into a pandas DataFrame.
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.EmptyDataError: If the file is empty
        """
        try:
            logger.info(f"Loading CSV file: {filepath}")
            df = pd.read_csv(filepath)
            logger.info(f"Successfully loaded CSV file. Shape: {df.shape}")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"Empty file: {filepath}")
            raise
    
    @staticmethod
    def load_multiple_csvs(filepaths: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Load multiple CSV files into a dictionary of DataFrames.
        
        Args:
            filepaths (List[str]): List of paths to CSV files
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of loaded DataFrames
        """
        dataframes = {}
        for filepath in filepaths:
            try:
                df = DataLoader.load_csv(filepath)
                dataframes[filepath] = df
            except Exception as e:
                logger.error(f"Error loading {filepath}: {str(e)}")
                continue
        return dataframes
    
    @staticmethod
    def merge_dataframes(dataframes: Dict[str, pd.DataFrame], 
                        common_id: str,
                        how: str = 'outer') -> pd.DataFrame:
        """
        Merge multiple DataFrames on a common ID column.
        
        Args:
            dataframes (Dict[str, pd.DataFrame]): Dictionary of DataFrames to merge
            common_id (str): Name of the common ID column
            how (str): Type of merge to perform ('inner', 'outer', 'left', 'right')
            
        Returns:
            pd.DataFrame: Merged DataFrame
        """
        try:
            logger.info(f"Merging {len(dataframes)} DataFrames on {common_id}")
            merged_df = None
            
            for df_name, df in dataframes.items():
                if common_id not in df.columns:
                    logger.warning(f"Column {common_id} not found in {df_name}")
                    continue
                    
                if merged_df is None:
                    merged_df = df.copy()
                else:
                    merged_df = pd.merge(
                        merged_df, 
                        df, 
                        on=common_id, 
                        how=how,
                        suffixes=('', f'_{df_name}')
                    )
            
            if merged_df is None:
                raise ValueError("No valid DataFrames to merge")
                
            logger.info(f"Successfully merged DataFrames. Final shape: {merged_df.shape}")
            return merged_df
            
        except Exception as e:
            logger.error(f"Error merging DataFrames: {str(e)}")
            raise
    
    @staticmethod
    def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform basic preprocessing on a DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: Preprocessed DataFrame
        """
        try:
            logger.info("Starting DataFrame preprocessing")
            
            # Handle missing values
            df = df.fillna(df.mean(numeric_only=True))
            
            # Convert categorical columns to numerical
            df = pd.get_dummies(df)
            
            logger.info(f"Preprocessing complete. New shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing DataFrame: {str(e)}")
            raise 