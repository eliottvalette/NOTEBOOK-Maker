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
