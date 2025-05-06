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
import json
import requests

load_dotenv()   
mistral_api_key = os.getenv('MISTRAL_API_KEY')

# Load datasets as if the User has submitted them
def load_datasets():
    """Load two datasets from CSV files."""
    df1 = pd.read_csv('Datasets/Tabular/Binary_pred/dataset1_with_target.csv')
    df2 = pd.read_csv('Datasets/Tabular/Binary_pred/dataset2_features_only.csv')
    print("Datasets loaded successfully.")
    
    return [df1, df2]

def load_form_answers():
    # Simulate the User's answers to the questions
    with open('answers_examples.json', 'r') as file:
        form_answers_examples = json.load(file)
        form_answers_preprocessing = form_answers_examples[DATASET_STYLE][0]
        form_answers_modelling = form_answers_examples[DATASET_STYLE][1]
        leaf_id_preprocessing = form_answers_examples[DATASET_STYLE][2]['leaf_id_preprocessing']
        leaf_id_modelling = form_answers_examples[DATASET_STYLE][2]['leaf_id_modelling']
    return form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling
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
    form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling = load_form_answers()
    insights = ""
    insights += get_insights(df1, 1)
    insights += "\n"
    insights += get_insights(df2, 2)
    insights += "\n"
    insights += "User's form answers:\n"
    insights += str(form_answers_preprocessing)
    return insights

# Load the decision tree from YAML
def load_decision_tree():
    """Load the decision tree from YAML file."""
    with open('decision_tree_preprocessing.yaml', 'r') as file:
        tree_preprocessing = yaml.safe_load(file)
    with open('decision_tree_modelling.yaml', 'r') as file:
        tree_modelling = yaml.safe_load(file)
    return tree_preprocessing, tree_modelling

# Sending insights and decision tree to Mistral LLM
def send_to_mistral(insights, decision_tree, mistral_api_key, simulate=False, form_type="preprocessing"):
    """Send insights and decision tree to Mistral LLM.

    Args:
        insights (str): Insights from the data
        decision_tree (dict): Decision tree from the YAML file
        mistral_api_key (str): API key for Mistral
        simulate (bool): Whether to simulate the API call
        form_type (str): Type of form to use ("preprocessing" or "modelling")
        
    Returns:
        list: Actions to perform based on the leaf node identified
    """
    form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling = load_form_answers()
    
    try:
        
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
            leaf_id_response = result["choices"][0]["message"]["content"].strip()
        else : 
            # Simuler une réponse en fonction du type de formulaire
            if form_type == "preprocessing":
                leaf_id_response = leaf_id_preprocessing
            else:
                leaf_id_response = leaf_id_modelling
        
        # Extract the leaf_id (just the number)
        import re
        leaf_id_match = re.search(r'\d+', leaf_id_response)
        if leaf_id_match:
            leaf_id = int(leaf_id_match.group())
            print(f"Mistral identified leaf_id: {leaf_id}")
        else:
            print(f"Could not extract leaf_id from response: {leaf_id_response}")
            raise ValueError(f"Could not extract leaf_id from response: {leaf_id_response}")
        
        # Get the actions for this leaf_id
        cell_code = get_cells_for_leaf_id(decision_tree, leaf_id, form_type)
        
        return cell_code
        
    except Exception as e:
        print(f"Error communicating with Mistral API: {str(e)}")
        raise e

def get_cells_for_leaf_id(decision_tree, leaf_id, form_type="preprocessing"):
    """Find the actions corresponding to a specific leaf_id in the decision tree.
    
    Args:
        decision_tree (dict): The decision tree structure
        leaf_id (int): The ID of the leaf node
        form_type (str): Type of form to use for arguments ("preprocessing" or "modelling")
        
    Returns:
        dict: The leaf node with cell_title and cell_content
    """
    form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling = load_form_answers()
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
        # Sélectionner le formulaire approprié en fonction du type
        form_answers = form_answers_preprocessing if form_type == "preprocessing" else form_answers_modelling
        
        # Si le nœud contient des arguments, les extraire du formulaire
        if 'arguments' in leaf_node and leaf_node['arguments']:
            # Récupérer les valeurs des arguments depuis le formulaire
            for arg in leaf_node['arguments']:
                # Extraire les valeurs des arguments du formulaire
                try:
                    # Accéder directement à la valeur dans le dictionnaire form_answers
                    if arg in form_answers:
                        value = form_answers[arg]
                        
                        # Stocker la valeur de l'argument
                        if 'arg_values' not in leaf_node:
                            leaf_node['arg_values'] = {}
                        leaf_node['arg_values'][arg] = value
                    else:
                        print(f"Avertissement: L'argument '{arg}' n'a pas été trouvé dans les réponses du formulaire.")
                except Exception as e:
                    print(f"Erreur lors de l'extraction de l'argument {arg}: {str(e)}")
        
        return leaf_node
    else:
        print(f"Leaf node with ID {leaf_id} not found in the decision tree.")
        raise ValueError(f"Leaf node with ID {leaf_id} not found in the decision tree.")

