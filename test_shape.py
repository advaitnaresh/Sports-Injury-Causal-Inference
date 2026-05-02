import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from src.phase2_real_data_analysis import load_real_data, prepare_real_data

df_real = load_real_data()
df_real_clean, X_real, T_real, Y_real, summary = prepare_real_data(df_real)

with pm.Model() as bayesian_model:
    X_data = pm.Data("X_data", X_real)
    T_data = pm.Data("T_data", T_real)
    
    beta_0 = pm.Normal("beta_0", mu=-2, sigma=1)
    beta_X = pm.Normal("beta_X", mu=0, sigma=1)
    beta_T = pm.Normal("beta_T", mu=0, sigma=1)
    
    logit_p = beta_0 + beta_X * X_data + beta_T * T_data
    p = pm.Deterministic("p", pm.math.invlogit(logit_p))
    Y_obs = pm.Bernoulli("Y_obs", p=p, observed=Y_real)
    
    trace_real = pm.sample(draws=10, tune=10, chains=1, random_seed=42)
    ppc_real = pm.sample_posterior_predictive(trace_real, random_seed=42)

y_raw = ppc_real.posterior_predictive["Y_obs"].values
print("y_raw.shape:", y_raw.shape)
