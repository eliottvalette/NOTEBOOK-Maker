"""
Configuration utilities for loading decision trees and form answers.
"""

import yaml
import json
from typing import Dict, Any, Tuple

def load_decision_trees() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load both decision trees from YAML files."""
    with open('src/trees/decision_tree_preprocessing.yaml', 'r') as file:
        tree_preprocessing = yaml.safe_load(file)
    with open('src/trees/decision_tree_preprocessing_nocode.yaml', 'r') as file:
        tree_preprocessing_nocode = yaml.safe_load(file)
    with open('src/trees/decision_tree_modelling.yaml', 'r') as file:
        tree_modelling = yaml.safe_load(file)
    with open('src/trees/decision_tree_modelling_nocode.yaml', 'r') as file:
        tree_modelling_nocode = yaml.safe_load(file)
    return tree_preprocessing, tree_preprocessing_nocode, tree_modelling, tree_modelling_nocode

def load_form_answers(dataset_style: str) -> Tuple[Dict[str, Any], Dict[str, Any], str, str]:
    """Load form answers for a specific dataset style."""
    with open('src/examples/answers_examples.json', 'r') as file:
        form_answers_examples = json.load(file)
        form_answers_preprocessing = form_answers_examples[dataset_style][0]
        form_answers_modelling = form_answers_examples[dataset_style][1]
        leaf_id_preprocessing = form_answers_examples[dataset_style][2]['leaf_id_preprocessing']
        leaf_id_modelling = form_answers_examples[dataset_style][2]['leaf_id_modelling']
    return form_answers_preprocessing, form_answers_modelling, leaf_id_preprocessing, leaf_id_modelling 