def format_notebook_cells(leaf):
    """Format leaf information into notebook cells.
    
    Args:
        leaf (dict): Leaf node from the decision tree
    
    Returns:
        list: List of nbformat cells ready to be added to a notebook
    """
    cells = []
    
    # Ajouter un titre au notebook
    title = leaf.get('cell_title', 'Analyse automatique')
    cells.append(new_markdown_cell(f"# {title}"))
    
    # Ajouter l'importation des bibliothèques standard
    imports_cell = new_code_cell(
        "# Importation des bibliothèques nécessaires\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "# Configuration pour afficher les graphiques dans le notebook\n"
        "%matplotlib inline\n"
        "plt.style.use('ggplot')\n"
        "sns.set(style='whitegrid')"
    )
    cells.append(imports_cell)

    # Traiter chaque élément de contenu de cellule dans le nœud feuille
    cell_content = leaf.get('cell_content', [])
    
    if not isinstance(cell_content, list):
        # Si cell_content n'est pas une liste, le convertir en élément unique d'une liste
        cell_content = [{'type': 'code', 'content': cell_content}]
    
    for cell in cell_content:
        cell_type = cell.get('type', 'code')  # Par défaut, considérer comme une cellule de code
        content = cell.get('content', '')
        
        # Remplacer les arguments dans le contenu avec leurs valeurs
        if 'arg_values' in leaf:
            for arg_name, arg_value in leaf['arg_values'].items():
                # Format de substitution pour les différents types de valeurs
                if isinstance(arg_value, list):
                    # Pour les listes, utiliser la représentation Python
                    arg_value_str = repr(arg_value)
                elif isinstance(arg_value, bool):
                    # Pour les booléens, utiliser True/False
                    arg_value_str = str(arg_value)
                elif isinstance(arg_value, (int, float)):
                    # Pour les nombres, utiliser leur représentation directe
                    arg_value_str = str(arg_value)
                else:
                    # Pour les chaînes, ajouter des guillemets sans échapper
                    arg_value_str = str(arg_value)
                
                # Remplacer toutes les occurrences de l'argument dans le contenu en utilisant les délimiteurs $
                content = content.replace(f"${arg_name}$", arg_value_str)
        
        # Créer la cellule appropriée selon le type
        if cell_type.lower() == 'markdown':
            cells.append(new_markdown_cell(content))
        else:  # 'code' par défaut
            cells.append(new_code_cell(content))
    
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
        output_dir = "Output"
        
        # Vérifier si le répertoire Output existe, sinon le créer
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Répertoire '{output_dir}' créé")
            
        output_filename = f"{output_dir}/gen_{DATASET_STYLE}.ipynb"
        
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
            executed_filename = f"{output_dir}/exe_{DATASET_STYLE}.ipynb"
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
    
# Get insights for modelling
def get_insights_for_modelling(insights):
    """
    Prépare les insights pour l'étape de modélisation.
    Ajoute les réponses du formulaire de modélisation aux insights d'origine.
    
    Args:
        insights (str): Insights d'origine avec les réponses du formulaire de prétraitement
        
    Returns:
        str: Insights enrichis avec les réponses du formulaire de modélisation
    """

    form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling = load_form_answers()
    # Garder les insights de base mais ajouter les réponses du formulaire de modélisation
    insights_modelling = insights + "\n\nUser's form answers for modelling:\n"
    insights_modelling += str(form_answers_modelling)
    
    return insights_modelling

