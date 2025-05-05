# Automated Data Science Notebook Generator (Prototype)

This project is a prototype of a fully automated pipeline that ingests user-provided data, determines appropriate analysis/modeling objectives, and generates executable Jupyter notebooks through an intelligent decision tree system powered by Mistral API.

## Work in Progress
**Note: This project is currently under active development.** The decision tree structure and some core components are still being built and refined.

## Project Overview

The main goal is to streamline the data analysis and modeling workflow by:
- Automatically analyzing input datasets
- Routing through a decision tree based on data characteristics and user preferences
- Generating and executing custom Jupyter notebooks tailored to specific analysis needs

## Current Data Support

The pipeline is structured based on the decision trees defined in YAML files and currently supports:

### Tabular Data Processing (Based on decision_tree_preprocessing.yaml)
- **Single Table Processing**:
  - CSV files
  - Excel files
- **Multiple Tables Processing**:
  - CSV files with common ID column for joining
  - Excel files with multiple sheets (planned)

### Modeling Approaches (Based on decision_tree_modelling.yaml)
- **Multiclass Classification**:
  - Random Forest/XGBoost implementation
- **Regression**:
  - Neural Network implementation
- **Time Series Forecasting**:
  - LSTM implementation

## Pipeline Architecture

1. **Data Ingestion**
   - Loading various data formats according to preprocessing decision tree
   - Basic data inspection and feature analysis

2. **User Preferences Collection**
   - Configuration parameters collected through form answers (currently simulated in code)
   - Analysis objectives determination

3. **Decision Tree Logic**
   - Structured YAML-defined decision trees for preprocessing and modeling
   - Mistral API integration for intelligent routing through the decision trees

4. **Dynamic Notebook Generation**
   - Context-aware code cell generation
   - Model selection based on data characteristics
   - Code generation for preprocessing, modeling, visualization, and evaluation

5. **Execution Engine**
   - Automatic notebook execution
   - Results and visualizations generation

## Decision Tree System

The system uses two primary decision trees:
- **Preprocessing Decision Tree**: Determines how to handle data based on format and structure
- **Modeling Decision Tree**: Selects appropriate modeling techniques based on task type

Each leaf node in the decision trees contains specific code templates that are assembled into a complete notebook.

## Getting Started

1. Clone this repository
2. Install required dependencies (requirements file coming soon)
3. Set up your Mistral API key in a `.env` file
4. Run the prototype:
   ```
   python prototype.py
   ```

## Coming Soon

- Web interface for dataset upload and configuration
- Support for more data types (images, text)
- Additional modeling techniques
- User-friendly parameter customization
- Enhanced visualization options

## Input Data

The pipeline expects:
- Two CSV files:
  - One with a common `ID` column and various features,
  - The other also containing a `YTarget` column (the target variable).

## Pipeline Steps

1. **Data Loading and Merging**
   - Load both CSVs with `pandas`.
   - Merge on the `ID` column.
   - Basic data inspection (`df.describe()`, `df.info()`, etc.).

2. **Question Generation**
   - Based on data inspection, ask questions such as:
     - _Do you want predictions?_
     - _Are you analyzing prices?_
     - _Do you prefer Gradient Boosting?_

3. **Mistral Decision Logic**
   - The user's answers are sent to the Mistral API.
   - A simple decision tree (defined in YAML) determines which notebook cells to generate.

4. **Notebook Generation**
   - Using `nbformat`, Python code cells are injected depending on decision tree outcomes.
   - Example cells include:
     - Data preparation,
     - Gradient Boosting training,
     - Price analysis,
     - Feature importance visualization.

5. **Notebook Execution**
   - The notebook is automatically executed (e.g., via `nbconvert` or `papermill`).
   - Results are returned to the user, including metrics and visualizations.

## Example Decision Tree (YAML)

```yaml
questions:
  - id: wants_prediction
    question: "Do you want to make predictions?"
    type: boolean
  - id: wants_price_analysis
    question: "Do you want to analyze pricing?"
    type: boolean
  - id: wants_gradboost
    question: "Do you prefer using Gradient Boosting?"
    type: boolean

decision_tree:
  - if: wants_prediction == true
    then:
      actions:
        - generate_cell: "prepare_and_train_model"

  - if: wants_price_analysis == true
    then:
      actions:
        - generate_cell: "price_analysis"

  - if: wants_gradboost == true
    then:
      actions:
        - generate_cell: "train_gradboost"
