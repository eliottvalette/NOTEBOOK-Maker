# prototype.py

"""
Pipeline automatisé pour l'analyse de données et le machine learning.

Ce script permet de:
1. Créer/charger deux CSV avec une colonne ID commune
2. Générer des questions automatiquement selon les données
3. Envoyer ces éléments à un LLM pour prise de décision
4. Générer dynamiquement un notebook avec nbformat
5. Exécuter le notebook et retourner les résultats
"""

import os
import pandas as pd
import numpy as np
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import nbclient
import yaml
import time
import random
from sklearn.datasets import make_classification, make_regression
from sample_cell_templates import CELL_TEMPLATES

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
    os.makedirs('Datasets/Both', exist_ok=True)
    
    # Sauvegarde des datasets
    df1.to_csv('Datasets/Both/dataset1_with_target.csv', index=False)
    df2.to_csv('Datasets/Both/dataset2_features_only.csv', index=False)
    
    return df1, df2

# Chargement des datasets
def load_datasets():
    """Charge deux datasets à partir des fichiers CSV."""
    try:
        df1 = pd.read_csv('Datasets/Both/dataset1_with_target.csv')
        df2 = pd.read_csv('Datasets/Both/dataset2_features_only.csv')
        print("Datasets chargés avec succès.")
    except FileNotFoundError:
        print("Datasets introuvables. Création de datasets synthétiques...")
        df1, df2 = create_synthetic_datasets()
        print("Datasets synthétiques créés et sauvegardés.")
    
    return df1, df2

# Génération des questions basées sur les données
def generate_questions(df1, df2):
    """Génère des questions pertinentes basées sur les attributs des données."""
    questions = {
        "questions": [
            {
                "id": "wants_prediction",
                "question": "Souhaitez-vous faire des prédictions ?",
                "type": "boolean"
            },
            {
                "id": "wants_price_analysis",
                "question": "Souhaitez-vous faire une analyse de prix ?",
                "type": "boolean"
            },
            {
                "id": "wants_gradboost",
                "question": "Souhaitez-vous utiliser un modèle Gradient Boosting ?",
                "type": "boolean"
            }
        ],
        "decision_tree": [
            {
                "if": "wants_prediction == true",
                "then": {
                    "actions": [
                        {"generate_cell": "prepare_and_train_model"}
                    ]
                }
            },
            {
                "if": "wants_price_analysis == true",
                "then": {
                    "actions": [
                        {"generate_cell": "price_analysis"}
                    ]
                }
            },
            {
                "if": "wants_gradboost == true",
                "then": {
                    "actions": [
                        {"generate_cell": "train_gradboost"}
                    ]
                }
            }
        ]
    }
    
    # Détecter si YTarget est une variable de classification ou de régression
    if 'YTarget' in df1.columns:
        y = df1['YTarget']
        is_classification = len(y.unique()) < 20
        
        if is_classification:
            questions["questions"].append({
                "id": "wants_classification_metrics",
                "question": "Souhaitez-vous voir les métriques de classification (précision, rappel, F1) ?",
                "type": "boolean"
            })
            questions["decision_tree"].append({
                "if": "wants_classification_metrics == true",
                "then": {
                    "actions": [
                        {"generate_cell": "classification_metrics"}
                    ]
                }
            })
        else:
            questions["questions"].append({
                "id": "wants_regression_metrics",
                "question": "Souhaitez-vous voir les métriques de régression (MSE, R²) ?",
                "type": "boolean"
            })
            questions["decision_tree"].append({
                "if": "wants_regression_metrics == true",
                "then": {
                    "actions": [
                        {"generate_cell": "regression_metrics"}
                    ]
                }
            })
    
    # Si on a plus de 5 features, proposer une réduction de dimension
    if len(df1.columns) > 5:
        questions["questions"].append({
            "id": "wants_dim_reduction",
            "question": "Souhaitez-vous effectuer une réduction de dimension (PCA) ?",
            "type": "boolean"
        })
        questions["decision_tree"].append({
            "if": "wants_dim_reduction == true",
            "then": {
                "actions": [
                    {"generate_cell": "dimension_reduction"}
                ]
            }
        })
    
    # Sauvegarde des questions en YAML
    with open('decision_tree.yaml', 'w') as f:
        yaml.dump(questions, f, default_flow_style=False)
    
    return questions

# Simulation de l'envoi au LLM et récupération des réponses
def get_llm_responses(questions):
    """Simule l'envoi des questions à un LLM et retourne des réponses"""
    # Dans une implémentation réelle, cette fonction enverrait les questions à Mistral
    # et traiterait les réponses. Pour l'instant, on simule des réponses.
    
    responses = {}
    for question in questions["questions"]:
        # Simuler une réponse aléatoire pour les questions booléennes
        if question["type"] == "boolean":
            responses[question["id"]] = random.choice([True, False])
    
    print("Réponses du LLM (simulées pour le prototype):")
    for key, value in responses.items():
        print(f"{key}: {value}")
    
    return responses

