# prototype.py

"""
This Automated Pipeline is designed to analyze data and machine learning.

This script allows to:
1. Load two CSV with a common ID column
2. Simulate Form answers from the User (hardcoded for now)
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
        # insights += f"Basic statistics:\n{df.describe().round(2)}\n"
        
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
def send_to_mistral(insights, decision_tree, mistral_api_key, simulate=False):
    """Send insights and decision tree to Mistral LLM.

    Args:
        insights (str): Insights from the data
        decision_tree (dict): Decision tree from the YAML file
        mistral_api_key (str): API key for Mistral
        
    Returns:
        list: Actions to perform based on the leaf node identified
    """
    try:
        import requests
        import json
        
        # Endpoint for Mistral API
        url = "https://api.mistral.ai/v1/chat/completions"
        
        # Format the decision tree as a readable string for the prompt
        decision_tree_str = json.dumps(decision_tree, indent=2)
        
        # Create the system prompt with instructions
        system_prompt = """You are an assistant specialized in data analysis.
                            Your task is to analyze the information about a dataset and determine the appropriate leaf_id
                            by following the provided decision tree. You must only respond with the leaf_id number, nothing else."""
                
        # Create the user prompt with insights and decision tree
        user_prompt = f"""Here is the information about the data to analyze:
                        {insights}
                        And here is the decision tree to follow:
                        {decision_tree_str}
                        Based on this information, what is the appropriate leaf_id? Respond only with the number."""
        
        # Prepare the headers and payload for the API request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {mistral_api_key}"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,  # Low temperature for deterministic responses
            "max_tokens": 10     # We just need a short response with the leaf_id
        }
        
        print("Sending request to Mistral API...")
        
        if not simulate:
            # Send the request to Mistral API
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses

            # Parse the response
            result = response.json()
        else : 
            result = {'id': 'c19deca4e9a940fdb562e45be3a70163', 'object': 'chat.completion', 'created': 1746017866, 'model': 'mistral-large-latest', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'tool_calls': None, 'content': '2'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 3645, 'total_tokens': 3648, 'completion_tokens': 3}}
        
        leaf_id_response = result["choices"][0]["message"]["content"].strip()

        # Extract the leaf_id (just the number)
        import re
        leaf_id_match = re.search(r'\d+', leaf_id_response)
        if leaf_id_match:
            leaf_id = int(leaf_id_match.group())
            print(f"Mistral identified leaf_id: {leaf_id}")
        else:
            print(f"Could not extract leaf_id from response: {leaf_id_response}")
            # Default to leaf_id 2 (merge datasets) if extraction fails
            leaf_id = 2
        
        # Get the actions for this leaf_id
        cell_code = get_cells_for_leaf_id(decision_tree, leaf_id)
        
        return cell_code
        
    except Exception as e:
        print(f"Error communicating with Mistral API: {str(e)}")
        raise e

def get_cells_for_leaf_id(decision_tree, leaf_id):
    """Find the actions corresponding to a specific leaf_id in the decision tree.
    
    Args:
        decision_tree (dict): The decision tree structure
        leaf_id (int): The ID of the leaf node
        
    Returns:
        dict: The leaf node with cell_title and cell_content
    """
    # Parcourir récursivement l'arbre de décision pour trouver la feuille avec l'ID spécifié
    def find_leaf(node, target_leaf_id):
        if isinstance(node, list):
            for item in node:
                result = find_leaf(item, target_leaf_id)
                if result:
                    return result
        elif isinstance(node, dict):
            if 'leaf_id' in node and node['leaf_id'] == target_leaf_id:
                return node
            
            for key, value in node.items():
                result = find_leaf(value, target_leaf_id)
                if result:
                    return result
        return None
    
    # Rechercher le nœud feuille dans l'arbre de décision
    leaf_node = find_leaf(decision_tree, leaf_id)
    
    if leaf_node:
        print(leaf_node)  # Debug - afficher le nœud trouvé
        
        # Si le nœud contient des arguments, les extraire du formulaire
        if 'arguments' in leaf_node and leaf_node['arguments']:
            # Récupérer les valeurs des arguments depuis le formulaire
            import re
            for arg in leaf_node['arguments']:
                # Chercher la valeur de l'argument dans le formulaire
                pattern = f"{arg}: \"([^\"]+)\""
                match = re.search(pattern, form_answers)
                if match:
                    # Ajouter l'argument et sa valeur au nœud feuille
                    value = match.group(1)
                    if 'arg_values' not in leaf_node:
                        leaf_node['arg_values'] = {}
                    leaf_node['arg_values'][arg] = value
        
        return leaf_node
    else:
        print(f"Leaf node with ID {leaf_id} not found in the decision tree.")
        # Retourner un nœud par défaut pour éviter les erreurs
        return {
            'leaf_id': leaf_id,
            'cell_title': 'Default Analysis',
            'arguments': [],
            'cell_content': '# Analyse par défaut\nprint("Aucun nœud correspondant trouvé dans l\'arbre de décision.")\nprint("Affichage des premières lignes des datasets:")\nprint("\\ndf1:")\nprint(df1.head())\nprint("\\ndf2:")\nprint(df2.head())'
        }

def generate_notebook_cells(df1, df2, actions):
    """Generate notebook cells based on actions.
    
    Args:
        df1 (DataFrame): First dataset
        df2 (DataFrame): Second dataset
        actions (dict): Actions to perform
        
    Returns:
        list: List of notebook cells
    """
    cells = []
    
    # Importer les cellules additionnelles depuis le fichier external_cells.py
    try:
        from external_cells import get_intro_cells, get_analysis_cells, get_conclusion_cells
        
        # Ajouter les cellules d'introduction (markdown d'intro + imports)
        cells.extend(get_intro_cells())
        
        # Créer une cellule qui définit tous les arguments nécessaires
        arg_definitions = []
        
        # Si le nœud feuille contient des valeurs d'arguments, les utiliser
        if actions and 'arg_values' in actions:
            for arg_name, arg_value in actions['arg_values'].items():
                arg_definitions.append(f"{arg_name} = '{arg_value}'")
        else:
            # Sinon, extraire common_id_column du formulaire comme méthode de secours
            import re
            common_id_match = re.search(r'common_id_column: "([^"]+)"', form_answers)
            common_id_column = common_id_match.group(1) if common_id_match else 'ID'
            arg_definitions.append(f"common_id_column = '{common_id_column}'")
        
        # Ajouter une cellule pour charger les données et définir les arguments
        load_data_cell_content = """
