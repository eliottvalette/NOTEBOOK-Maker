"""
Main pipeline module that orchestrates the entire notebook generation process.
"""

import os
from typing import List, Tuple, Dict, Any
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from nb_maker_src.utils.config import load_decision_trees, load_form_answers
from nb_maker_src.utils.insights import get_insights_and_answers, get_insights_for_modelling
from nb_maker_src.utils.mistral_calls import send_to_mistral
from nb_maker_src.utils.notebook import format_notebook_cells, modelling_cells, create_and_execute_notebook

class NotebookPipeline:
    def __init__(self, dataset_style: str, dfs_paths: List[str]):
        """Initialize the pipeline with a specific dataset style and optional dataset path."""
        self.dataset_style = dataset_style
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")
        
        # Define base paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.datasets_dir = self.base_dir / 'Datasets'
        self.output_dir = self.base_dir / 'Output'
        self.dfs_paths = dfs_paths

    def run(self, ans_preprocessing, ans_modelling) -> bool:
        """Run the complete pipeline."""
        try:
            print("Starting automated pipeline...")

            # Get insights and form answers
            print("Extracting insights from data...")
            insights = get_insights_and_answers(*self.dfs_paths, 
                                                ans_preprocessing = ans_preprocessing)
            
            # Load decision trees
            print("Loading decision trees...")
            tree_preprocessing, tree_preprocessing_nocode, tree_modelling, tree_modelling_nocode = load_decision_trees()
            
            # Preprocessing phase
            print("Consulting Mistral LLM for preprocessing decisions...")
            leaf = send_to_mistral(insights = insights, 
                                   decision_tree = tree_preprocessing, 
                                   nocode_decision_tree = tree_preprocessing_nocode,
                                   mistral_api_key = self.mistral_api_key, 
                                   simulate = True, 
                                   form_type = "preprocessing",
                                   dataset_style = self.dataset_style)
            
            # Format preprocessing cells
            print("Formatting notebook cells based on Mistral's preprocessing decisions...")
            preprocessing_cells = format_notebook_cells(leaf)
            
            # Modelling phase
            print("Getting new insights for Modelling...")
            insights_modelling = get_insights_for_modelling(insights, ans_modelling)
            
            print("Consulting Mistral LLM for Modelling decisions...")
            leaf_modelling = send_to_mistral(insights=insights_modelling, 
                                             decision_tree=tree_modelling, 
                                             nocode_decision_tree=tree_modelling_nocode, 
                                             mistral_api_key=self.mistral_api_key, 
                                             simulate=True, 
                                             form_type="modelling",
                                             dataset_style=self.dataset_style)
            
            # Create modelling cells
            print("Creating cells for Modelling...")
            model_cells = modelling_cells(leaf_modelling)
            
            # Combine all cells
            print("Combining preprocessing and modelling cells...")
            all_cells = preprocessing_cells + model_cells
            
            # Create and execute notebook
            print("Creating and executing notebook...")
            
            # Ensure output directory exists
            self.output_dir.mkdir(exist_ok=True)
            
            # Create output filenames
            gen_filename = f"gen_{self.dataset_style}.ipynb"
            exe_filename = f"exe_{self.dataset_style}.ipynb"
            
            success = create_and_execute_notebook(
                cells=all_cells,
                output_dir=str(self.output_dir),
                gen_filename=gen_filename,
                exe_filename=exe_filename,
                execute=True
            )
            
            if success:
                print("Pipeline completed successfully!")
            else:
                print("Pipeline completed with errors.")
                
            return success
            
        except Exception as e:
            print(f"Error in pipeline execution: {str(e)}")
            raise e

def main(dataset_style, dfs_paths, ans_preprocessing, ans_modelling, manual = False):
    """Main entry point for the pipeline."""
    # Run pipeline for each dataset style
    print(f"\nProcessing dataset style: {dataset_style}")
    pipeline = NotebookPipeline(dataset_style, dfs_paths)
    pipeline.run(ans_preprocessing, ans_modelling)