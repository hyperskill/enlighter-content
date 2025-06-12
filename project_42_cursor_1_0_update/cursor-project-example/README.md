# Iris Dataset Analysis Project

## Overview
This project contains a comprehensive Jupyter notebook analysis of the classic Iris dataset, featuring distribution visualizations and exploratory data analysis.

## Generated Files
- `iris_analysis.ipynb` - Main Jupyter notebook with complete analysis
- `requirements.txt` - All necessary Python packages
- `README.md` - This documentation file

## Package Analysis
The notebook uses the following key libraries:

### Core Data Libraries
- **pandas** (≥1.5.0) - Data manipulation and analysis
- **numpy** (≥1.21.0) - Numerical computing
- **scikit-learn** (≥1.0.0) - Machine learning library (includes Iris dataset)

### Visualization Libraries
- **matplotlib** (≥3.5.0) - Basic plotting functionality
- **seaborn** (≥0.11.0) - Statistical data visualization

### Jupyter Environment
- **jupyter** (≥1.0.0) - Core Jupyter functionality
- **notebook** (≥6.4.0) - Jupyter notebook interface
- **ipykernel** (≥6.0.0) - Python kernel for Jupyter
- **jupyterlab** (≥3.0.0) - Modern notebook interface

## Installation Status
✅ **All packages successfully installed!**

The installation process confirmed that most packages were already available in the system, with only `jupyter` and `notebook` packages needing to be newly installed.

## Key Features of the Analysis

### 1. Dataset Overview
- Complete dataset loading and exploration
- Statistical summary and data quality checks
- 150 samples, 4 features, 3 species classes

### 2. Label Distribution Analysis
- **Bar Plot**: Visual count of each species
- **Pie Chart**: Percentage distribution with colors
- Shows perfect balance: 50 samples per species (33.3% each)

### 3. Advanced Visualizations
- Feature distribution histograms by species
- Correlation heatmap between features
- Scatter plot matrix for comprehensive analysis
- Professional styling with colors and labels

## How to Run
1. Ensure all packages are installed (already done)
2. Open the notebook:
   ```bash
   jupyter notebook iris_analysis.ipynb
   ```
   Or use JupyterLab:
   ```bash
   jupyter lab iris_analysis.ipynb
   ```
3. Run all cells to see the complete analysis

## Key Insights
- **Balanced Dataset**: Equal representation of all three iris species
- **Clean Data**: No missing values, well-structured format
- **Feature Relationships**: Strong correlation between petal measurements
- **Species Separation**: Clear patterns distinguish different species

## System Requirements
- Python 3.7+
- All packages listed in requirements.txt
- Jupyter notebook environment

## Notes
- The notebook is designed to run completely from start to finish
- All visualizations are embedded and ready to display
- Code includes proper styling and error handling 