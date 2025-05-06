"""
Utilities for interacting with the Mistral API.
"""

import json
import requests
import re
from typing import Dict, Any, List
from .config import load_form_answers

def send_to_mistral(insights: str, decision_tree: Dict[str, Any], 
                   mistral_api_key: str, simulate: bool = False, 
                   form_type: str = "preprocessing") -> Dict[str, Any]:
    """Send insights and decision tree to Mistral LLM for analysis."""
    try:
        # Format the decision tree as a readable string
        decision_tree_str = json.dumps(decision_tree, indent=2)
        
        # Create the system prompt
        system_prompt = """You are an assistant specialized in data analysis.
                        Your task is to analyze the information about a dataset and determine the appropriate leaf_id
                        by following the provided decision tree. You must only respond with the leaf_id number, nothing else."""
        
        # Create the user prompt
        user_prompt = f"""Here is the information about the data to analyze:
                        {insights}
                        And here is the decision tree to follow:
                        {decision_tree_str}
                        Based on this information, what is the appropriate leaf_id? Respond only with the number."""
        
        if not simulate:
            # Prepare API request
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
                "temperature": 0.0,
                "max_tokens": 10
            }
            
            # Send request to Mistral API
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            leaf_id_response = result["choices"][0]["message"]["content"].strip()
        else:
            # Simulate response based on form type
            _, _, leaf_id_preprocessing, leaf_id_modelling = load_form_answers('A_1_one_csv')
            leaf_id_response = leaf_id_preprocessing if form_type == "preprocessing" else leaf_id_modelling
        
        # Extract leaf_id
        leaf_id_match = re.search(r'\d+', leaf_id_response)
        if leaf_id_match:
            leaf_id = int(leaf_id_match.group())
            print(f"Mistral identified leaf_id: {leaf_id}")
        else:
            raise ValueError(f"Could not extract leaf_id from response: {leaf_id_response}")
        
        # Get the actions for this leaf_id
        return get_cells_for_leaf_id(decision_tree, leaf_id, form_type)
        
    except Exception as e:
        print(f"Error communicating with Mistral API: {str(e)}")
        raise e

def get_cells_for_leaf_id(decision_tree: Dict[str, Any], leaf_id: int, 
                         form_type: str = "preprocessing") -> Dict[str, Any]:
    """Find the actions corresponding to a specific leaf_id in the decision tree."""
    def find_leaf(node: Dict[str, Any], target_leaf_id: int) -> Dict[str, Any]:
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
    
    # Find the leaf node
    leaf_node = find_leaf(decision_tree, leaf_id)
    
    if leaf_node:
        # Get form answers
        form_answers_preprocessing, form_answers_modelling, _, _ = load_form_answers('A_1_one_csv')
        form_answers = form_answers_preprocessing if form_type == "preprocessing" else form_answers_modelling
        
        # Process arguments if present
        if 'arguments' in leaf_node and leaf_node['arguments']:
            for arg in leaf_node['arguments']:
                try:
                    if arg in form_answers:
                        value = form_answers[arg]
                        if 'arg_values' not in leaf_node:
                            leaf_node['arg_values'] = {}
                        leaf_node['arg_values'][arg] = value
                    else:
                        print(f"Warning: Argument '{arg}' not found in form answers.")
                except Exception as e:
                    print(f"Error extracting argument {arg}: {str(e)}")
        
        return leaf_node
    else:
        raise ValueError(f"Leaf node with ID {leaf_id} not found in the decision tree.") 