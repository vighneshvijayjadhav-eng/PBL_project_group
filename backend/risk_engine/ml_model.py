import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.config import settings
from risk_engine.feature_config import BOOLEAN_FEATURES, FEATURE_ORDER, ORDINAL_MAPPINGS
from risk_engine.schemas import ClaimRiskInput


MODEL_BUNDLE_CACHE: dict | None = None
SCALER_CACHE = None
ENCODERS_CACHE: dict[str, dict[str, int]] | None = None
FEATURE_ORDER_CACHE: list[str] | None = None
ROOT = Path(__file__).resolve().parents[1]


def _artifact_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_model() -> dict:
    global MODEL_BUNDLE_CACHE
    if MODEL_BUNDLE_CACHE is not None:
        return MODEL_BUNDLE_CACHE

    model_path = _artifact_path(settings.ml_model_path)
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    with model_path.open("rb") as model_file:
        bundle = pickle.load(model_file)

    required_keys = {"model_name", "model", "feature_order"}
    if not isinstance(bundle, dict) or not required_keys.issubset(bundle.keys()):
        raise ValueError("SCHEMA_MISMATCH")

    MODEL_BUNDLE_CACHE = bundle
    return MODEL_BUNDLE_CACHE


def load_scaler():
    global SCALER_CACHE
    if SCALER_CACHE is not None:
        return SCALER_CACHE

    scaler_path = _artifact_path(settings.scaler_path)
    if not scaler_path.exists():
        raise FileNotFoundError(scaler_path)

    with scaler_path.open("rb") as scaler_file:
        scaler = pickle.load(scaler_file)

    if not hasattr(scaler, "transform"):
        raise ValueError("SCHEMA_MISMATCH")

    SCALER_CACHE = scaler
    return SCALER_CACHE


def load_encoders() -> dict[str, dict[str, int]]:
    global ENCODERS_CACHE
    if ENCODERS_CACHE is not None:
        return ENCODERS_CACHE

    encoders_path = _artifact_path(settings.encoders_path)
    if not encoders_path.exists():
        raise FileNotFoundError(encoders_path)

    with encoders_path.open("rb") as encoders_file:
        encoders = pickle.load(encoders_file)

    required_keys = {"claimant_gender", "incident_severity", "claimant_location"}
    if not isinstance(encoders, dict) or not required_keys.issubset(encoders.keys()):
        raise ValueError("SCHEMA_MISMATCH")

    ENCODERS_CACHE = encoders
    return ENCODERS_CACHE


def load_feature_order() -> list[str]:
    global FEATURE_ORDER_CACHE
    if FEATURE_ORDER_CACHE is not None:
        return FEATURE_ORDER_CACHE

    feature_order_path = _artifact_path(settings.feature_order_path)
    if not feature_order_path.exists():
        raise FileNotFoundError(feature_order_path)

    with feature_order_path.open("r", encoding="utf-8") as feature_file:
        feature_order = json.load(feature_file)

    if feature_order != FEATURE_ORDER:
        raise ValueError("SCHEMA_MISMATCH")

    FEATURE_ORDER_CACHE = feature_order
    return FEATURE_ORDER_CACHE


def _payload_to_dict(input_data: ClaimRiskInput | dict[str, Any]) -> dict[str, Any]:
    if isinstance(input_data, ClaimRiskInput):
        return input_data.model_dump()
    if isinstance(input_data, dict):
        return input_data
    raise ValueError("SCHEMA_MISMATCH")


def validate_payload(input_data: ClaimRiskInput | dict[str, Any]) -> ClaimRiskInput:
    payload_data = _payload_to_dict(input_data)
    missing_features = [feature for feature in FEATURE_ORDER if feature not in payload_data]
    if missing_features:
        raise ValueError("FEATURE_MISSING")

    try:
        return ClaimRiskInput(**payload_data)
    except Exception as exc:
        error_text = str(exc)
        if "Field required" in error_text:
            raise ValueError("FEATURE_MISSING") from exc
        raise ValueError("SCHEMA_MISMATCH") from exc


def _encode_feature(feature_name: str, value: Any, encoders: dict[str, dict[str, int]]) -> float:
    if feature_name in BOOLEAN_FEATURES:
        return float(int(bool(value)))
    if feature_name == "incident_severity":
        encoder = encoders["incident_severity"]
        if value not in encoder:
            raise ValueError("MODEL_INPUT_INVALID")
        return float(encoder[value])
    if feature_name in {"claimant_gender", "claimant_location"}:
        encoder = encoders[feature_name]
        if value not in encoder:
            raise ValueError("MODEL_INPUT_INVALID")
        return float(encoder[value])
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("MODEL_INPUT_INVALID") from exc


def build_feature_vector(input_data: ClaimRiskInput | dict[str, Any]) -> np.ndarray:
    payload = validate_payload(input_data)
    model_bundle = load_model()
    feature_order = load_feature_order()
    encoders = load_encoders()

    if model_bundle["feature_order"] != feature_order:
        raise ValueError("SCHEMA_MISMATCH")

    payload_data = payload.model_dump()
    encoded_values: list[float] = []
    for feature_name in feature_order:
        if feature_name not in payload_data:
            raise ValueError("FEATURE_MISSING")
        encoded_values.append(_encode_feature(feature_name, payload_data[feature_name], encoders))

    scaler = load_scaler()
    feature_frame = pd.DataFrame([encoded_values], columns=feature_order, dtype=float)
    scaled_vector = scaler.transform(feature_frame)
    return scaled_vector


def predict(input_data: ClaimRiskInput | dict[str, Any]) -> float:
    model_bundle = load_model()
    scaled_vector = build_feature_vector(input_data)
    model = model_bundle["model"]
    if not hasattr(model, "predict_proba"):
        raise ValueError("SCHEMA_MISMATCH")

    probability = float(model.predict_proba(scaled_vector)[0][1])
    return max(0.0, min(1.0, round(probability, 4)))
