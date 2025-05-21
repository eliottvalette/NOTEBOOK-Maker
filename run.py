"""
Script principal pour exécuter le pipeline de génération de notebooks.
"""

from src.core.pipeline import main, NotebookPipeline
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        dataset_styles = [sys.argv[1]]
    else : 
        dataset_styles = ['A_1_one_csv', 'B_2_joinable_csvs', 'C_1_csv_time_series']
    
    main(dataset_styles) 