"""
Script principal pour exécuter le pipeline de génération de notebooks.
"""

import sys
from nb_maker_src.core.pipeline import main

if __name__ == "__main__":
    dataset_styles = [sys.argv[1]] if len(sys.argv) > 1 else [
        'A_1_one_csv', 'B_2_joinable_csvs', 'C_1_csv_time_series'
    ]
    main(dataset_styles) 