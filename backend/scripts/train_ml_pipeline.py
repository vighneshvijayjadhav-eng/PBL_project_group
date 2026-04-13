import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from risk_engine.feature_config import (
    BOOLEAN_FEATURES,
    FEATURE_ORDER,
    ORDINAL_MAPPINGS,
    TARGET_COLUMN,
)

DATA_DIR = ROOT / "risk_engine" / "data"
ARTIFACTS_DIR = ROOT / "risk_engine" / "artifacts"
DATASET_PATH = DATA_DIR / "synthetic_claims_v2.csv"


def generate_synthetic_dataset(path: Path, rows: int = 2500) -> None:
    rng = np.random.default_rng(42)
    genders = np.array(["male", "female", "other"])
    severities = np.array(["low", "medium", "high"])
    locations = np.array(["Pune", "Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad"])

    claim_amount = rng.uniform(1000, 120000, rows).round(2)
    policy_tenure_months = rng.integers(1, 121, rows)
    premium_to_claim_ratio = np.clip(rng.normal(1.5, 0.7, rows), 0.05, None).round(2)
    previous_claims_count = rng.integers(0, 8, rows)
    previous_fraud_flag = rng.choice([0, 1], size=rows, p=[0.9, 0.1])
    incident_severity = rng.choice(severities, size=rows, p=[0.45, 0.35, 0.20])
    hospitalization_required = rng.choice([0, 1], size=rows, p=[0.7, 0.3])
    police_report_filed = rng.choice([0, 1], size=rows, p=[0.25, 0.75])
    document_count = rng.integers(0, 8, rows)
    claim_submission_delay_days = rng.integers(0, 61, rows)
    claimant_age = rng.integers(18, 81, rows)
    claimant_gender = rng.choice(genders, size=rows, p=[0.49, 0.49, 0.02])
    claimant_location = rng.choice(locations, size=rows)

    severity_score = np.vectorize({"low": 0.1, "medium": 0.45, "high": 0.85}.get)(incident_severity)
    location_risk = np.vectorize(
        {"Pune": 0.10, "Mumbai": 0.18, "Delhi": 0.22, "Bengaluru": 0.14, "Chennai": 0.12, "Hyderabad": 0.16}.get
    )(claimant_location)
    gender_score = np.vectorize({"male": 0.08, "female": 0.05, "other": 0.06}.get)(claimant_gender)

    fraud_signal = (
        (claim_amount / 120000) * 0.20
        + np.clip((1.2 - premium_to_claim_ratio) / 1.2, 0, 1) * 0.18
        + (previous_claims_count / 7) * 0.12
        + previous_fraud_flag * 0.18
        + severity_score * 0.10
        + hospitalization_required * 0.05
        + (1 - police_report_filed) * 0.06
        + np.clip(claim_submission_delay_days / 60, 0, 1) * 0.06
        + np.clip((2 - document_count) / 2, 0, 1) * 0.03
        + np.clip((25 - policy_tenure_months) / 24, 0, 1) * 0.04
        + location_risk
        + gender_score
    )
    fraud_probability = 1 / (1 + np.exp(-((fraud_signal * 5) - 2.2)))
    fraud_label = (rng.random(rows) < fraud_probability).astype(int)

    dataset = pd.DataFrame(
        {
            "claim_amount": claim_amount,
            "policy_tenure_months": policy_tenure_months,
            "premium_to_claim_ratio": premium_to_claim_ratio,
            "previous_claims_count": previous_claims_count,
            "previous_fraud_flag": previous_fraud_flag,
            "incident_severity": incident_severity,
            "hospitalization_required": hospitalization_required,
            "police_report_filed": police_report_filed,
            "document_count": document_count,
            "claim_submission_delay_days": claim_submission_delay_days,
            "claimant_age": claimant_age,
            "claimant_gender": claimant_gender,
            "claimant_location": claimant_location,
            "fraud_label": fraud_label,
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(path, index=False)


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        generate_synthetic_dataset(path)

    dataset = pd.read_csv(path)
    expected_columns = FEATURE_ORDER + [TARGET_COLUMN]
    if list(dataset.columns) != expected_columns:
        raise ValueError(
            f"SCHEMA_MISMATCH: expected columns {expected_columns}, got {list(dataset.columns)}"
        )
    if dataset[FEATURE_ORDER + [TARGET_COLUMN]].isnull().any().any():
        raise ValueError("FEATURE_MISSING: dataset contains null values")
    return dataset


def fit_encoders(dataset: pd.DataFrame) -> dict[str, dict[str, int]]:
    encoders: dict[str, dict[str, int]] = {}
    encoders["claimant_gender"] = {"male": 0, "female": 1, "other": 2}
    encoders["incident_severity"] = ORDINAL_MAPPINGS["incident_severity"]
    location_values = sorted(dataset["claimant_location"].astype(str).unique().tolist())
    encoders["claimant_location"] = {value: index for index, value in enumerate(location_values)}
    return encoders


def transform_features(dataset: pd.DataFrame, encoders: dict[str, dict[str, int]]) -> pd.DataFrame:
    frame = dataset.copy()
    for feature in BOOLEAN_FEATURES:
        frame[feature] = frame[feature].astype(int)

    frame["claimant_gender"] = frame["claimant_gender"].map(encoders["claimant_gender"])
    frame["incident_severity"] = frame["incident_severity"].map(encoders["incident_severity"])
    frame["claimant_location"] = frame["claimant_location"].map(encoders["claimant_location"])

    if frame[FEATURE_ORDER].isnull().any().any():
        raise ValueError("MODEL_INPUT_INVALID: encoding produced null values")
    return frame


def evaluate_model(name: str, model, x_test, y_test) -> dict[str, float]:
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1_score": f1_score(y_test, predictions, zero_division=0),
    }
    print(f"{name} Metrics")
    for metric_name, metric_value in metrics.items():
        print(f"  {metric_name}: {metric_value:.4f}")
    return metrics


def main() -> None:
    dataset = load_dataset(DATASET_PATH)
    encoders = fit_encoders(dataset)
    transformed = transform_features(dataset, encoders)

    x = transformed[FEATURE_ORDER]
    y = transformed[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    logistic_model = LogisticRegression(max_iter=2000, random_state=42)
    logistic_model.fit(x_train_scaled, y_train)
    logistic_metrics = evaluate_model("LogisticRegression", logistic_model, x_test_scaled, y_test)

    random_forest_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
    )
    random_forest_model.fit(x_train_scaled, y_train)
    random_forest_metrics = evaluate_model("RandomForestClassifier", random_forest_model, x_test_scaled, y_test)

    best_name = "RandomForestClassifier"
    best_model = random_forest_model
    best_metrics = random_forest_metrics
    if logistic_metrics["f1_score"] > random_forest_metrics["f1_score"]:
        best_name = "LogisticRegression"
        best_model = logistic_model
        best_metrics = logistic_metrics

    print(f"Selected model: {best_name} (f1_score={best_metrics['f1_score']:.4f})")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with (ARTIFACTS_DIR / "best_model.pkl").open("wb") as model_file:
        pickle.dump(
            {
                "model_name": best_name,
                "model": best_model,
                "feature_order": FEATURE_ORDER,
            },
            model_file,
        )
    with (ARTIFACTS_DIR / "scaler.pkl").open("wb") as scaler_file:
        pickle.dump(scaler, scaler_file)
    with (ARTIFACTS_DIR / "encoders.pkl").open("wb") as encoders_file:
        pickle.dump(encoders, encoders_file)
    with (ARTIFACTS_DIR / "feature_order.json").open("w", encoding="utf-8") as feature_file:
        json.dump(FEATURE_ORDER, feature_file, indent=2)


if __name__ == "__main__":
    main()