# Format cells for modelling
def modelling_cells(leaf_modelling):
    """
    Formate les cellules pour l'étape de modélisation.
    Cette fonction est séparée de la fonction format_notebook_cells
    car elle doit ajouter les cellules de modélisation après les cellules de prétraitement.
    
    Args:
        leaf_modelling (dict): Le nœud feuille pour la phase de modélisation
        
    Returns:
        list: Liste des cellules de notebook pour la modélisation
    """
    cells = []
    
    # Ajouter un titre pour la section de modélisation
    title = leaf_modelling.get('cell_title', 'Modélisation')
    cells.append(new_markdown_cell(f"# {title}"))
    
    # Ajouter des cellules pour le contenu de modélisation
    cell_content = leaf_modelling.get('cell_content', [])
    
    if not isinstance(cell_content, list):
        # Si cell_content n'est pas une liste, le convertir en élément unique d'une liste
        cell_content = [{'type': 'code', 'content': cell_content}]
    
    for cell in cell_content:
        cell_type = cell.get('type', 'code')  # Par défaut, considérer comme une cellule de code
        content = cell.get('content', '')
        
        # Remplacer les arguments dans le contenu avec leurs valeurs
        if 'arg_values' in leaf_modelling:
            for arg_name, arg_value in leaf_modelling['arg_values'].items():
                # Format de substitution pour les différents types de valeurs
                if isinstance(arg_value, list):
                    # Pour les listes, utiliser la représentation Python
                    arg_value_str = repr(arg_value)
                elif isinstance(arg_value, bool):
                    # Pour les booléens, utiliser True/False
                    arg_value_str = str(arg_value)
                elif isinstance(arg_value, (int, float)):
                    # Pour les nombres, utiliser leur représentation directe
                    arg_value_str = str(arg_value)
                else:
                    # Pour les chaînes, ajouter des guillemets sans échapper
                    arg_value_str = str(arg_value)
                
                # Remplacer toutes les occurrences de l'argument dans le contenu en utilisant les délimiteurs $
                content = content.replace(f"${arg_name}$", arg_value_str)
        
        # Créer la cellule appropriée selon le type
        if cell_type.lower() == 'markdown':
            cells.append(new_markdown_cell(content))
        else:  # 'code' par défaut
            cells.append(new_code_cell(content))
    
    return cells

def main():
    """Main function orchestrating the pipeline."""
    print("Starting automated pipeline...")
    
    # Load datasets (For test purposes, in the real pipeine, the user will submit the datasets and the form answers but it can have different format and number)
    print("Loading datasets...")
    dfs = load_datasets()
    df1, df2 = dfs[0], dfs[1]    

    # Get insights and form answers
    print("Extracting insights from data...")
    insights = get_insights_and_answers(df1, df2)
    
    # Load decision tree
    print("Loading decision tree...")
    tree_preprocessing, tree_modelling = load_decision_tree()
    
    # Send to Mistral for preprocessing decisions
    print("Consulting Mistral LLM for preprocessing decisions...")
    leaf = send_to_mistral(insights, tree_preprocessing, mistral_api_key, simulate=True, form_type="preprocessing")

    # Formatting notebook cells for preprocessing
    print("Formatting notebook cells based on Mistral's preprocessing decisions...")
    preprocessing_cells = format_notebook_cells(leaf)
 
    # Get New insights for Modelling
    print("Getting new insights for Modelling...")
    insights_modelling = get_insights_for_modelling(insights)

    # New call to Mistral for Modelling
    print("Consulting Mistral LLM for Modelling decisions...")
    leaf_modelling = send_to_mistral(insights_modelling, tree_modelling, mistral_api_key, simulate=True, form_type="modelling")

    # Add cells for Modelling
    print("Creating cells for Modelling...")
    model_cells = modelling_cells(leaf_modelling)
    
    # Combine all cells
    print("Combining preprocessing and modelling cells...")
    all_cells = preprocessing_cells + model_cells
    
    # Create and execute notebook
    print("Creating and executing notebook...")
    success = create_and_execute_notebook(all_cells)
    
    if success:
        print("Pipeline completed successfully!")
    else:
        print("Pipeline completed with errors.")


if __name__ == "__main__":
    for dataset_style in ['A_1_one_csv', 'B_2_joinable_csvs', 'C_1_csv_time_series']:
        DATASET_STYLE = dataset_style
        main()
