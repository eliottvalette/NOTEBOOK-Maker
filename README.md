# Automated Data Science Notebook Generator

## Project Description

This project provides an automated pipeline for generating and executing Jupyter notebooks tailored to specific data analysis and modeling tasks. The system leverages decision trees and large language models (Mistral API) to dynamically determine preprocessing and modeling steps based on the characteristics of the input data. The solution is designed to streamline the workflow from raw data ingestion to the delivery of ready-to-use, executable notebooks.

## Key Features

- **Automated Data Analysis**: Ingests user-selected datasets and performs initial inspection and feature analysis.
- **Decision Tree-Driven Workflow**: Utilizes structured YAML-based decision trees to guide preprocessing and modeling choices.
- **LLM Integration**: Integrates with the Mistral API to enhance decision-making and code generation at each step.
- **Dynamic Notebook Generation**: Assembles context-aware code and markdown cells into a Jupyter notebook, customized for the selected dataset and analysis objectives.
- **Notebook Execution**: Automatically executes the generated notebook, producing a version with results and visualizations.
- **Web Interface**: Provides a modern web interface for dataset selection, notebook generation, download, and preview.

## System Architecture

- **Frontend**: Built with Next.js and React, the interface allows users to select dataset styles, trigger notebook generation, and preview or download results.
- **API Backend**: FastAPI serves as the backend, exposing endpoints for notebook generation, execution, and preview. It manages communication between the frontend and the pipeline.
- **Pipeline**: The core pipeline (Python) orchestrates data loading, decision tree traversal, LLM calls, notebook assembly, and execution. Outputs are stored in the `Output/` directory.

## Workflow Overview

1. **Dataset Selection**: The user selects a dataset style via the web interface.
2. **Notebook Generation**: The frontend sends a request to the FastAPI backend, which triggers the pipeline to generate and execute a notebook based on the selected dataset.
3. **Output Delivery**: The backend provides endpoints to download the generated and executed notebooks, or to preview them as HTML in the browser.

## Output

- Generated and executed notebooks are saved in the `Output/` directory, named according to the dataset style (e.g., `gen_A_1_one_csv.ipynb`, `exe_A_1_one_csv.ipynb`).
- Notebooks can be downloaded or previewed directly from the web interface.

## Extensibility

The system is designed for modularity and extensibility. Decision trees, code templates, and data ingestion logic can be adapted to support new data types, analysis tasks, or modeling techniques as requirements evolve.

## Development Status

This project is under active development. The decision tree logic, LLM integration, and user interface are subject to ongoing refinement and extension.

