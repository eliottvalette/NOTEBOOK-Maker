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
from dotenv import load_dotenv
from sample_cell_templates import CELL_TEMPLATES

load_dotenv()   
mistral_api_key = os.getenv('MISTRAL_API_KEY')

# Load datasets as if the User has submitted them
def load_datasets():
    """Load two datasets from CSV files."""
    df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
    df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')
    print("Datasets loaded successfully.")
    
    return [df1, df2]

# Simulate the User's answers to the questions
form_answers = """
has_several_csvs: True,
number_of_csvs: 2,
csv_names: ["dataset1_with_target.csv", "dataset2_features_only.csv"],
has_common_id: True,
common_id_column: "ID",
target_column: "YTarget",
wants_binary_prediction: True,
wants_gradboost: True,
wants_classification_metrics: True,
wants_regression_metrics: True,
"""

# Get insights from the data
def get_insights(df, idx):
    """Get insights from the data."""
    insights = f"Insights from dataset {idx}:\n"
    
    try:
        # Shape
        insights += f"Shape: {df.shape}\n"
        
        # Info about columns and data types
        insights += f"Columns: {list(df.columns)}\n"
        insights += f"Data types:\n{df.dtypes.to_string()}\n"
        
        # Missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            insights += f"Missing values:\n{missing_values[missing_values > 0].to_string()}\n"
        else:
            insights += "No missing values found.\n"
        
        # Basic statistics
        insights += f"Basic statistics:\n{df.describe().round(2)}\n"
        
        # Sample data
        insights += f"Sample data (first 3 rows):\n{df.head(3).to_string()}\n"
        
        # For target column if it exists
        if 'YTarget' in df.columns:
            insights += f"Target distribution:\n"
            insights += f"Unique values: {df['YTarget'].nunique()}\n"
            insights += f"Value counts:\n{df['YTarget'].value_counts().to_string()}\n"
        
        return insights
    except Exception as e:
        return f"Error getting insights from dataset {idx}: {str(e)}\n"


# Gather the insights from the datasets and form answers as a single string
def get_insights_and_answers(df1, df2):
    """Gather the insights from the datasets and form answers as a single string."""
    insights = ""
    insights += get_insights(df1, 1)
    insights += "\n"
    insights += get_insights(df2, 2)
    insights += "\n"
    insights += "User's form answers:\n"
    insights += form_answers
    return insights

# Load the decision tree from YAML
def load_decision_tree():
    """Load the decision tree from YAML file."""
    with open('decision_tree.yaml', 'r') as file:
        tree = yaml.safe_load(file)
    return tree

# Sending insights and decision tree to Mistral LLM
def send_to_mistral(insights, decision_tree, mistral_api_key):
    """Send insights and decision tree to Mistral LLM.

    Args:
        insights (str): Insights from the data
        decision_tree (dict): Decision tree from the YAML file
        
    Returns:
        int: ID of the Leaf Node in the Decision Tree
    """

    















# Generate notebook cells based on the actions from Mistral
def generate_notebook_cells(df1, df2, actions):
    """Generate notebook cells based on the actions determined by Mistral."""
    cells = []
    
    # Add imports cell
    imports_cell = new_code_cell(
        """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# Set plot style
plt.style.use('ggplot')
sns.set(style="whitegrid")
"""
    )
    cells.append(imports_cell)
    
    # Add data loading cell
    load_data_cell = new_code_cell(
        """
# Load datasets
print("Loading datasets...")
df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')

print(f"Dataset 1 shape: {df1.shape}")
print(f"Dataset 2 shape: {df2.shape}")

# Display sample data
print("\\nSample data from Dataset 1:")
df1.head(3)
"""
    )
    cells.append(load_data_cell)
    
    # Add dataset info cell
    info_cell = new_code_cell(
        """
# Basic dataset information
print("\\nBasic information about Dataset 1:")
df1.info()

print("\\nBasic information about Dataset 2:")
df2.info()

# Check for missing values
print("\\nMissing values in Dataset 1:")
print(df1.isnull().sum())

print("\\nMissing values in Dataset 2:")
print(df2.isnull().sum())
"""
    )
    cells.append(info_cell)
    
    # Add cells based on actions
    for action in actions:
        if 'generate_cell' in action:
            cell_type = action['generate_cell']
            if cell_type in CELL_TEMPLATES:
                # Add a markdown title first
                title = cell_type.replace('_', ' ').title()
                cells.append(new_markdown_cell(f"## {title}"))
                
                # Add the code cell
                cells.append(new_code_cell(CELL_TEMPLATES[cell_type]))
    
    # Add a conclusion cell
    cells.append(new_markdown_cell("## Conclusion"))
    cells.append(new_code_cell(
        """
print("Analysis completed successfully!")
print("Summary of actions performed:")
"""
        + "\n".join([f"print(\"- {action['generate_cell'] if 'generate_cell' in action else action}\")" for action in actions])
    ))
    
    return cells

# Create and execute the notebook
def create_and_execute_notebook(cells):
    """Create and execute a notebook with the provided cells."""
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
        print(f"Error executing notebook: {e}")
        return False

def main():
    """Main function orchestrating the pipeline."""
    print("Starting automated pipeline...")
    
    # Load datasets
    print("Loading datasets...")
    dfs = load_datasets()
    df1, df2 = dfs[0], dfs[1]
    
    # Get insights and form answers
    print("Extracting insights from data...")
    insights = get_insights_and_answers(df1, df2)
    
    # Load decision tree
    print("Loading decision tree...")
    decision_tree = load_decision_tree()
    
    # Send to Mistral (simulated)
    print("Consulting Mistral LLM for notebook generation decisions...")
    actions = send_to_mistral(insights, decision_tree)
    
    # Generate notebook cells
    print("Generating notebook cells based on Mistral's decisions...")
    cells = generate_notebook_cells(df1, df2, actions)
    
    # Create and execute notebook
    print("Creating and executing notebook...")
    success = create_and_execute_notebook(cells)
    
    if success:
        print("Pipeline completed successfully!")
    else:
        print("Pipeline completed with errors.")

if __name__ == "__main__":
    main()
