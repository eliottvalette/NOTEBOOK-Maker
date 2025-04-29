"""
Templates de cellules pour le notebook généré.
Ce fichier contient des templates de code pour différentes analyses.
"""

# Template pour la préparation et l'entraînement du modèle
PREPARE_AND_TRAIN_MODEL = """
# Préparation des données
X = df.drop(columns=["YTarget", "ID"])
y = df["YTarget"]

# Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Détection automatique du type de problème
is_classification = len(np.unique(y)) < 20
print(f"Type de problème détecté: {'Classification' if is_classification else 'Régression'}")
"""

# Template pour l'entraînement du Gradient Boosting
TRAIN_GRADBOOST = """
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier

# Déterminer si c'est une tâche de classification ou régression
is_classification = len(np.unique(y)) < 20

# Choix du modèle
if is_classification:
    model = GradientBoostingClassifier()
else:
    model = GradientBoostingRegressor()

# Entraînement
model.fit(X_train_scaled, y_train)

# Prédictions
y_pred = model.predict(X_test_scaled)

# Évaluation
if is_classification:
    score = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {score:.3f}")
else:
    mse = mean_squared_error(y_test, y_pred)
    print(f"MSE: {mse:.3f}")
    print(f"RMSE: {np.sqrt(mse):.3f}")

# Importance des features
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_importance.head(10))
plt.title('Top 10 des caractéristiques les plus importantes')
plt.tight_layout()
plt.show()
"""

# Template pour l'analyse des prix
PRICE_ANALYSIS = """
# Cette analyse suppose que certaines colonnes sont liées à des prix
# Adaptation nécessaire selon les données réelles

# Identifier les colonnes potentiellement liées aux prix
price_columns = [col for col in df.columns if any(term in col.lower() 
                                                for term in ['price', 'cost', 'prix', 'value', 'feature_1'])]

if price_columns:
    print(f"Colonnes liées aux prix identifiées: {price_columns}")
    
    # Statistiques descriptives sur les colonnes de prix
    print("\nStatistiques descriptives des prix:")
    df[price_columns].describe()
    
    # Visualisation de la distribution des prix
    plt.figure(figsize=(12, 8))
    for i, col in enumerate(price_columns):
        plt.subplot(len(price_columns), 1, i+1)
        sns.histplot(df[col], kde=True)
        plt.title(f'Distribution de {col}')
    plt.tight_layout()
    plt.show()
else:
    print("Aucune colonne liée aux prix n'a été identifiée.")
"""

# Template pour les métriques de classification
CLASSIFICATION_METRICS = """
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc

# S'assurer que le modèle est bien entraîné
if 'model' not in locals():
    print("Le modèle n'a pas été entraîné précédemment.")
else:
    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Matrice de confusion')
    plt.ylabel('Valeur réelle')
    plt.xlabel('Valeur prédite')
    plt.show()
    
    # Rapport de classification
    print("Rapport de classification:")
    print(classification_report(y_test, y_pred))
    
    # Courbe ROC pour les problèmes binaires
    if len(np.unique(y)) == 2:
        try:
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            roc_auc = auc(fpr, tpr)
            
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.3f}')
            plt.plot([0, 1], [0, 1], 'k--')
            plt.xlabel('Taux de faux positifs')
            plt.ylabel('Taux de vrais positifs')
            plt.title('Courbe ROC')
            plt.legend(loc='lower right')
            plt.show()
        except:
            print("Impossible de calculer la courbe ROC.")
"""

# Template pour les métriques de régression
REGRESSION_METRICS = """
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# S'assurer que le modèle est bien entraîné
if 'model' not in locals():
    print("Le modèle n'a pas été entraîné précédemment.")
else:
    # Calcul des métriques de régression
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Erreur absolue moyenne (MAE): {mae:.3f}")
    print(f"Erreur quadratique moyenne (MSE): {mse:.3f}")
    print(f"Racine de l'erreur quadratique moyenne (RMSE): {rmse:.3f}")
    print(f"Coefficient de détermination (R²): {r2:.3f}")
    
    # Graphique des valeurs réelles vs prédites
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Valeurs réelles')
    plt.ylabel('Valeurs prédites')
    plt.title('Valeurs réelles vs prédites')
    plt.show()
    
    # Graphique des résidus
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Valeurs prédites')
    plt.ylabel('Résidus')
    plt.title('Graphique des résidus')
    plt.show()
"""

# Template pour la réduction de dimension
DIMENSION_REDUCTION = """
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Préparation des données (sans la cible et l'ID)
X = df.drop(columns=["YTarget", "ID"])

# Standardisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Appliquer PCA
pca = PCA()
pca_result = pca.fit_transform(X_scaled)

# Variance expliquée
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

# Graphique de la variance expliquée
plt.figure(figsize=(10, 6))
plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.5, label='Variance individuelle')
plt.step(range(1, len(cumulative_variance) + 1), cumulative_variance, where='mid', label='Variance cumulée')
plt.axhline(y=0.8, color='r', linestyle='--', label='Seuil 80%')
plt.xlabel('Composantes principales')
plt.ylabel('Ratio de variance expliquée')
plt.title('Variance expliquée par les composantes principales')
plt.legend()
plt.show()

# Détermination du nombre optimal de composantes
n_components = np.argmax(cumulative_variance >= 0.8) + 1
print(f"Nombre optimal de composantes pour retenir 80% de la variance: {n_components}")

# PCA avec le nombre optimal de composantes
pca_optimal = PCA(n_components=n_components)
pca_result_optimal = pca_optimal.fit_transform(X_scaled)

# Créer un dataframe avec les résultats PCA
pca_df = pd.DataFrame(
    data=pca_result_optimal,
    columns=[f'PC{i+1}' for i in range(n_components)]
)
pca_df['YTarget'] = df['YTarget']

# Visualisation des deux premières composantes
plt.figure(figsize=(10, 8))
scatter = plt.scatter(pca_df['PC1'], pca_df['PC2'], c=pca_df['YTarget'], cmap='viridis', alpha=0.5)
plt.colorbar(scatter, label='YTarget')
plt.xlabel('Première composante principale')
plt.ylabel('Deuxième composante principale')
plt.title('Projection PCA sur les deux premières composantes principales')
plt.show()
"""

# Dictionnaire des templates
CELL_TEMPLATES = {
    "prepare_and_train_model": PREPARE_AND_TRAIN_MODEL,
    "train_gradboost": TRAIN_GRADBOOST,
    "price_analysis": PRICE_ANALYSIS,
    "classification_metrics": CLASSIFICATION_METRICS,
    "regression_metrics": REGRESSION_METRICS,
    "dimension_reduction": DIMENSION_REDUCTION
} 