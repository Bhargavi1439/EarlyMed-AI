from typing import Any, Dict, List


def generate_clinical_decision_support(
    disease_results: Dict[str, Any],
    shap_explanations: Dict[str, Any],
    overall_risk: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate structured, non-prescriptive clinical decision support insights.
    Strictly marked as AI-assisted research decision support (NOT medical advice).
    Avoids definitive diagnoses, prescribing medications, or modifying clinical therapies.
    """
    observations_by_disease = {}
    follow_up_recommendations = []

    for d_key, res in disease_results.items():
        if not res.get("evaluated") or res.get("probability") is None:
            continue

        d_name = res.get("disease", d_key.replace("_", " ").title())
        pct = res.get("probability_pct", 0)
        expl = shap_explanations.get(d_key, {})

        model_obs = []
        top_contribs = expl.get("top_contributions", [])
        for item in top_contribs[:3]:
            feat_lbl = item.get("label")
            direction = item.get("impact_direction")
            if direction == "higher_risk":
                model_obs.append(f"{feat_lbl} contributed towards a higher estimated risk output.")
            else:
                model_obs.append(f"{feat_lbl} contributed towards a lower or protective risk estimate.")

        if not model_obs:
            model_obs.append("Routine clinical biomarkers contributed to the multivariate model output.")

        observations_by_disease[d_name] = {
            "risk_percentage": pct,
            "risk_label": res.get("risk_label"),
            "model_name": res.get("model_name"),
            "observations": model_obs,
        }

    # Synthesize research-oriented suggested discussions
    follow_up_recommendations.append("Review relevant laboratory and clinical measurements with a qualified healthcare physician.")
    follow_up_recommendations.append("Correlate automated statistical risk estimates with longitudinal clinical history and examination.")

    score = overall_risk.get("score", 0)
    if score >= 70:
        follow_up_recommendations.append("Given elevated statistical risk markers across one or more evaluated domains, consider comprehensive clinical diagnostic evaluation.")
    elif score >= 40:
        follow_up_recommendations.append("Moderate statistical risk indicates borderline clinical parameters; routine preventive monitoring is suggested.")
    else:
        follow_up_recommendations.append("Clinical parameters currently reflect low overall statistical risk across evaluated models; routine screening schedule may be maintained.")

    disclaimer = (
        "AI-Assisted Research Decision Support Notice: This summary is generated from empirical machine learning "
        "models on research cohorts. It does NOT constitute medical advice, diagnostic determination, or treatment guidance. "
        "No medicines are prescribed or recommended. Clinical decisions must always be directed by licensed medical professionals."
    )

    return {
        "title": "AI-Assisted Research Decision Support",
        "observations_by_disease": observations_by_disease,
        "suggested_follow_up": follow_up_recommendations,
        "disclaimer": disclaimer,
    }
