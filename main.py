from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass
class SurrogateConfig:
    excel_path: Path
    train_sheet: str
    test_sheet: str
    input_tags: Sequence[str]
    output_tags: Sequence[str]
    time_tag: str = "time"


def _split_X_y(
    df: pd.DataFrame, cfg: SurrogateConfig
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    print("## [split] DataFrame columns:", list(df.columns))
    print("## [split] Using time tag:", cfg.time_tag)

    feature_cols = [c for c in cfg.input_tags if c in df.columns and c != cfg.time_tag]
    missing_inputs = [c for c in cfg.input_tags if c not in df.columns]
    if missing_inputs:
        raise ValueError(f"Missing input tags in Excel: {missing_inputs!r}")

    X = df.loc[:, feature_cols].to_numpy(dtype=float)

    y_dict: Dict[str, np.ndarray] = {}
    for tag in cfg.output_tags:
        if tag not in df.columns:
            raise ValueError(f"Missing output tag in Excel: {tag!r}")
        y_dict[tag] = df[tag].to_numpy(dtype=float)

    return X, y_dict


def load_train_test(cfg: SurrogateConfig):
    print("### [data] Loading Excel from:", cfg.excel_path)
    excel_path = Path(cfg.excel_path)
    if not excel_path.is_file():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    train_df = pd.read_excel(excel_path, sheet_name=cfg.train_sheet)
    test_df = pd.read_excel(excel_path, sheet_name=cfg.test_sheet)

    print("### [data] Train shape:", train_df.shape, "Test shape:", test_df.shape)

    X_train, y_train = _split_X_y(train_df, cfg)
    X_test, y_test = _split_X_y(test_df, cfg)

    print("### [data] X_train shape:", X_train.shape)
    print("### [data] Outputs in train:", list(y_train.keys()))

    return train_df, test_df, X_train, y_train, X_test, y_test


def train_baseline_models(
    X_train: np.ndarray,
    y_train: Dict[str, np.ndarray],
    n_estimators: int = 200,
    random_state: int = 0,
) -> Dict[str, RandomForestRegressor]:
    print("### [train] Starting training. X_train shape:", X_train.shape)
    models: Dict[str, RandomForestRegressor] = {}
    for tag, y in y_train.items():
        print(f"### [train] Training model for output tag: {tag}, y shape: {y.shape}")
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )
        model.fit(X_train, y)
        print(f"### [train] Finished training model for {tag}")
        models[tag] = model
    return models


def evaluate_models(
    models: Dict[str, RandomForestRegressor],
    X: np.ndarray,
    y_true: Dict[str, np.ndarray],
) -> Dict[str, Dict[str, float]]:
    print("### [eval] Evaluating models")
    metrics: Dict[str, Dict[str, float]] = {}
    for tag, model in models.items():
        if tag not in y_true:
            continue
        y_pred = model.predict(X)
        yt = y_true[tag]
        mae = float(mean_absolute_error(yt, y_pred))
        # Older versions of scikit-learn may not support squared=False,
        # so compute RMSE manually from MSE.
        mse = float(mean_squared_error(yt, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(yt, y_pred))
        print(f"#### [eval] Tag={tag} MAE={mae:.6g} RMSE={rmse:.6g} R2={r2:.6g}")
        metrics[tag] = {
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
        }
    return metrics


def main() -> None:
    """
    Run the surrogate modelling experiment and print results in a notebook-friendly way.
    """
    cfg = SurrogateConfig(
        excel_path=Path("simple_dynamic_process.xlsx"),
        train_sheet="Training Data",
        test_sheet="Testing Data",
        # Column names are case-sensitive: use exactly what's in the Excel header
        input_tags=["U1", "U2"],
        output_tags=["Y1", "Y2"],
        time_tag="Time",
    )

    print("# Surrogate Model Experiment")

    # Load data
    train_df, test_df, X_train, y_train, X_test, y_test = load_train_test(cfg)

    print("\n# Data Preview (Train head)")
    print(train_df.head())

    print("\n# Data Preview (Test head)")
    print(test_df.head())

    # Train models
    models = train_baseline_models(X_train, y_train)

    # Evaluate
    print("\n# Train Metrics")
    train_metrics = evaluate_models(models, X_train, y_train)
    print(train_metrics)

    print("\n# Test Metrics")
    test_metrics = evaluate_models(models, X_test, y_test)
    print(test_metrics)

    # Plot actual vs predicted for train and test for each output
    print("\n# Plots")
    n_tags = len(cfg.output_tags)
    fig, axes = plt.subplots(2, n_tags, figsize=(5 * n_tags, 8), sharex=False)

    if n_tags == 1:
        axes = np.array([[axes[0]], [axes[1]]])  # normalize shape to 2 x n_tags

    for j, tag in enumerate(cfg.output_tags):
        y_train_true = y_train[tag]
        y_train_pred = models[tag].predict(X_train)
        y_test_true = y_test[tag]
        y_test_pred = models[tag].predict(X_test)

        idx_train = np.arange(len(y_train_true))
        idx_test = np.arange(len(y_test_true))

        # Train: actual vs predicted over time index
        ax_train = axes[0, j]
        ax_train.plot(idx_train, y_train_true, label="Train actual", alpha=0.7)
        ax_train.plot(idx_train, y_train_pred, label="Train predicted", alpha=0.7)
        ax_train.set_title(f"{tag} - Train")
        ax_train.set_xlabel("Sample index")
        ax_train.set_ylabel(tag)
        ax_train.legend()

        # Test: scatter actual vs predicted
        ax_test = axes[1, j]
        ax_test.scatter(y_test_true, y_test_pred, s=10, alpha=0.6)
        min_val = min(y_test_true.min(), y_test_pred.min())
        max_val = max(y_test_true.max(), y_test_pred.max())
        ax_test.plot([min_val, max_val], [min_val, max_val], "r--", label="Ideal")
        ax_test.set_title(f"{tag} - Test (actual vs predicted)")
        ax_test.set_xlabel("Actual")
        ax_test.set_ylabel("Predicted")
        ax_test.legend()

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
