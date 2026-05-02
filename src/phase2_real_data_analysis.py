import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
import arviz as az
from pathlib import Path


RANDOM_SEED = 42


def find_dataset_path(path_hint=None):
    candidates = []
    if path_hint is not None:
        candidates.append(Path(path_hint))
    candidates.extend([
        Path("data/multimodal_sports_injury_dataset.csv"),
        Path("multimodal_sports_injury_dataset.csv"),
    ])
    candidates.extend(Path(".").glob("*multimodal*injury*.csv"))
    candidates.extend(Path("data").glob("*multimodal*injury*.csv"))

    for candidate in candidates:
        if candidate is not None and candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not find the dataset file. Please place the Kaggle CSV as '\n"
        "data/multimodal_sports_injury_dataset.csv' or 'multimodal_sports_injury_dataset.csv' in the repository root."
    )


def load_real_data(csv_path=None):
    csv_path = find_dataset_path(csv_path)
    df = pd.read_csv(csv_path)
    print(f"Loaded real dataset from: {csv_path}")
    print(f"Shape: {df.shape}")
    return df


def prepare_real_data(
    df,
    x_col="training_load",
    t_col="recovery_score",
    target_col="injury_occurred",
    injured_label=2,
):
    df = df.copy()
    expected_columns = {x_col, t_col, target_col}
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise KeyError(
            f"Missing required columns in the dataset: {sorted(missing_columns)}. "
            "Please verify the CSV column names."
        )

    df = df.drop_duplicates()
    df = df.dropna(subset=[x_col, t_col, target_col])

    df["X_training_load"] = (df[x_col] - df[x_col].mean()) / df[x_col].std(ddof=0)
    df["T_recovery_score"] = (df[t_col] - df[t_col].mean()) / df[t_col].std(ddof=0)
    df["Y_injury_binary"] = (df[target_col] == injured_label).astype(int)

    n_rows = len(df)
    n_injured = int(df["Y_injury_binary"].sum())
    observed_rate = n_injured / n_rows

    summary = {
        "n_rows": n_rows,
        "n_injured": n_injured,
        "injury_rate": observed_rate,
        "x_mean": float(df["X_training_load"].mean()),
        "x_std": float(df["X_training_load"].std(ddof=0)),
        "t_mean": float(df["T_recovery_score"].mean()),
        "t_std": float(df["T_recovery_score"].std(ddof=0)),
        "correlation_X_T": float(df[["X_training_load", "T_recovery_score"]].corr().iloc[0, 1]),
    }

    print("Real-data preprocessing summary:")
    print(f"  Rows after dropna/duplicates: {n_rows}")
    print(f"  Binary injury rate (Y=2 → injured): {observed_rate:.3%} ({n_injured}/{n_rows})")
    print(f"  Standardized X mean = {summary['x_mean']:.3f}, sd = {summary['x_std']:.3f}")
    print(f"  Standardized T mean = {summary['t_mean']:.3f}, sd = {summary['t_std']:.3f}")
    print(f"  Correlation between X and T = {summary['correlation_X_T']:.3f}")

    return (
        df,
        df["X_training_load"].to_numpy(dtype=float),
        df["T_recovery_score"].to_numpy(dtype=float),
        df["Y_injury_binary"].to_numpy(dtype=int),
        summary,
    )


def plot_real_data_distribution(X, T, Y, output_path="./plot_real_data_distributions_real.png"):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4))
    fig.suptitle("Real Dataset — Variable Distributions", fontsize=14, fontweight="bold")

    axes[0].hist(X, bins=30, color="#4C8DBF", edgecolor="white", alpha=0.85)
    axes[0].set_title("Training Load X (Confounder)")
    axes[0].set_xlabel("Standardized")
    axes[0].set_ylabel("Count")

    axes[1].hist(T, bins=30, color="#5DAE6F", edgecolor="white", alpha=0.85)
    axes[1].set_title("Recovery Score T (Treatment)")
    axes[1].set_xlabel("Standardized")

    counts = [Y.sum(), len(Y) - Y.sum()]
    bars = axes[2].bar(["Injured (Y=1)", "Not Injured (Y=0)"], counts,
                       color=["#E07A5F", "#7CB7C1"], edgecolor="white")
    axes[2].set_title("Injury Status Y (Binary Outcome)")
    axes[2].set_ylabel("Count")
    for bar, count in zip(bars, counts):
        axes[2].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 5,
                     str(count), ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()


