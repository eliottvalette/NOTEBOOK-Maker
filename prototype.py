# prototype.py

"""
This Automated Pipeline is designed to analyze data and machine learning.

This script allows to:
1. Load two CSV with a common ID column
2. Simulate Form answers from the User
3. Send these elements to an LLM for decision-making
4. Dynamically generate a notebook with nbformat
5. Execute the notebook and return the results
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
from sample_cell_templates import CELL_TEMPLATES

# Load datasets as if the User has submitted them
def load_datasets():
    """Load two datasets from CSV files."""
    df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
    df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')
    print("Datasets loaded successfully.")
    
    return df1, df2


# Simulate the User's answers to the questions
form_answers = {
    "has_several_csvs": True,
    "number_of_csvs": 2,
    "csv_names": ["dataset1_with_target.csv", "dataset2_features_only.csv"],
    "has_common_id": True,
    "common_id_column": "ID",
    "target_column": "YTarget",
    "wants_binary_prediction": True,
    "wants_gradboost": True,
    "wants_classification_metrics": True,
    "wants_regression_metrics": True,
}

# Generate the code cells based on the answers
def generate_notebook_cells(df1, df2, responses):
    """Generate the code cells for the notebook based on the answers."""
    cells = []
    
    # Standard imports
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
    
    # Load data cell
    load_data_cell = new_code_cell(
        """
# Load the datasets
df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')

# Merge the datasets on the ID
df = pd.merge(df1, df2, on='ID', how='inner')

# Display the first lines
print("Dimensions du dataset fusionné:", df.shape)
df.head()
"""
    )
    cells.append(load_data_cell)
    
    # EDA cell
    eda_cell = new_code_cell(
        """
# Descriptive statistics
print("Statistiques descriptives:")
df.describe()
"""
    )
    cells.append(eda_cell)
    
    # Conditional cells based on the answers and the decision tree
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
    
    # Add a conclusion cell
    cells.append(new_markdown_cell("## Conclusion"))
    cells.append(new_code_cell(
        """
# Summary of the operations performed
print("Summary of the performed analyses:")

# Display the LLM's responses
responses = {}
"""
        + "\n".join([f"responses['{key}'] = {value}" for key, value in responses.items()]) +
        """

for key, value in responses.items():
    print(f"- {key}: {'Oui' if value else 'Non'}")

# Save the model if trained
if 'model' in locals():
    import joblib
    joblib.dump(model, 'trained_model.joblib')
    print("The model has been saved in 'trained_model.joblib'")
"""
    ))
    
    return cells

# Création et exécution du notebook
def create_and_execute_notebook(cells):
    """Create a notebook with the provided cells and execute it."""
    # Create the notebook
    nb = new_notebook()
    nb.cells = cells
    
    # Save the notebook
    notebook_path = 'generated_notebook.ipynb'
    with open(notebook_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"Notebook created: {notebook_path}")
    
    # Execute the notebook
    try:
        client = nbclient.NotebookClient(nb, timeout=600)
        executed_nb = client.execute()
        
        # Save the executed notebook
        executed_path = 'executed_notebook.ipynb'
        with open(executed_path, 'w') as f:
            nbformat.write(executed_nb, f)
        
        print(f"Notebook executed and saved: {executed_path}")
        return True
    except Exception as e:
        print(f"Error during the notebook execution: {e}")
        return False

def main():
    """Main function that orchestrates the entire pipeline."""
    print("Starting the automated pipeline...")
    
    # Load or create the datasets
    df1, df2 = load_datasets()
    
    # Generate the questions based on the data
    questions = generate_questions(df1, df2)
    
    # Simulate the sending to the LLM and the retrieval of the responses
    responses = get_llm_responses(questions)
    
    # Generate the notebook cells
    cells = generate_notebook_cells(df1, df2, responses)
    
    # Create and execute the notebook
    success = create_and_execute_notebook(cells)
    
    if success:
        print("Pipeline terminé avec succès!")
    else:
        print("The pipeline has ended with errors.")

if __name__ == "__main__":
    main()