import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from risk_engine.feature_config import FEATURE_ORDER
from risk_engine.ml_model import load_encoders, load_feature_order, load_model, load_scaler


def _collect_model_columns() -> set[str]:
    source = (ROOT / "app" / "models.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    claim_fields: set[str] = set()
    in_claim_class = False
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Claim":
            in_claim_class = True
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    claim_fields.add(item.target.id)
            break
    if not in_claim_class:
        raise AssertionError("Claim model not found")
    return claim_fields


def _collect_schema_fields() -> set[str]:
    source = (ROOT / "app" / "schemas" / "claim.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    fields: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ClaimSubmitResponse":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.add(item.target.id)
            break
    if not fields:
        raise AssertionError("ClaimSubmitResponse not found")
    return fields


def main() -> None:
    model_fields = _collect_model_columns()
    schema_fields = _collect_schema_fields()
    feature_order = load_feature_order()
    model_bundle = load_model()
    scaler = load_scaler()
    encoders = load_encoders()

    assert schema_fields.issubset(model_fields), "schemas to models mismatch"
    assert set(FEATURE_ORDER).issubset(model_fields), "feature_order has missing model fields"
    assert feature_order == FEATURE_ORDER, "feature_order mismatch"
    assert model_bundle["feature_order"] == FEATURE_ORDER, "saved model feature_order mismatch"
    assert set(encoders.keys()) == {"claimant_gender", "incident_severity", "claimant_location"}, "encoders mismatch"
    assert hasattr(scaler, "transform"), "scaler invalid"

    artifact_paths = [
        ROOT / settings.ml_model_path,
        ROOT / settings.scaler_path,
        ROOT / settings.encoders_path,
        ROOT / settings.feature_order_path,
    ]
    for artifact_path in artifact_paths:
        assert artifact_path.exists(), f"missing artifact: {artifact_path}"

    artifact_names = sorted(path.name for path in (ROOT / "risk_engine" / "artifacts").iterdir() if path.is_file())
    assert artifact_names == ["best_model.pkl", "encoders.pkl", "feature_order.json", "scaler.pkl"], artifact_names

    print(json.dumps({"schema_sync": True, "artifacts": artifact_names}, indent=2))


if __name__ == "__main__":
    main()