# Génération des cellules de code selon les réponses
def generate_notebook_cells(df1, df2, responses):
    """Génère les cellules de code pour le notebook basé sur les réponses."""
    cells = []
    
    # Cellule d'import standard
    imports_cell = new_code_cell(
        """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
"""
    )
    cells.append(imports_cell)
    
    # Cellule de chargement des données
    load_data_cell = new_code_cell(
        """
# Charger les datasets
df1 = pd.read_csv('Datasets/Both/dataset1_with_target.csv')
df2 = pd.read_csv('Datasets/Both/dataset2_features_only.csv')

# Fusionner les datasets sur l'ID
df = pd.merge(df1, df2, on='ID', how='inner')

# Afficher les premières lignes
print("Dimensions du dataset fusionné:", df.shape)
df.head()
"""
    )
    cells.append(load_data_cell)
    
    # Analyses exploratoires
    eda_cell = new_code_cell(
        """
# Statistiques descriptives
print("Statistiques descriptives:")
df.describe()
"""
    )
    cells.append(eda_cell)
    
    # Cellules conditionnelles en fonction des réponses et de l'arbre de décision
    if responses.get("wants_prediction", False):
        cells.append(new_markdown_cell("## Préparation et entraînement du modèle"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("prepare_and_train_model", "")))
    
    if responses.get("wants_gradboost", False):
        cells.append(new_markdown_cell("## Entraînement du modèle Gradient Boosting"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("train_gradboost", "")))
    
    if responses.get("wants_price_analysis", False):
        cells.append(new_markdown_cell("## Analyse des prix"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("price_analysis", "")))
    
    if responses.get("wants_classification_metrics", False):
        cells.append(new_markdown_cell("## Métriques de classification détaillées"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("classification_metrics", "")))
    
    if responses.get("wants_regression_metrics", False):
        cells.append(new_markdown_cell("## Métriques de régression détaillées"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("regression_metrics", "")))
    
    if responses.get("wants_dim_reduction", False):
        cells.append(new_markdown_cell("## Réduction de dimension avec PCA"))
        cells.append(new_code_cell(CELL_TEMPLATES.get("dimension_reduction", "")))
    
    # Ajout d'une cellule de conclusion
    cells.append(new_markdown_cell("## Conclusion"))
    cells.append(new_code_cell(
        """
# Résumé des opérations effectuées
print("Résumé des analyses effectuées:")

# Afficher les réponses du LLM
responses = {}
"""
        + "\n".join([f"responses['{key}'] = {value}" for key, value in responses.items()]) +
        """

for key, value in responses.items():
    print(f"- {key}: {'Oui' if value else 'Non'}")

# Sauvegarder le modèle si entraîné
if 'model' in locals():
    import joblib
    joblib.dump(model, 'trained_model.joblib')
    print("Le modèle a été sauvegardé dans 'trained_model.joblib'")
"""
    ))
    
    return cells

# Création et exécution du notebook
def create_and_execute_notebook(cells):
    """Crée un notebook avec les cellules fournies et l'exécute."""
    # Création du notebook
    nb = new_notebook()
    nb.cells = cells
    
    # Sauvegarde du notebook
    notebook_path = 'generated_notebook.ipynb'
    with open(notebook_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"Notebook créé: {notebook_path}")
    
    # Exécution du notebook
    try:
        client = nbclient.NotebookClient(nb, timeout=600)
        executed_nb = client.execute()
        
        # Sauvegarde du notebook exécuté
        executed_path = 'executed_notebook.ipynb'
        with open(executed_path, 'w') as f:
            nbformat.write(executed_nb, f)
        
        print(f"Notebook exécuté et sauvegardé: {executed_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'exécution du notebook: {e}")
        return False

def main():
    """Fonction principale qui orchestre tout le pipeline."""
    print("Démarrage du pipeline automatisé...")
    
    # Chargement ou création des datasets
    df1, df2 = load_datasets()
    
    # Génération des questions basées sur les données
    questions = generate_questions(df1, df2)
    
    # Simulation de l'envoi au LLM et récupération des réponses
    responses = get_llm_responses(questions)
    
    # Génération des cellules du notebook
    cells = generate_notebook_cells(df1, df2, responses)
    
    # Création et exécution du notebook
    success = create_and_execute_notebook(cells)
    
    if success:
        print("Pipeline terminé avec succès!")
    else:
        print("Le pipeline s'est terminé avec des erreurs.")

if __name__ == "__main__":
    main()