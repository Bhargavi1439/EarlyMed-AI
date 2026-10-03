from typing import Any, Dict, List, Tuple
from utils.medical_parser import PARAMETER_METADATA


def validate_extracted_data(extracted_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate extracted medical parameters before prediction.
    Checks:
    - Impossible ranges / physiological limits
    - Missing values for specific disease models
    - Model readiness for Diabetes, Heart Disease, and Kidney Disease
    Never fabricates values.
    """
    warnings = []
    flags = []
    validated_params = {}

    for key, item in extracted_params.items():
        norm_val = item.get("normalized_value")
        meta = PARAMETER_METADATA.get(key)
        if meta and "range" in meta and norm_val is not None:
            min_v, max_v = meta["range"]
            if norm_val < min_v or norm_val > max_v:
                warnings.append(
                    f"{meta['label']} value of {norm_val} {item.get('standard_unit')} is outside the expected physiological reference range ({min_v}–{max_v})."
                )
                flags.append(key)

        validated_params[key] = item

    # ── Check Disease Model Readiness ────────────────────────────────────────

    # Empirical Minimum Feature Thresholds
    MIN_FEATURES = {
        "diabetes": 3,
        "heart_disease": 4,
        "kidney_disease": 3,
    }

    # 1. Diabetes Readiness
    # Primary model features + clinical surrogates (HbA1c, PPBS, eAG, inferred male parity)
    is_male = extracted_params.get("sex", {}).get("normalized_value") == 1
    diabetes_keys = ["glucose", "diastolic_bp", "bmi", "insulin", "age", "pregnancies", "skin_thickness", "diabetes_pedigree", "hba1c", "glucose_pp", "glucose_eag"]
    diabetes_found = [k for k in diabetes_keys if k in extracted_params]
    if is_male and "pregnancies" not in diabetes_found:
        diabetes_found.append("pregnancies")
    
    diabetes_missing = [k for k in ["glucose", "diastolic_bp", "bmi", "insulin", "age", "pregnancies", "skin_thickness", "diabetes_pedigree"] if k not in diabetes_found]
    
    # Validation policy: Minimum 3 features, must include glucose or HbA1c
    has_glucose = ("glucose" in extracted_params and extracted_params["glucose"].get("normalized_value") is not None) or \
                  ("hba1c" in extracted_params and extracted_params["hba1c"].get("normalized_value") is not None)
    diabetes_ready = has_glucose and len(diabetes_found) >= MIN_FEATURES["diabetes"]
    diabetes_reason = (
        f"Validation policy satisfied (found {len(diabetes_found)} relevant diabetic indicators)."
        if diabetes_ready
        else f"Insufficient relevant information (Validated minimum: {MIN_FEATURES['diabetes']} features including Glucose or HbA1c)."
    )

    # 2. Heart Disease Readiness
    full_heart_keys = ["age", "sex", "chest_pain", "systolic_bp", "cholesterol", "glucose", "restecg", "heart_rate", "exang", "oldpeak", "slope", "ca", "thal"]
    heart_clinical_keys = ["age", "sex", "chest_pain", "systolic_bp", "cholesterol", "glucose", "heart_rate", "hdl", "ldl", "triglycerides", "vldl", "non_hdl"]
    heart_found = [k for k in full_heart_keys if k in extracted_params]
    for extra_lipid in ["hdl", "ldl", "triglycerides", "vldl", "non_hdl"]:
        if extra_lipid in extracted_params and extra_lipid not in heart_found:
            heart_found.append(extra_lipid)

    heart_missing = [k for k in full_heart_keys if k not in extracted_params]
    
    # Validation policy: Minimum 4 features (e.g. Age, Sex, Cholesterol/Lipids, Glucose/BP)
    heart_ready = len(heart_found) >= MIN_FEATURES["heart_disease"]
    heart_reason = (
        f"Validation policy satisfied (found {len(heart_found)} relevant cardiovascular markers)."
        if heart_ready
        else f"Prediction available when minimum cardiovascular markers are present (Found {len(heart_found)}, Validated minimum: {MIN_FEATURES['heart_disease']} features)."
    )

    # 3. Kidney Disease (CKD) Readiness
    renal_keys = ["age", "systolic_bp", "glucose", "urea", "creatinine", "hemoglobin", "packed_cell_volume", "wbc", "rbc", "albumin", "specific_gravity", "egfr", "bun", "uric_acid"]
    renal_found = [k for k in renal_keys if k in extracted_params]
    renal_missing = [k for k in ["age", "systolic_bp", "glucose", "urea", "creatinine", "hemoglobin", "packed_cell_volume", "wbc", "rbc", "albumin", "specific_gravity"] if k not in renal_found]
    
    # Validation policy: Minimum 3 features (e.g. Creatinine/Urea/eGFR/Age/Specific Gravity)
    kidney_ready = len(renal_found) >= MIN_FEATURES["kidney_disease"]
    kidney_reason = (
        f"Validation policy satisfied (found {len(renal_found)} relevant renal markers)."
        if kidney_ready
        else f"Prediction available when minimum renal markers are present (Found {len(renal_found)}, Validated minimum: {MIN_FEATURES['kidney_disease']} features)."
    )

    model_readiness = {
        "diabetes": {
            "ready": diabetes_ready,
            "found_features": diabetes_found,
            "missing_features": diabetes_missing,
            "reason": diabetes_reason,
            "coverage_str": f"{len(diabetes_found)}/8"
        },
        "heart_disease": {
            "ready": heart_ready,
            "found_features": heart_found,
            "missing_features": heart_missing,
            "reason": heart_reason,
            "coverage_str": f"{len(heart_found)}/13"
        },
        "kidney_disease": {
            "ready": kidney_ready,
            "found_features": renal_found,
            "missing_features": renal_missing,
            "reason": kidney_reason,
            "coverage_str": f"{len(renal_found)}/11"
        },
    }

    return {
        "is_valid": True,
        "warnings": warnings,
        "flags": flags,
        "model_readiness": model_readiness,
        "parameters": validated_params,
    }
