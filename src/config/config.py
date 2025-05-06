"""
Configuration module for the notebook maker application.
Contains all global settings and configurations.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# File paths
DATASET_DIR = 'Datasets'
OUTPUT_DIR = 'Output'

# Dataset paths
DATASET_PATHS = {
    'binary_pred': {
        'dataset1': os.path.join(DATASET_DIR, 'Tabular/Binary_pred/dataset1_with_target.csv'),
        'dataset2': os.path.join(DATASET_DIR, 'Tabular/Binary_pred/dataset2_features_only.csv')
    },
    'time_series': {
        'dataset': os.path.join(DATASET_DIR, 'Tabular/Time_series/dataset_time_series.csv')
    }
}

# Decision tree paths
DECISION_TREE_PATHS = {
    'preprocessing': 'decision_tree_preprocessing.yaml',
    'modelling': 'decision_tree_modelling.yaml'
}

# Model parameters
MODEL_PARAMS = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'xgboost': {
        'max_depth': 6,
        'eta': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8
    },
    'lstm': {
        'hidden_size': 128,
        'num_layers': 2,
        'dropout': 0.2
    }
}

# Notebook settings
NOTEBOOK_SETTINGS = {
    'default_theme': 'ggplot',
    'figure_size': (12, 8),
    'dpi': 100
} 