# Chargement des données
df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')

"""
        
        # Ajouter les définitions d'arguments à la cellule
        if arg_definitions:
            load_data_cell_content += "# Définition des arguments\n"
            load_data_cell_content += "\n".join(arg_definitions) + "\n\n"
        
        load_data_cell_content += """
print("df1 shape:", df1.shape)
print("df2 shape:", df2.shape)
"""
        
        # Ajouter des informations sur les arguments
        if 'common_id_column' in load_data_cell_content:
            load_data_cell_content += "print(f\"Colonne ID commune: {common_id_column}\")\n"
        
        cells.append(new_code_cell(load_data_cell_content))
        
        # Ajouter la cellule correspondant au leaf_id identifié
        if actions and 'cell_title' in actions and 'cell_content' in actions:
            # Ajouter le titre comme cellule markdown
            cells.append(new_markdown_cell(f"## {actions['cell_title']}"))
            
            # Ajouter le contenu comme cellule de code
            cells.append(new_code_cell(actions['cell_content']))
        
        # Ajouter des cellules d'analyse supplémentaires selon le type de données
        analysis_cells = get_analysis_cells(df1, df2)
        cells.extend(analysis_cells)
        
        # Ajouter une cellule de conclusion
        cells.extend(get_conclusion_cells())
    
    except ImportError:
        print("Attention: Le fichier external_cells.py n'a pas été trouvé. Utilisation des cellules par défaut.")
        # Code existant comme fallback
        # Ajouter une cellule d'introduction
        cells.append(new_markdown_cell("# Analyse de données automatisée\n\nCe notebook a été généré automatiquement en fonction des données fournies et des réponses au formulaire."))
        
        # Cellule d'imports
        cells.append(new_code_cell("""
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
"""))
        
        # Définir les arguments
        import re
        common_id_match = re.search(r'common_id_column: "([^"]+)"', form_answers)
        common_id_column = common_id_match.group(1) if common_id_match else 'ID'
        
        # Cellule de chargement des données
        cells.append(new_code_cell(f"""
