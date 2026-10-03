import numpy as np
from typing import Any, Dict, List, Optional

try:
    from lime.lime_tabular import LimeTabularExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False


def explain_with_lime(
    model: Any,
    processed_vector: np.ndarray,
    feature_names: List[str],
    feature_labels: Optional[Dict[str, str]] = None,
    raw_feature_values: Optional[Dict[str, Any]] = None,
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Compute local LIME surrogate explanation for the patient's record.
    """
    feature_labels = feature_labels or {}
    raw_feature_values = raw_feature_values or {}

    if not LIME_AVAILABLE:
        return {
            "method": "LIME (Local Interpretable Model-agnostic Explanations)",
            "available": False,
            "rules": [],
            "message": "LIME library not available.",
        }

    try:
        # Create background distribution around the test sample for local perturbation
        np.random.seed(42)
        n_dim = len(feature_names)
        background = np.random.normal(loc=0.0, scale=1.0, size=(100, n_dim))

        explainer = LimeTabularExplainer(
            training_data=background,
            feature_names=feature_names,
            class_names=["Lower Risk", "Higher Risk"],
            mode="classification",
            random_state=42,
        )

        def predict_fn(x):
            if hasattr(model, "predict_proba"):
                return model.predict_proba(x)
            preds = model.predict(x)
            return np.vstack([1 - preds, preds]).T

        exp = explainer.explain_instance(
            data_row=processed_vector,
            predict_fn=predict_fn,
            num_features=top_n,
            labels=(1,),
        )

        explanation_list = exp.as_list(label=1)
        rules = []
        max_abs = max([abs(weight) for _, weight in explanation_list] or [1e-6])

        for condition, weight in explanation_list:
            # Map condition feature name to human label
            clean_condition = condition
            for fname in feature_names:
                if fname in clean_condition:
                    lbl = feature_labels.get(fname, fname)
                    clean_condition = clean_condition.replace(fname, lbl)
                    break

            rules.append({
                "condition": clean_condition,
                "weight": round(float(weight), 4),
                "abs_weight": round(abs(float(weight)), 4),
                "impact_direction": "higher_risk" if weight > 0 else "lower_risk",
                "bar_percentage": min(100, int(round((abs(float(weight)) / max_abs) * 100))),
            })

        return {
            "method": "LIME (Local Interpretable Model-agnostic Explanations)",
            "available": True,
            "rules": rules,
            "message": "Local surrogate rules computed successfully.",
        }
    except Exception as exc:
        return {
            "method": "LIME (Local Interpretable Model-agnostic Explanations)",
            "available": False,
            "rules": [],
            "message": f"LIME local explanation note: {str(exc)}",
        }
