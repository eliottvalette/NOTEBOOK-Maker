import os
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression

# Génération de datasets synthétiques
def create_synthetic_datasets(n_samples=1000, n_features=10, random_state=42):
    """Crée deux datasets synthétiques avec une colonne ID commune."""
    # Générer des IDs uniques
    ids = np.arange(1, n_samples + 1)
    
    # Dataset 1 avec target (classification)
    X_class, y_class = make_classification(
        n_samples=n_samples, 
        n_features=n_features-1, 
        n_informative=5, 
        n_redundant=2,
        random_state=random_state
    )
    
    df1 = pd.DataFrame(X_class, columns=[f'Feature_{i+1}' for i in range(n_features-1)])
    df1['YTarget'] = y_class
    df1['ID'] = ids
    
    # Dataset 2 sans target mais avec des features supplémentaires
    X_reg, _ = make_regression(
        n_samples=n_samples, 
        n_features=n_features, 
        n_informative=7,
        random_state=random_state
    )
    
    df2 = pd.DataFrame(X_reg, columns=[f'Extra_Feature_{i+1}' for i in range(n_features)])
    df2['ID'] = ids
    
    # Création des répertoires si nécessaire
    os.makedirs('Datasets/Tabular/Test', exist_ok=True)
    
    # Sauvegarde des datasets
    df1.to_csv('Datasets/Tabular/Test/dataset1_with_target.csv', index=False)
    df2.to_csv('Datasets/Tabular/Test/dataset2_features_only.csv', index=False)
    
    return df1, df2

if __name__ == "__main__":
    create_synthetic_datasets()