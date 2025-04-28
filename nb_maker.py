"""
RUN :
pip install nbformat nbclient  
pip install ipykernel jupyter nbclient nbformat
python nb_maker.py
"""
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

# Création d'un notebook vide
nb = new_notebook()

# Ajout d'un titre
nb.cells.append(new_markdown_cell('# Analyse de données et Gradient Boosting\n\nCe notebook démontre l\'utilisation de XGBoost sur un jeu de données synthétique.'))

# Installation des dépendances
nb.cells.append(new_markdown_cell('## Installation des dépendances nécessaires'))

nb.cells.append(new_code_cell('''
!pip install pandas
!pip install matplotlib
!pip install seaborn
!pip install scikit-learn
!pip install xgboost
!pip install graphviz
'''))

# Importation des librairies
nb.cells.append(new_code_cell('''
# Importation des librairies nécessaires
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
'''))

# Création d'un dataset synthétique
nb.cells.append(new_markdown_cell('## Génération d\'un jeu de données synthétique'))

nb.cells.append(new_code_cell('''
# Création d\'un dataset synthétique pour la classification
from sklearn.datasets import make_classification

# Génération des données
X, y = make_classification(
    n_samples=1000, 
    n_features=20,
    n_informative=10,
    n_redundant=5,
    n_classes=2,
    random_state=42
)

# Conversion en DataFrame pour une meilleure visualisation
df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
df['target'] = y

# Affichage des premières lignes
print("Aperçu du jeu de données:")
df.head()
'''))

# Exploration des données
nb.cells.append(new_markdown_cell('## Exploration des données'))

nb.cells.append(new_code_cell('''
# Statistiques descriptives
print("Statistiques descriptives:")
df.describe()
'''))

nb.cells.append(new_code_cell('''
# Visualisation de la distribution des classes
plt.figure(figsize=(8, 6))
sns.countplot(x='target', data=df)
plt.title('Distribution des classes')
plt.show()
'''))

nb.cells.append(new_code_cell('''
# Visualisation de quelques caractéristiques
plt.figure(figsize=(12, 10))
sns.pairplot(df[['feature_0', 'feature_1', 'feature_2', 'target']], hue='target')
plt.title('Visualisation des caractéristiques')
plt.show()
'''))

nb.cells.append(new_code_cell('''
# Matrice de corrélation
plt.figure(figsize=(12, 10))
corr = df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Matrice de corrélation')
plt.show()
'''))

# Préparation des données
nb.cells.append(new_markdown_cell('## Préparation des données pour l\'apprentissage'))

nb.cells.append(new_code_cell('''
# Division en ensembles d'entraînement et de test
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Taille de l'ensemble d'entraînement: {X_train.shape}")
print(f"Taille de l'ensemble de test: {X_test.shape}")
'''))

# Entraînement du modèle
nb.cells.append(new_markdown_cell('## Entraînement du modèle Gradient Boosting (XGBoost)'))

nb.cells.append(new_code_cell('''
# Configuration du modèle XGBoost
model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='binary:logistic',
    random_state=42
)

# Entraînement du modèle
model.fit(X_train, y_train)
'''))

# Évaluation du modèle
nb.cells.append(new_markdown_cell('## Évaluation du modèle'))

nb.cells.append(new_code_cell('''
# Prédictions sur l'ensemble de test
y_pred = model.predict(X_test)

# Évaluation des performances
accuracy = accuracy_score(y_test, y_pred)
print(f"Précision du modèle: {accuracy:.4f}")

# Rapport de classification détaillé
print("Rapport de classification:")
print(classification_report(y_test, y_pred))

# Matrice de confusion
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Prédictions')
plt.ylabel('Valeurs réelles')
plt.title('Matrice de confusion')
plt.show()
'''))

# Importance des caractéristiques
nb.cells.append(new_markdown_cell('## Analyse de l\'importance des caractéristiques'))

nb.cells.append(new_code_cell('''
# Visualisation de l'importance des caractéristiques
plt.figure(figsize=(12, 6))
xgb.plot_importance(model, max_num_features=10)
plt.title('Importance des caractéristiques')
plt.show()
'''))

# Visualisation de l'arbre de décision
nb.cells.append(new_code_cell('''
# Visualisation d un arbre de décision du modèle
plt.figure(figsize=(20, 10))
xgb.plot_tree(model, num_trees=0)
plt.title('Visualisation d un arbre de décision du modèle')
plt.show()
'''))

# Conclusion
nb.cells.append(new_markdown_cell('## Conclusion\n\nDans ce notebook, nous avons créé un jeu de données synthétique et entraîné un modèle de classification avec XGBoost. Nous avons pu visualiser les performances du modèle et identifier les caractéristiques les plus importantes pour la prédiction.'))

# Sauvegarde dans un fichier
with open('gradient_boosting_analysis.ipynb', 'w') as f:
    nbformat.write(nb, f)

# ----- 2eme cas : exécution d'un notebook -----
from nbclient import NotebookClient
import nbformat

try:
    # Chargement du notebook
    with open('gradient_boosting_analysis.ipynb') as f:
        nb = nbformat.read(f, as_version=4)

    # Exécution
    client = NotebookClient(nb)
    client.execute()

    # Sauvegarde du résultat (avec les outputs ajoutés)
    with open('gradient_boosting_analysis_executed.ipynb', 'w') as f:
        nbformat.write(nb, f)
    
    print("Notebook créé et exécuté avec succès!")
    
except Exception as e:
    print(f"Erreur lors de l'exécution du notebook: {e}")
    print("Le notebook a été créé mais n'a pas pu être exécuté. Vérifiez que toutes les dépendances sont installées.")
    print("Vous pouvez installer les dépendances nécessaires avec: pip install xgboost scikit-learn matplotlib seaborn pandas numpy")
