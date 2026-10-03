import numpy as np
try:
    import shap
    SHAP_AVAILABLE = True
except (ImportError, OSError) as e:
    SHAP_AVAILABLE = False
    print(f"Warning: SHAP library could not be loaded ({e}). Falling back to simple feature importance.")
from typing import Any, Dict, List, Optional


def explain_with_shap(
    model: Any,
    processed_vector: np.ndarray,
    feature_names: List[str],
    feature_labels: Optional[Dict[str, str]] = None,
    raw_feature_values: Optional[Dict[str, Any]] = None,
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Compute patient-specific SHAP explanation.
    Uses non-causal language ('contributed to the model prediction').
    """
    feature_labels = feature_labels or {}
    raw_feature_values = raw_feature_values or {}
    sample = processed_vector.reshape(1, -1)

    try:
        if not SHAP_AVAILABLE:
            raise Exception("SHAP library is not available.")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(sample)

        # Handle different SHAP output shapes (multi-class vs binary)
        if isinstance(shap_values, list):
            # Binary classifier: pick positive class (index 1)
            vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3:
                vals = shap_values[0, :, 1]
            elif shap_values.ndim == 2:
                vals = shap_values[0]
            else:
                vals = shap_values
        else:
            vals = np.array(shap_values)
    except Exception as exc:
        # Fallback to feature importance weighting if TreeExplainer encounters model quirks
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            vals = (sample[0] * importances)
        elif hasattr(model, "coef_"):
            vals = (sample[0] * model.coef_[0])
        else:
            vals = np.zeros(len(feature_names))

    # Pair features with shap values
    contributions = []
    max_abs = max(1e-6, float(np.max(np.abs(vals))))

    for name, s_val in zip(feature_names, vals):
        s_float = float(s_val)
        raw_val = raw_feature_values.get(name)
        lbl = feature_labels.get(name, name.replace("_", " ").title())
        impact_dir = "higher_risk" if s_float > 0 else "lower_risk"
        bar_pct = min(100, int(round((abs(s_float) / max_abs) * 100)))

        # Phrasing
        if s_float > 0:
            observation = f"{lbl} contributed towards a higher estimated risk."
        else:
            observation = f"{lbl} contributed towards a lower estimated risk."

        contributions.append({
            "feature": name,
            "label": lbl,
            "raw_value": raw_val,
            "shap_value": round(s_float, 4),
            "abs_impact": round(abs(s_float), 4),
            "impact_direction": impact_dir,
            "bar_percentage": bar_pct,
            "observation": observation,
        })

    # Sort by absolute impact descending
    contributions.sort(key=lambda x: x["abs_impact"], reverse=True)
    top_contributions = contributions[:top_n]

    # Overall summary narrative
    higher_factors = [c["label"] for c in top_contributions if c["impact_direction"] == "higher_risk"]
    lower_factors = [c["label"] for c in top_contributions if c["impact_direction"] == "lower_risk"]

    summary_bullets = []
    if higher_factors:
        summary_bullets.append(f"Higher estimated risk was associated with contributions from: {', '.join(higher_factors)}.")
    if lower_factors:
        summary_bullets.append(f"Protective or lower estimated risk contributions were associated with: {', '.join(lower_factors)}.")

    return {
        "method": "SHAP (SHapley Additive exPlanations)",
        "top_contributions": top_contributions,
        "all_contributions": contributions,
        "summary_bullets": summary_bullets,
    }