def run_real_model(bayesian_model, X, T, Y=None, draws=2000, tune=1000, chains=4, cores=1):
    with bayesian_model:
        data_dict = {"T_data": T, "X_data": X}
        if Y is not None:
            data_dict["Y_data"] = Y
        pm.set_data(data_dict)
        trace_real = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=cores,
            target_accept=0.9,
            random_seed=RANDOM_SEED,
            return_inferencedata=True,
            progressbar=True,
        )
    return trace_real


def plot_real_posterior_predictive(Y, trace, ppc, output_path="./plot_real_posterior_predictive.png", n_bins=10):
    mean_p = trace.posterior["p"].mean(dim=["chain", "draw"]).values
    hdi_p = az.hdi(trace.posterior, hdi_prob=0.89)["p"].values
    lower_mean, upper_mean = hdi_p[:, 0], hdi_p[:, 1]

    y_raw = ppc.posterior_predictive["Y_obs"].values
    y_draws = y_raw.reshape(-1, y_raw.shape[-1])

    bin_ids = pd.qcut(mean_p, q=n_bins, labels=False, duplicates="drop")
    group_index = np.arange(len(mean_p))

    binned = pd.DataFrame({
        "mean_p": mean_p,
        "y": Y,
        "lower_mean": lower_mean,
        "upper_mean": upper_mean,
        "bin": bin_ids,
    })

    bin_summary = binned.groupby("bin").agg(
        observed_rate=("y", "mean"),
        mean_pred=("mean_p", "mean"),
        lower_mean=("lower_mean", "mean"),
        upper_mean=("upper_mean", "mean"),
        count=("y", "size"),
    ).reset_index()

    posterior_probs_by_bin = []
    for draw in y_draws:
        posterior_probs_by_bin.append(
            pd.Series(draw, index=group_index)
              .groupby(bin_ids)
              .mean()
              .values
        )
    posterior_probs_by_bin = np.vstack(posterior_probs_by_bin)

    bin_summary["lower_pred"] = np.percentile(posterior_probs_by_bin, 5.5, axis=0)
    bin_summary["upper_pred"] = np.percentile(posterior_probs_by_bin, 94.5, axis=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(bin_summary["mean_pred"], bin_summary["observed_rate"], marker="o", color="#2B3A67",
            label="Observed injury rate")
    ax.plot(bin_summary["mean_pred"], bin_summary["mean_pred"], color="#444444", linestyle="--",
            label="Perfect calibration")
    ax.fill_between(bin_summary["mean_pred"], bin_summary["lower_mean"], bin_summary["upper_mean"],
                    color="#A3C4BC", alpha=0.35, label="89% HDI of mean predicted probability")
    ax.fill_between(bin_summary["mean_pred"], bin_summary["lower_pred"], bin_summary["upper_pred"],
                    color="#E8B4A0", alpha=0.25, label="89% predictive interval for Y")

    ax.set_title("Posterior Predictive Check — Real Data Calibration", fontsize=14, fontweight="bold")
    ax.set_xlabel("Mean Predicted Injury Probability")
    ax.set_ylabel("Observed Injury Rate")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()

    return bin_summary


if __name__ == "__main__":
    df_real = load_real_data()
    df_real_clean, X_real, T_real, Y_real, summary = prepare_real_data(df_real)
    plot_real_data_distribution(X_real, T_real, Y_real)
    print(summary)
