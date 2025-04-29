"""
Templates de cellules pour le notebook généré.
Ce fichier contient des templates de code pour différentes analyses.
"""

# Template pour la fusion des datasets
MERGE_DATASETS = """
# Fusion des datasets sur la colonne ID commune
print("Fusion des datasets sur la colonne ID commune")
df = pd.merge(df1, df2, on='ID', how='inner')
print(f"Dimensions du dataset fusionné: {df.shape}")
print(f"Nombre de lignes après fusion: {df.shape[0]}")
print(f"Nombre de colonnes après fusion: {df.shape[1]}")
print("Aperçu du dataset fusionné:")
df.head()
"""

# Template pour la préparation et l'entraînement du modèle
PREPARE_AND_TRAIN_MODEL = """
# Préparation des données pour les prédictions binaires
print("Préparation des données pour les prédictions binaires")
X = df.drop(columns=["YTarget", "ID"])
y = df["YTarget"]

# Vérification que la cible est bien binaire
if len(np.unique(y)) != 2:
    print(f"ATTENTION: La variable cible n'est pas binaire. Valeurs uniques: {np.unique(y)}")
    print("Conversion de la cible en variable binaire (0/1)...")
    # Conversion simple pour la démonstration (à adapter selon les besoins réels)
    y = (y > y.median()).astype(int)
    print(f"Après conversion, valeurs uniques: {np.unique(y)}")

# Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Dimensions des données d'entraînement: {X_train.shape}")
print(f"Dimensions des données de test: {X_test.shape}")
"""

# Template pour l'entraînement du Gradient Boosting
TRAIN_GRADBOOST = """
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier

print("Entraînement d'un modèle Gradient Boosting...")

# Déterminer si c'est une tâche de classification binaire
is_binary_classification = len(np.unique(y)) == 2
if not is_binary_classification:
    print("ATTENTION: La tâche n'est pas une classification binaire.")
    print(f"Valeurs uniques dans la cible: {np.unique(y)}")

# Choix du modèle - pour ce cas, nous utilisons forcément un classifieur binaire
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
print("Paramètres du modèle:")
print(model.get_params())

# Entraînement
print("Entraînement du modèle...")
model.fit(X_train_scaled, y_train)
print("Modèle entraîné avec succès!")

# Prédictions
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

# Évaluation basique
score = accuracy_score(y_test, y_pred)
print(f"Accuracy: {score:.3f}")
"""

# Template pour les métriques de classification
CLASSIFICATION_METRICS = """
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve, average_precision_score

print("Calcul des métriques de classification détaillées...")

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
    
    # Courbe ROC
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.3f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('Taux de faux positifs')
    plt.ylabel('Taux de vrais positifs')
    plt.title('Courbe ROC')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()
    
    # Courbe Precision-Recall
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    ap_score = average_precision_score(y_test, y_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label=f'AP = {ap_score:.3f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Courbe Precision-Recall')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()
"""

# Template pour les métriques de régression
REGRESSION_METRICS = """
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

print("Analyse des métriques de régression...")

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
    plt.grid(True)
    plt.show()
    
    # Graphique des résidus
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Valeurs prédites')
    plt.ylabel('Résidus')
    plt.title('Graphique des résidus')
    plt.grid(True)
    plt.show()
    
    # Distribution des résidus
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True)
    plt.xlabel('Résidus')
    plt.title('Distribution des résidus')
    plt.grid(True)
    plt.show()
"""

# Template pour l'analyse des features importantes
FEATURE_IMPORTANCE = """
print("Analyse de l'importance des features...")

# S'assurer que le modèle est bien entraîné
if 'model' not in locals():
    print("Le modèle n'a pas été entraîné précédemment.")
elif not hasattr(model, 'feature_importances_'):
    print("Le modèle n'a pas d'attribut feature_importances_.")
else:
    # Importance des features
    feature_importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("Top 10 des features les plus importantes:")
    print(feature_importance.head(10))
    
    # Visualisation
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=feature_importance.head(15))
    plt.title('Top 15 des caractéristiques les plus importantes')
    plt.tight_layout()
    plt.show()
    
    # Visualisation de la distribution des features les plus importantes
    top_features = feature_importance.head(3)['Feature'].values
    plt.figure(figsize=(15, 5))
    for i, feature in enumerate(top_features):
        plt.subplot(1, 3, i+1)
        sns.histplot(df[feature], kde=True)
        plt.title(f'Distribution de {feature}')
    plt.tight_layout()
    plt.show()
    
    # Analyse de corrélation entre les features les plus importantes
    if len(top_features) > 1:
        plt.figure(figsize=(10, 8))
        correlation_matrix = df[top_features].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Corrélation entre les features les plus importantes')
        plt.tight_layout()
        plt.show()
"""

# Template pour comparer les datasets
COMPARE_DATASETS = """
print("Comparaison des datasets...")

# Statistiques descriptives
print("Comparaison des statistiques descriptives:")
stats_df1 = df1.describe().T
stats_df2 = df2.describe().T

if 'ID' in df1.columns and 'ID' in df2.columns:
    # Vérifier si les IDs sont les mêmes
    print(f"Nombre d'IDs dans dataset1: {df1['ID'].nunique()}")
    print(f"Nombre d'IDs dans dataset2: {df2['ID'].nunique()}")
    common_ids = set(df1['ID']).intersection(set(df2['ID']))
    print(f"Nombre d'IDs communs: {len(common_ids)}")
    
    # Visualisation des distributions de variables clés
    plt.figure(figsize=(15, 10))
    cols_to_plot = min(3, len(df1.columns) - 1)  # exclure l'ID
    for i, col in enumerate([c for c in df1.columns if c != 'ID'][:cols_to_plot]):
        if col in df2.columns:
            plt.subplot(cols_to_plot, 1, i+1)
            sns.kdeplot(df1[col], label='Dataset 1')
            sns.kdeplot(df2[col], label='Dataset 2')
            plt.title(f'Distribution de {col}')
            plt.legend()
    plt.tight_layout()
    plt.show()
    
    # Matrice de corrélation pour chaque dataset
    plt.figure(figsize=(18, 8))
    
    # Dataset 1
    plt.subplot(1, 2, 1)
    corr_matrix1 = df1.select_dtypes(include=['number']).corr()
    sns.heatmap(corr_matrix1, annot=False, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Matrice de corrélation - Dataset 1')
    
    # Dataset 2
    plt.subplot(1, 2, 2)
    corr_matrix2 = df2.select_dtypes(include=['number']).corr()
    sns.heatmap(corr_matrix2, annot=False, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Matrice de corrélation - Dataset 2')
    
    plt.tight_layout()
    plt.show()
"""

# Template pour l'analyse des prix (gardé pour référence)
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

# Template pour la réduction de dimension (gardé pour référence)
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
    "merge_datasets": MERGE_DATASETS,
    "prepare_and_train_model": PREPARE_AND_TRAIN_MODEL,
    "train_gradboost": TRAIN_GRADBOOST,
    "price_analysis": PRICE_ANALYSIS,
    "classification_metrics": CLASSIFICATION_METRICS,
    "regression_metrics": REGRESSION_METRICS,
    "dimension_reduction": DIMENSION_REDUCTION,
    "feature_importance": FEATURE_IMPORTANCE,
    "compare_datasets": COMPARE_DATASETS
} 