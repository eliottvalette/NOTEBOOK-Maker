"""
Utilities for notebook generation and execution.
"""

import os
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import nbclient
from typing import List, Dict, Any

def format_notebook_cells(leaf: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format leaf information into notebook cells."""
    cells = []

    # Process cell content
    cell_content = leaf.get('cell_content', []) # gets the content of the cell from the leaf, if not provided, it will be an empty list
    if not isinstance(cell_content, list):
        cell_content = [{'type': 'code', 'content': cell_content}]
    
    for cell in cell_content:
        # Handle both dictionary and list formats
        if isinstance(cell, dict):
            cell_type = cell.get('type', 'code')
            content = cell.get('content', '')
        else:
            # If cell is a list (from YAML anchor), it should be a list of cells
            if isinstance(cell, list):
                for subcell in cell:
                    if isinstance(subcell, dict):
                        cell_type = subcell.get('type', 'code')
                        content = subcell.get('content', '')
                        
                        # Replace arguments with their values
                        if 'arg_values' in leaf:
                            for arg_name, arg_value in leaf['arg_values'].items():
                                if isinstance(arg_value, list):
                                    arg_value_str = repr(arg_value)
                                elif isinstance(arg_value, bool):
                                    arg_value_str = str(arg_value)
                                elif isinstance(arg_value, (int, float)):
                                    arg_value_str = str(arg_value)
                                else:
                                    arg_value_str = str(arg_value)
                                
                                content = content.replace(f"${arg_name}$", arg_value_str)
                        
                        # Create appropriate cell
                        if cell_type.lower() == 'markdown':
                            cells.append(new_markdown_cell(content))
                        else:
                            cells.append(new_code_cell(content))
                continue
            else:
                cell_type = 'code'
                content = str(cell)
        
        # Replace arguments with their values
        if 'arg_values' in leaf:
            for arg_name, arg_value in leaf['arg_values'].items():
                if isinstance(arg_value, list):
                    arg_value_str = repr(arg_value)
                elif isinstance(arg_value, bool):
                    arg_value_str = str(arg_value)
                elif isinstance(arg_value, (int, float)):
                    arg_value_str = str(arg_value)
                else:
                    arg_value_str = str(arg_value)
                
                content = content.replace(f"${arg_name}$", arg_value_str)
        
        # Create appropriate cell
        if cell_type.lower() == 'markdown':
            cells.append(new_markdown_cell(content))
        else:
            cells.append(new_code_cell(content))
    
    return cells

def modelling_cells(leaf_modelling: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format cells for the modelling phase."""
    cells = []
    
    # Process cell content
    cell_content = leaf_modelling.get('cell_content', [])
    if not isinstance(cell_content, list):
        cell_content = [{'type': 'code', 'content': cell_content}]
    
    for cell in cell_content:
        # Handle both dictionary and list formats
        if isinstance(cell, dict):
            cell_type = cell.get('type', 'code')
            content = cell.get('content', '')
            
            # Replace arguments with their values
            if 'arg_values' in leaf_modelling:
                for arg_name, arg_value in leaf_modelling['arg_values'].items():
                    if isinstance(arg_value, list):
                        arg_value_str = repr(arg_value)
                    elif isinstance(arg_value, bool):
                        arg_value_str = str(arg_value)
                    elif isinstance(arg_value, (int, float)):
                        arg_value_str = str(arg_value)
                    else:
                        arg_value_str = str(arg_value)
                    
                    content = content.replace(f"${arg_name}$", arg_value_str)
            
            # Create appropriate cell
            if cell_type.lower() == 'markdown':
                cells.append(new_markdown_cell(content))
            else:
                cells.append(new_code_cell(content))
        else:
            # If cell is a list (from YAML anchor), it should be a list of cells
            if isinstance(cell, list):
                for subcell in cell:
                    if isinstance(subcell, dict):
                        cell_type = subcell.get('type', 'code')
                        content = subcell.get('content', '')
                        
                        # Replace arguments with their values
                        if 'arg_values' in leaf_modelling:
                            for arg_name, arg_value in leaf_modelling['arg_values'].items():
                                if isinstance(arg_value, list):
                                    arg_value_str = repr(arg_value)
                                elif isinstance(arg_value, bool):
                                    arg_value_str = str(arg_value)
                                elif isinstance(arg_value, (int, float)):
                                    arg_value_str = str(arg_value)
                                else:
                                    arg_value_str = str(arg_value)
                                
                                content = content.replace(f"${arg_name}$", arg_value_str)
                        
                        # Create appropriate cell
                        if cell_type.lower() == 'markdown':
                            cells.append(new_markdown_cell(content))
                        else:
                            cells.append(new_code_cell(content))
            else:
                # Handle string content
                content = str(cell)
                cells.append(new_code_cell(content))
    
    return cells

def create_and_execute_notebook(cells: List[Dict[str, Any]], 
                              output_dir: str = "Output",
                              gen_filename: str = "gen_notebook.ipynb",
                              exe_filename: str = "executed_notebook.ipynb",
                              execute: bool = True) -> bool:
    """Create and execute a notebook with the given cells.
    
    Args:
        cells (list): List of notebook cells
        output_dir (str): Directory to save the notebooks
        gen_filename (str): Name of the generated notebook file
        exe_filename (str): Name of the executed notebook file
        
    Returns:
        bool: True if the notebook was created and executed successfully
    """
    try:
        # Create notebook
        notebook = new_notebook(cells=cells)
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directory '{output_dir}' created")
            
        # Define output paths
        gen_path = os.path.join(output_dir, gen_filename)
        exe_path = os.path.join(output_dir, exe_filename)
        
        # Save notebook
        with open(gen_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
        
        print(f"Notebook created and saved as: {gen_path}")
        
        # Execute notebook
        if execute:
            print("Executing notebook...")
            try:
                client = nbclient.NotebookClient(
                    notebook,
                    timeout=600,
                    kernel_name='python3',
                    resources={'path': '.'}
                )
                executed_nb = client.execute()
                
                # Save executed notebook
                with open(exe_path, 'w', encoding='utf-8') as f:
                    nbformat.write(executed_nb, f)
                
                print(f"Notebook executed and results saved as: {exe_path}")
                
            except Exception as exec_error:
                print(f"Error executing notebook: {str(exec_error)}")
                print("Notebook was generated but could not be executed automatically.")
                print(f"You can manually execute the notebook: {gen_path}")
                raise exec_error
        
        return True
    
    except Exception as e:
        print(f"Error creating notebook: {str(e)}")
        raise e