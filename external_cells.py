"""
Ce fichier contient les définitions des cellules de notebook utilisées par prototype.py.
Il permet de séparer la logique de génération du notebook du reste du code.
"""

import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

def get_intro_cells():
    """Retourne les cellules d'introduction du notebook.
    
    Returns:
        list: Liste de cellules d'introduction
    """
    cells = []
    
    # Cellule de titre
    cells.append(new_markdown_cell("# Analyse de données automatisée\n\nCe notebook a été généré automatiquement en fonction des données fournies et des réponses au formulaire."))
    
    # Cellule d'imports
    imports_cell = new_code_cell("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')
""")
    cells.append(imports_cell)
    
    return cells

def get_analysis_cells(df1, df2):
    """Retourne les cellules d'analyse en fonction des données.
    
    Args:
        df1 (DataFrame): Premier dataset
        df2 (DataFrame): Deuxième dataset
        
    Returns:
        list: Liste de cellules d'analyse
    """
    cells = []
    
    # Analyse de la variable cible (si présente)
    if 'YTarget' in df1.columns:
        target_analysis_cell = new_code_cell("""
# Analyse de la variable cible
if 'YTarget' in merged_df.columns:
    print("Distribution de la variable cible:")
    target_counts = merged_df['YTarget'].value_counts()
    print(target_counts)
    
    plt.figure(figsize=(10, 6))
    sns.countplot(x='YTarget', data=merged_df)
    plt.title('Distribution de la variable cible')
    plt.show()
""")
        cells.append(target_analysis_cell)
    
        # Ajouter une cellule pour créer un modèle de base
        model_cell = new_code_cell("""
# Préparation des données pour la modélisation
if 'YTarget' in merged_df.columns:
    # Séparer les features et la cible
    X = merged_df.drop(['YTarget', 'ID'], axis=1)
    y = merged_df['YTarget']
    
    # Diviser en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîner un modèle GradientBoosting
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluer le modèle
    y_pred = model.predict(X_test)
    
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1 Score:", f1_score(y_test, y_pred))
    
    # Afficher la matrice de confusion
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Matrice de confusion')
    plt.xlabel('Prédit')
    plt.ylabel('Réel')
    plt.show()
    
    # Afficher l'importance des features
    plt.figure(figsize=(12, 8))
    feature_importance = pd.DataFrame({
        'features': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    sns.barplot(x='importance', y='features', data=feature_importance.head(15))
    plt.title('Importance des features')
    plt.show()
""")
        cells.append(model_cell)
    
    # Ajouter d'autres cellules d'analyse selon les besoins
    # Par exemple, une analyse exploratoire des données
    eda_cell = new_code_cell("""
# Analyse exploratoire des données
if 'merged_df' in locals():
    # Afficher les corrélations
    plt.figure(figsize=(12, 10))
    corr_matrix = merged_df.select_dtypes(include=[np.number]).corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=False, cmap='coolwarm', linewidths=0.5)
    plt.title('Matrice de corrélation')
    plt.tight_layout()
    plt.show()
    
    # Distribution des variables numériques
    num_cols = merged_df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        print("\nDistribution des variables numériques:")
        n_cols = min(len(num_cols), 4)
        n_rows = (len(num_cols) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 3*n_rows))
        axes = axes.flatten()
        
        for i, col in enumerate(num_cols):
            if i < len(axes):
                sns.histplot(merged_df[col], kde=True, ax=axes[i])
                axes[i].set_title(f'Distribution de {col}')
        
        # Masquer les axes supplémentaires si nécessaire
        for j in range(i+1, len(axes)):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        plt.show()
""")
    cells.append(eda_cell)
    
    return cells

def get_conclusion_cells():
    """Retourne les cellules de conclusion du notebook.
    
    Returns:
        list: Liste de cellules de conclusion
    """
    cells = []
    
    # Cellule de conclusion
    cells.append(new_markdown_cell("## Conclusion\n\nCe notebook a automatiquement analysé vos données et créé un modèle de base. Vous pouvez maintenant explorer davantage les données et améliorer le modèle selon vos besoins."))
    
    # Éventuellement ajouter d'autres cellules de conclusion ici
    # Par exemple, des suggestions pour améliorer le modèle
    cells.append(new_markdown_cell("""
### Suggestions d'amélioration

1. **Prétraitement des données**
   - Traiter les valeurs manquantes avec des techniques comme l'imputation
   - Normaliser ou standardiser les variables numériques
   - Encoder les variables catégorielles

2. **Feature Engineering**
   - Créer de nouvelles caractéristiques pertinentes
   - Réduire la dimensionnalité avec PCA ou t-SNE
   - Sélectionner les features les plus importantes

3. **Modélisation**
   - Tester différents algorithmes (Random Forest, XGBoost, etc.)
   - Optimiser les hyperparamètres avec GridSearchCV
   - Utiliser des techniques d'ensemble

4. **Évaluation**
   - Effectuer une validation croisée
   - Analyser les erreurs de prédiction
   - Comparer les performances avec des métriques adaptées
"""))
    
    return cells

# Ajouter d'autres fonctions pour des types de cellules spécifiques si nécessaire
def get_regression_cells():
    """Retourne les cellules spécifiques à une régression.
    
    Returns:
        list: Liste de cellules pour la régression
    """
    cells = []
    
    # Cellule de modèle de régression
    regression_cell = new_code_cell("""
# Modèle de régression
if 'YTarget' in merged_df.columns and merged_df['YTarget'].dtype in [np.float64, np.int64]:
    # Séparer les features et la cible
    X = merged_df.drop(['YTarget', 'ID'], axis=1)
    y = merged_df['YTarget']
    
    # Diviser en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîner un modèle GradientBoosting pour la régression
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluer le modèle
    y_pred = model.predict(X_test)
    
    print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
    print("Root Mean Squared Error:", np.sqrt(mean_squared_error(y_test, y_pred)))
    print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
    print("R² Score:", r2_score(y_test, y_pred))
    
    # Afficher les prédictions vs valeurs réelles
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Valeurs réelles')
    plt.ylabel('Prédictions')
    plt.title('Prédictions vs Valeurs réelles')
    plt.show()
    
    # Afficher l'importance des features
    plt.figure(figsize=(12, 8))
    feature_importance = pd.DataFrame({
        'features': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    sns.barplot(x='importance', y='features', data=feature_importance.head(15))
    plt.title('Importance des features')
    plt.show()
""")
    cells.append(regression_cell)
    
    return cells 