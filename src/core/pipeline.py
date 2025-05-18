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

from src.utils.config import load_decision_trees, load_form_answers
from src.utils.insights import get_insights_and_answers, get_insights_for_modelling
from src.utils.mistral_calls import send_to_mistral
from src.utils.notebook import format_notebook_cells, modelling_cells, create_and_execute_notebook

class NotebookPipeline:
    def __init__(self, dataset_style: str):
        """Initialize the pipeline with a specific dataset style."""
        self.dataset_style = dataset_style
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")
        
        # Define base paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.datasets_dir = self.base_dir / 'Datasets'
        self.output_dir = self.base_dir / 'Output'

    def load_datasets(self) -> List[pd.DataFrame]:
        """Load datasets based on the dataset style."""
        print(f"Loading datasets for style: {self.dataset_style}")
        
        try:
            if self.dataset_style == 'A_1_one_csv':
                # Single CSV with target
                df_path = self.datasets_dir / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset1_with_target.csv'
                if not df_path.exists():
                    raise FileNotFoundError(f"Dataset file not found: {df_path}")
                df = pd.read_csv(df_path)
                return [df]
                
            elif self.dataset_style == 'B_2_joinable_csvs':
                # Two joinable CSVs
                df1_path = self.datasets_dir / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset1_with_target.csv'
                df2_path = self.datasets_dir / 'Tabular' / 'Binary_pred' / 'csv' / 'dataset2_features_only.csv'
                
                if not df1_path.exists():
                    raise FileNotFoundError(f"Dataset file not found: {df1_path}")
                if not df2_path.exists():
                    raise FileNotFoundError(f"Dataset file not found: {df2_path}")
                    
                df1 = pd.read_csv(df1_path)
                df2 = pd.read_csv(df2_path)
                return [df1, df2]
                
            elif self.dataset_style == 'C_1_csv_time_series':
                # Time series CSV
                df_path = self.datasets_dir / 'Tabular' / 'Time_series' / 'csv' / 'dataset_time_series.csv'
                if not df_path.exists():
                    raise FileNotFoundError(f"Dataset file not found: {df_path}")
                df = pd.read_csv(df_path)
                return [df]
            
            elif self.dataset_style == 'test':
                # Test dataset
                df_path = self.datasets_dir / 'Tabular' / 'Binary_pred' / 'excel' / 'dataset1_with_target.xlsx'
                if not df_path.exists():
                    raise FileNotFoundError(f"Dataset file not found: {df_path}")
                df = pd.read_excel(df_path)
                return [df]
                
            else:
                raise ValueError(f"Unknown dataset style: {self.dataset_style}")
                
        except Exception as e:
            print(f"Error loading datasets: {str(e)}")
            raise

    def run(self) -> bool:
        """Run the complete pipeline."""
        try:
            print("Starting automated pipeline...")
            
            # Load datasets
            print("Loading datasets...")
            dfs = self.load_datasets()
            
            # Get insights and form answers
            print("Extracting insights from data...")
            insights = get_insights_and_answers(*dfs, dataset_style=self.dataset_style)
            
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
            insights_modelling = get_insights_for_modelling(insights, dataset_style=self.dataset_style)
            
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

def main():
    """Main entry point for the pipeline."""
    try:
        # Run pipeline for each dataset style
        for dataset_style in ['A_1_one_csv', 'B_2_joinable_csvs', 'C_1_csv_time_series']:
            print(f"\nProcessing dataset style: {dataset_style}")
            pipeline = NotebookPipeline(dataset_style)
            pipeline.run()
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 