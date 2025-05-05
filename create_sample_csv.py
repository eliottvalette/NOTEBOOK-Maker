import os
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression

# Génération de datasets synthétiques
def create_synthetic_datasets(n_samples=10_000, n_features=10, random_state=42):
    """Crée deux datasets synthétiques avec une colonne ID commune."""
    # Générer des IDs uniques
    ids = np.arange(1, n_samples + 1)
    
    # Calculer le nombre réel de features pour make_classification
    n_features_total = n_features * 2 - 2
    
    # Dataset 1 avec target (classification)
    X_class, y_class = make_classification(
        n_samples=n_samples, 
        n_features=n_features_total, 
        n_informative=5, 
        n_redundant=2,
        random_state=random_state
    )
    
    # Diviser les features entre les deux DataFrames - la moitié pour chacun
    features_per_df = n_features_total // 2
    
    # Créer les DataFrames avec le bon nombre de colonnes
    df1 = pd.DataFrame(X_class[:, :features_per_df], 
                      columns=[f'Feature_{i+1}' for i in range(features_per_df)])
    df2 = pd.DataFrame(X_class[:, features_per_df:], 
                      columns=[f'Extra_Feature_{i+1}' for i in range(X_class.shape[1] - features_per_df)])
    
    # Ajouter la target et l'ID
    df1['YTarget'] = y_class
    df1['ID'] = ids
    df2['ID'] = ids
    
    # Création des répertoires si nécessaire
    os.makedirs('Datasets/Tabular/Test', exist_ok=True)
    
    # Sauvegarde des datasets
    df1.to_csv('Datasets/Tabular/Binary_pred/dataset1_with_target.csv', index=False)
    df2.to_csv('Datasets/Tabular/Binary_pred/dataset2_features_only.csv', index=False)
    
    print(f"Datasets créés avec succès:")
    print(f"- dataset1_with_target.csv: {df1.shape} (avec colonne cible 'YTarget')")
    print(f"- dataset2_features_only.csv: {df2.shape}")
    
    return df1, df2

def create_time_series_dataset(n_samples=10_000, n_features=10, random_state=42):
    """
    Create a synthetic time series dataset with a 10 step prediction task
    Even if it's synthetic, it should be a good representation of a time series dataset and be predictable
    """
    # Set random seed for reproducibility
    np.random.seed(random_state)
    
    # Create a dataframe with time index
    dates = pd.date_range(start='2020-01-01', periods=n_samples, freq='D')
    df = pd.DataFrame(index=dates)
    
    # Add ID column
    df['ID'] = np.arange(1, n_samples + 1)
    
    # Create base features with different patterns
    for i in range(n_features):
        # Create a feature with trend
        if i % 3 == 0:
            # Linear trend with some noise
            trend = np.linspace(0, 10, n_samples) + np.random.normal(0, 0.5, n_samples)
            df[f'Feature_{i+1}'] = trend
        # Create a feature with seasonality
        elif i % 3 == 1:
            # Seasonal pattern with different frequencies
            period = 365 if i < 3 else 30 if i < 6 else 7
            seasonality = 5 * np.sin(2 * np.pi * np.arange(n_samples) / period) + np.random.normal(0, 0.3, n_samples)
            df[f'Feature_{i+1}'] = seasonality
        # Create a feature with both trend and seasonality
        else:
            # Combine trend and seasonality
            trend = np.linspace(0, 5, n_samples)
            period = 180 if i < 5 else 90
            seasonality = 3 * np.sin(2 * np.pi * np.arange(n_samples) / period)
            df[f'Feature_{i+1}'] = trend + seasonality + np.random.normal(0, 0.4, n_samples)
    
    # Create target variable that depends on previous values of features
    # Target is a function of the last 10 days of some features plus noise
    target = np.zeros(n_samples)
    
    for i in range(10, n_samples):
        # Target depends on the last 10 values of the first 3 features with decreasing weights
        weights = np.array([0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05])
        
        for j in range(3):  # Use only first 3 features for simplicity
            feature_values = df[f'Feature_{j+1}'].values[i-10:i]
            target[i] += np.sum(feature_values * weights)
        
        # Add some noise
        target[i] += np.random.normal(0, 1.0)
    
    # Add target to dataframe
    df['Target'] = target

    # Drop Index 
    df = df.reset_index(drop=True)

    # Create directory if it doesn't exist
    os.makedirs('Datasets/Tabular/Time_series', exist_ok=True)
    
    # Save dataset
    df.to_csv('Datasets/Tabular/Time_series/dataset_time_series.csv', index=True)
    
    print(f"Time series dataset created successfully:")
    print(f"- dataset_time_series.csv: {df.shape} (with target column 'Target')")
    
    return df


if __name__ == "__main__":
    create_synthetic_datasets()
    create_time_series_dataset()