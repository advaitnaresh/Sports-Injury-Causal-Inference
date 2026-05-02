# Advait Phase 2 Guide

This file documents Advait's Phase 2 real-data execution work for the sports injury causal inference project.

## Dataset Placement

Place the Kaggle dataset CSV in one of these locations:

- `data/multimodal_sports_injury_dataset.csv`
- `multimodal_sports_injury_dataset.csv`

The notebook and helper script will search for the expected file name and load it automatically.

## Files Added

- `src/phase2_real_data_analysis.py`
  - Contains functions to load the real dataset, preprocess the relevant columns, standardize the confounder and treatment, and generate diagnostics plots.

- `leo_phase3_master_notebook.ipynb`
  - Updated Section 5 with real-data loading and preprocessing.
  - Updated Section 6 with the real-data posterior model run and MCMC diagnostics.
  - Updated Section 7 with the posterior predictive check plot that includes observed data, posterior mean, mean uncertainty, and prediction uncertainty.

## How to Run

1. Install dependencies:

```bash
pip install pymc arviz numpy pandas matplotlib scipy
```

2. Place the dataset CSV in `data/multimodal_sports_injury_dataset.csv`.

3. Open and run `leo_phase3_master_notebook.ipynb`.

4. If you want to run the helper script directly:

```bash
python src/phase2_real_data_analysis.py
```

## Notes

- The notebook reuses the same Bayesian logistic model defined in Section 4.
- The binary outcome is defined as `injury_occurred == 2` to represent injured athlete-days.
- The script standardizes `training_load` and `recovery_score` to mean 0 and standard deviation 1, matching the Phase 1 validation scale.
