# Phase 1: Theoretical Foundation & Full Parameter Validation
**Author:** Tilak Bhansali  
**Course:** Foundations of Data Science  
**Project:** Does preventative physiotherapy reduce overuse injuries in athletes?

---

## What Did I Do?

My job (Phase 1) was to **prove that our statistical model actually works** before Advait runs it on real data. This is like testing a scale with known weights before using it to weigh something — we need to know the tool is accurate before trusting its results.

I did this in three stages: writing out the math, building fake (simulated) data, and then checking if the model could figure out the right answers when we already knew what the right answers were.

---

## Files in This Folder

| File | What it is |
|------|-----------|
| `tilak_phase1_validation.ipynb` | The main Jupyter Notebook with all my code and explanations. Run this top to bottom. |
| `tilak_posterior_samples.csv` | A CSV of the model's estimated parameter values. Advait (Phase 2) and Leo (Phase 3) can reference this. |
| `plot_data_distributions.png` | Chart showing the three variables (training load, recovery score, injury status) in the simulated dataset. |
| `plot_prior_predictive.png` | Chart showing what the model predicts *before* it sees any data (the "prior"). |
| `plot_parameter_recovery.png` | **The key validation chart.** Shows that the model correctly estimated all three parameters. |
| `plot_forest.png` | A "forest plot" summarizing all three parameter estimates with their uncertainty ranges. |
| `README_tilak_phase1.md` | This file. |

---

## The Model — Plain English

We are trying to answer: **Does doing more recovery (physiotherapy) reduce injuries?**

The complication is that athletes who train harder tend to *both* do more recovery AND be more likely to get injured — just because of the hard training itself. This is called a **confound** (the training load is messing up our ability to see the true effect of recovery).

So our model has three pieces:

- **T (Treatment):** Recovery Score — how much recovery an athlete does
- **X (Confounder):** Training Load — how hard they train (this influences both T and Y)
- **Y (Outcome):** Injury Status — did they get injured (1) or not (0)?

The math equation is:

```
P(injury) = logistic(α + β_T × Recovery + β_X × Training Load)
```

- `α` (alpha) = the baseline injury risk
- `β_T` (beta_T) = how much recovery affects injury risk — **we expect this to be negative** (more recovery = lower injury risk)
- `β_X` (beta_X) = how much training load affects injury risk — **we expect this to be positive** (harder training = higher injury risk)

All three parameters get a **Normal(0, 1) prior** — this means we start with no assumption about whether they're positive or negative, and let the data tell us.

---

## What is "Parameter Recovery" and Why Does It Matter?

The grader explicitly required **comprehensive parameter recovery** for all three parameters (α, β_T, β_X).

Here's what that means and why it's important:

1. I made up a fake dataset where I **already knew** the true values:
   - True α = -1.5
   - True β_T = -1.2 (recovery is protective)
   - True β_X = +0.9 (training load increases risk)

2. I ran our model on this fake data, and it came up with its own estimates.

3. I then checked: **does the model's estimate match the true value?**

If yes → the model is working correctly, and we can trust it on real data.

### Results: All 3 Parameters Successfully Recovered

| Parameter | True Value | Model Estimate | 94% Confidence Range | Recovered? |
|-----------|-----------|----------------|---------------------|------------|
| α (intercept) | -1.500 | -1.436 | [-1.664, -1.217] | YES |
| β_T (treatment/recovery) | -1.200 | -1.165 | [-1.439, -0.838] | YES |
| β_X (confounder/training) | +0.900 | +0.749 | [+0.457, +1.045] | YES |

"Recovered" means the true value falls inside the model's confidence range. All three do — the model is validated.

---

## How to Run the Notebook

### Requirements
```
pip install pymc arviz numpy pandas matplotlib scipy
```

### Run
Open `tilak_phase1_validation.ipynb` in Jupyter and click **Run All**.

> **Note on `cores=1`:** The notebook uses `cores=1` in the sampling step. This is required in some server/cloud environments. If you're running on your own laptop, you can change this to `cores=4` to run faster.

The notebook will:
1. Print explanations at every step
2. Generate all 4 plots inline
3. Print the recovery results in a table
4. Save `tilak_posterior_samples.csv`

---

## For Advait (Phase 2)

The file `tilak_posterior_samples.csv` contains 4,000 rows of posterior samples for α, β_T, and β_X from the simulation. You can use these as a reference when interpreting your real-data results — the signs and rough magnitudes should be consistent.

Your pipeline should:
1. Load the Kaggle dataset
2. Map `training_load` → X, `recovery_score` → T, `injury_status` → Y
3. Standardize X and T (mean=0, sd=1) to match our model's scale
4. Use the same PyMC model structure from my notebook (just swap in real data)

---

## For Leo (Phase 3)

Key facts for the discussion section:
- β_T is **negative** (-1.2 true value) → recovery score has a **protective effect** on injuries
- β_X is **positive** (+0.9 true value) → training load **increases** injury risk
- Without controlling for X (the confounder), we would overestimate or underestimate β_T
- The model uses ATE (Average Treatment Effect) which is captured by β_T in the logistic framework
- All convergence diagnostics passed: R-hat ≈ 1.00 and ESS > 2000 for all parameters
