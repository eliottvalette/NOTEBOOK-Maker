import os
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression

# Génération de datasets synthétiques
def create_synthetic_datasets(n_samples=1000, n_features=10, random_state=42):
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

def create_time_series_dataset(n_samples=1000, n_features=10, random_state=42):
    """Crée un dataset de séries temporelles synthétiques."""
    # Générer des IDs uniques
    ids = np.arange(1, n_samples + 1)
    
    # Créer les features temporelles
    time_steps = np.arange(n_samples)
    features = np.random.randn(n_samples, n_features)
    
    # Créer la cible
    target = np.sum(features, axis=1) + np.random.randn(n_samples)
    
    # Créer le DataFrame
    df = pd.DataFrame({
        'ID': ids,
        'TimeStep': time_steps,
        'Feature1': features[:, 0],
        'Feature2': features[:, 1],
        'Target': target
    })
    
    # Sauvegarder le DataFrame
    df.to_csv('Datasets/Tabular/Time_series/dataset_time_series.csv', index=False)
    
    print(f"Dataset de séries temporelles créé avec succès:")
    print(f"- dataset_time_series.csv: {df.shape}")
    
    return df


if __name__ == "__main__":
    create_synthetic_datasets()
    create_time_series_dataset()