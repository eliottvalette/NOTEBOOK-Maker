"""
Script principal pour exécuter le pipeline de génération de notebooks.
"""

import sys
from nb_maker_src.core.pipeline import main
from nb_maker_src.utils.manual_load import get_datasets_paths
from nb_maker_src.utils.config import load_form_answers


if __name__ == "__main__":
    # COMMING FROM API
    if len(sys.argv) > 1: 
        dataset_styles = sys.argv[1]
        dfs_paths = [sys.argv[2]]
        ans_preprocessing = sys.argv[3]
        ans_modelling = sys.argv[4]
        main(dataset_style = dataset_styles, 
             dfs_paths = dfs_paths, 
             ans_preprocessing = ans_preprocessing, 
             ans_modelling = ans_modelling, 
             manual = False) 

    # RUNNING MANUALLY
    else:
        dataset_styles = ['A_1_one_csv', 'B_2_joinable_csvs', 'C_1_csv_time_series', 'test']
        for style in dataset_styles:
            dfs_paths = get_datasets_paths(style)
            ans_preprocessing, ans_modelling, _, _ = load_form_answers(style)
            main(dataset_style = style, 
                 dfs_paths = dfs_paths, 
                 ans_preprocessing = ans_preprocessing, 
                 ans_modelling = ans_modelling, 
                 manual = True)