# Chargement des données
df1 = pd.read_csv('Datasets/Tabular/Test/dataset1_with_target.csv')
df2 = pd.read_csv('Datasets/Tabular/Test/dataset2_features_only.csv')

# Définition des arguments
common_id_column = '{common_id_column}'

print("df1 shape:", df1.shape)
print("df2 shape:", df2.shape)
print(f"Colonne ID commune: {{common_id_column}}")
"""))
        
        # Ajouter la cellule correspondant au leaf_id identifié
        if actions and 'cell_title' in actions and 'cell_content' in actions:
            cells.append(new_markdown_cell(f"## {actions['cell_title']}"))
            cells.append(new_code_cell(actions['cell_content']))
        
        # Cellule de conclusion
        cells.append(new_markdown_cell("## Conclusion\n\nCe notebook a automatiquement analysé vos données et créé un modèle de base. Vous pouvez maintenant explorer davantage les données et améliorer le modèle selon vos besoins."))
    
    return cells

def create_and_execute_notebook(cells):
    """Create and execute a notebook with the given cells.
    
    Args:
        cells (list): List of notebook cells
        
    Returns:
        bool: True if the notebook was created and executed successfully
    """
    try:
        # Créer un nouveau notebook avec les cellules fournies
        notebook = new_notebook(cells=cells)
        
        # Définir le nom du fichier de sortie
        timestamp = time.strftime("%Hh-%Mm-%Ss")
        output_filename = f"generated_notebook_{timestamp}.ipynb"
        
        # Sauvegarder le notebook
        with open(output_filename, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
        
        print(f"Notebook créé et sauvegardé sous le nom : {output_filename}")
        
        # Exécuter le notebook en utilisant nbclient
        print("Exécution du notebook...")
        try:
            client = nbclient.NotebookClient(
                notebook,
                timeout=600,
                kernel_name='python3',
                resources={'path': '.'}
            )
            executed_nb = client.execute()
            
            # Sauvegarder le notebook exécuté
            executed_filename = f"executed_notebook_{timestamp}.ipynb"
            with open(executed_filename, 'w', encoding='utf-8') as f:
                nbformat.write(executed_nb, f)
            
            print(f"Notebook exécuté et résultats sauvegardés sous le nom : {executed_filename}")
            
            return True
        except Exception as exec_error:
            print(f"Erreur lors de l'exécution du notebook: {str(exec_error)}")
            print("Le notebook a été généré mais n'a pas pu être exécuté automatiquement.")
            print(f"Vous pouvez exécuter manuellement le notebook: {output_filename}")
            return False
    
    except Exception as e:
        print(f"Erreur lors de la création du notebook: {str(e)}")
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
    print('insights', insights)
    
    # Load decision tree
    print("Loading decision tree...")
    decision_tree = load_decision_tree()
    print('decision_tree', decision_tree)
    
    # Send to Mistral (simulated)
    print("Consulting Mistral LLM for notebook generation decisions...")
    actions = send_to_mistral(insights, decision_tree, mistral_api_key, simulate=True)
    print('actions', actions)

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
