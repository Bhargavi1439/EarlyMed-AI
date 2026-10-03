import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    DIABETES_MODELS_DIR,
    FEATURE_COLUMNS as DIABETES_COLS,
    HEART_FEATURE_COLUMNS as HEART_COLS,
    HEART_MODELS_DIR,
    KIDNEY_FEATURE_COLUMNS as KIDNEY_COLS,
    KIDNEY_MODELS_DIR,
    THYROID_FEATURE_COLUMNS as THYROID_COLS,
    THYROID_MODELS_DIR,
)
from src.preprocessing import InvalidZeroToNaN  # noqa: F401 (for joblib unpickling)


class MultiDiseasePredictor:
    """
    Unified predictor for Diabetes, Heart Disease, and Chronic Kidney Disease.
    Uses exact training preprocessors, pipelines, and models.
    """

    def __init__(self):
        # 1. Load Diabetes
        self.diabetes_prep = joblib.load(DIABETES_MODELS_DIR / "preprocessor.joblib")
        self.diabetes_model = joblib.load(DIABETES_MODELS_DIR / "model.joblib")
        self.diabetes_meta = json.loads((DIABETES_MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))

        # 2. Load Heart Disease
        self.heart_prep = joblib.load(HEART_MODELS_DIR / "preprocessor.joblib")
        self.heart_model = joblib.load(HEART_MODELS_DIR / "model.joblib")
        self.heart_meta = json.loads((HEART_MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))

        # 3. Load Kidney Disease
        self.kidney_prep = joblib.load(KIDNEY_MODELS_DIR / "preprocessor.joblib")
        self.kidney_model = joblib.load(KIDNEY_MODELS_DIR / "model.joblib")
        self.kidney_meta = json.loads((KIDNEY_MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))

        # 4. Load Thyroid Disease
        if (THYROID_MODELS_DIR / "preprocessor.joblib").exists():
            self.thyroid_prep = joblib.load(THYROID_MODELS_DIR / "preprocessor.joblib")
            self.thyroid_model = joblib.load(THYROID_MODELS_DIR / "model.joblib")
            self.thyroid_meta = json.loads((THYROID_MODELS_DIR / "metadata.json").read_text(encoding="utf-8"))
        else:
            self.thyroid_prep = None
            self.thyroid_model = None
            self.thyroid_meta = {}

    def predict_diabetes(self, raw_params: Dict[str, Any], readiness: dict) -> Dict[str, Any]:
        if not readiness.get("ready", False):
            return {
                "evaluated": False,
                "status": "insufficient_relevant_information",
                "disease": "Diabetes",
                "risk_label": "Not Evaluated",
                "probability": None,
                "probability_pct": None,
                "reason": readiness.get("reason", "Required glucose measurement missing."),
                "model_name": self.diabetes_meta.get("selected_model", "XGBoost"),
                "features_found": readiness.get("found_features", []),
                "features_missing": readiness.get("missing_features", []),
                "feature_coverage": readiness.get("coverage_str", "0"),
                "imputed_features": [],
            }

        # Build feature vector with clinical proxy derivation
        glucose = raw_params.get("glucose", {}).get("normalized_value", np.nan)
        if pd.isna(glucose):
            if "glucose_eag" in raw_params and raw_params["glucose_eag"].get("normalized_value") is not None:
                glucose = raw_params["glucose_eag"]["normalized_value"]
            elif "hba1c" in raw_params and raw_params["hba1c"].get("normalized_value") is not None:
                # Nathan et al. formula: eAG = 28.7 * HbA1c - 46.7
                glucose = round(28.7 * float(raw_params["hba1c"]["normalized_value"]) - 46.7, 1)

        diastolic_bp = raw_params.get("diastolic_bp", {}).get("normalized_value", np.nan)
        bmi = raw_params.get("bmi", {}).get("normalized_value", np.nan)
        insulin = raw_params.get("insulin", {}).get("normalized_value", np.nan)
        age = raw_params.get("age", {}).get("normalized_value", np.nan)
        pregnancies = raw_params.get("pregnancies", {}).get("normalized_value", 0.0 if raw_params.get("sex", {}).get("normalized_value") == 1 else np.nan)
        skin_thickness = raw_params.get("skin_thickness", {}).get("normalized_value", np.nan)
        dpf = raw_params.get("diabetes_pedigree", {}).get("normalized_value", np.nan)

        feature_dict = {
            "Pregnancies": pregnancies,
            "Glucose": glucose,
            "BloodPressure": diastolic_bp,
            "SkinThickness": skin_thickness,
            "Insulin": insulin,
            "BMI": bmi,
            "DiabetesPedigreeFunction": dpf,
            "Age": age,
        }

        imputed = [k for k, v in feature_dict.items() if pd.isna(v)]
        df_row = pd.DataFrame([feature_dict])[DIABETES_COLS]
        processed = self.diabetes_prep.transform(df_row)

        prob = float(self.diabetes_model.predict_proba(processed)[0, 1])
        pct = round(prob * 100, 1)
        pred_class = int(prob >= 0.5)

        return {
            "evaluated": True,
            "status": "prediction_available",
            "disease": "Diabetes",
            "predicted_class": pred_class,
            "risk_label": "risk_detected" if pred_class == 1 else "no_risk_detected",
            "probability": prob,
            "probability_pct": pct,
            "reason": readiness.get("reason", "Model prediction available."),
            "model_name": self.diabetes_meta.get("selected_model", "XGBoost").replace("_", " ").title(),
            "features_used": feature_dict,
            "features_found": readiness.get("found_features", []),
            "features_missing": readiness.get("missing_features", []),
            "feature_coverage": readiness.get("coverage_str", "0"),
            "imputed_features": imputed,
            "processed_vector": processed[0],
            "feature_names": DIABETES_COLS,
        }

    def predict_heart(self, raw_params: Dict[str, Any], readiness: dict) -> Dict[str, Any]:
        if not readiness.get("ready", False):
            return {
                "evaluated": False,
                "status": "insufficient_relevant_information",
                "disease": "Heart Disease",
                "risk_label": "Not Evaluated",
                "probability": None,
                "probability_pct": None,
                "reason": readiness.get("reason", "Insufficient cardiovascular markers in report."),
                "model_name": self.heart_meta.get("selected_model", "Random Forest"),
                "features_found": readiness.get("found_features", []),
                "features_missing": readiness.get("missing_features", []),
                "feature_coverage": readiness.get("coverage_str", "0"),
                "imputed_features": [],
            }

        age = raw_params.get("age", {}).get("normalized_value", np.nan)
        sex = raw_params.get("sex", {}).get("normalized_value", np.nan)
        cp = raw_params.get("chest_pain", {}).get("normalized_value", np.nan)
        trestbps = raw_params.get("systolic_bp", {}).get("normalized_value", np.nan)
        chol = raw_params.get("cholesterol", {}).get("normalized_value", np.nan)

        # FBS: 1 if fasting glucose > 120, else 0
        glucose_val = raw_params.get("glucose", {}).get("normalized_value")
        fbs = 1.0 if glucose_val is not None and glucose_val > 120 else (0.0 if glucose_val is not None else np.nan)

        thalach = raw_params.get("heart_rate", {}).get("normalized_value", np.nan)

        feature_dict = {
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": np.nan,
            "thalach": thalach,
            "exang": np.nan,
            "oldpeak": np.nan,
            "slope": np.nan,
            "ca": np.nan,
            "thal": np.nan,
        }

        imputed = [k for k, v in feature_dict.items() if pd.isna(v)]
        df_row = pd.DataFrame([feature_dict])[HEART_COLS]
        processed = self.heart_prep.transform(df_row)

        prob = float(self.heart_model.predict_proba(processed)[0, 1])
        pct = round(prob * 100, 1)
        pred_class = int(prob >= 0.5)

        return {
            "evaluated": True,
            "status": "prediction_available",
            "disease": "Heart Disease",
            "predicted_class": pred_class,
            "risk_label": "risk_detected" if pred_class == 1 else "no_risk_detected",
            "probability": prob,
            "probability_pct": pct,
            "reason": readiness.get("reason", "Model prediction available."),
            "model_name": self.heart_meta.get("selected_model", "Random Forest").replace("_", " ").title(),
            "features_used": feature_dict,
            "features_found": readiness.get("found_features", []),
            "features_missing": readiness.get("missing_features", []),
            "feature_coverage": readiness.get("coverage_str", "0"),
            "imputed_features": imputed,
            "processed_vector": processed[0],
            "feature_names": HEART_COLS,
        }

    def predict_kidney(self, raw_params: Dict[str, Any], readiness: dict) -> Dict[str, Any]:
        if not readiness.get("ready", False):
            return {
                "evaluated": False,
                "status": "insufficient_relevant_information",
                "disease": "Chronic Kidney Disease",
                "risk_label": "Not Evaluated",
                "probability": None,
                "probability_pct": None,
                "reason": readiness.get("reason", "Insufficient information to evaluate CKD: Creatinine/Urea not found."),
                "model_name": self.kidney_meta.get("selected_model", "Random Forest"),
                "features_found": readiness.get("found_features", []),
                "features_missing": readiness.get("missing_features", []),
                "feature_coverage": readiness.get("coverage_str", "0"),
                "imputed_features": [],
            }

        age = raw_params.get("age", {}).get("normalized_value", np.nan)
        bp = raw_params.get("systolic_bp", {}).get("normalized_value", np.nan)
        bgr = raw_params.get("glucose", {}).get("normalized_value", np.nan)
        if pd.isna(bgr):
            if "glucose_eag" in raw_params and raw_params["glucose_eag"].get("normalized_value") is not None:
                bgr = raw_params["glucose_eag"]["normalized_value"]
            elif "hba1c" in raw_params and raw_params["hba1c"].get("normalized_value") is not None:
                bgr = round(28.7 * float(raw_params["hba1c"]["normalized_value"]) - 46.7, 1)

        bu = raw_params.get("urea", {}).get("normalized_value", np.nan)
        if pd.isna(bu) and "bun" in raw_params and raw_params["bun"].get("normalized_value") is not None:
            bu = round(float(raw_params["bun"]["normalized_value"]) * 2.14, 1)

        sc = raw_params.get("creatinine", {}).get("normalized_value", np.nan)
        hemo = raw_params.get("hemoglobin", {}).get("normalized_value", np.nan)
        pcv = raw_params.get("packed_cell_volume", {}).get("normalized_value", np.nan)
        wc = raw_params.get("wbc", {}).get("normalized_value", np.nan)
        rc = raw_params.get("rbc", {}).get("normalized_value", np.nan)
        al = raw_params.get("albumin", {}).get("normalized_value", np.nan)
        sg = raw_params.get("specific_gravity", {}).get("normalized_value", np.nan)

        # Hypertension flag: 1 if systolic > 140 or diastolic > 90
        sys_bp = raw_params.get("systolic_bp", {}).get("normalized_value")
        dia_bp = raw_params.get("diastolic_bp", {}).get("normalized_value")
        htn = 1.0 if (sys_bp and sys_bp >= 140) or (dia_bp and dia_bp >= 90) else (0.0 if sys_bp or dia_bp else np.nan)

        # Diabetes Mellitus flag: 1 if bgr > 140 or hba1c > 6.5
        hba1c = raw_params.get("hba1c", {}).get("normalized_value")
        dm = 1.0 if (bgr and bgr >= 140) or (hba1c and hba1c >= 6.5) else (0.0 if bgr or hba1c else np.nan)

        feature_dict = {
            "age": age,
            "bp": bp,
            "bgr": bgr,
            "bu": bu,
            "sc": sc,
            "hemo": hemo,
            "pcv": pcv,
            "wc": wc,
            "rc": rc,
            "al": al,
            "sg": sg,
            "htn": htn,
            "dm": dm,
        }

        imputed = [k for k, v in feature_dict.items() if pd.isna(v)]
        df_row = pd.DataFrame([feature_dict])[KIDNEY_COLS]
        processed = self.kidney_prep.transform(df_row)

        prob = float(self.kidney_model.predict_proba(processed)[0, 1])
        pct = round(prob * 100, 1)
        pred_class = int(prob >= 0.5)

        return {
            "evaluated": True,
            "status": "prediction_available",
            "disease": "Chronic Kidney Disease",
            "predicted_class": pred_class,
            "risk_label": "risk_detected" if pred_class == 1 else "no_risk_detected",
            "probability": prob,
            "probability_pct": pct,
            "reason": readiness.get("reason", "Model prediction available."),
            "model_name": self.kidney_meta.get("selected_model", "Random Forest").replace("_", " ").title(),
            "features_used": feature_dict,
            "features_found": readiness.get("found_features", []),
            "features_missing": readiness.get("missing_features", []),
            "feature_coverage": readiness.get("coverage_str", "0"),
            "imputed_features": imputed,
            "processed_vector": processed[0],
            "feature_names": KIDNEY_COLS,
        }

    def predict_thyroid(self, raw_params: Dict[str, Any], readiness: dict) -> Dict[str, Any]:
        if not self.thyroid_model or not readiness.get("ready", False):
            return {
                "evaluated": False,
                "status": "insufficient_relevant_information",
                "disease": "Thyroid Cancer Recurrence",
                "risk_label": "Not Evaluated",
                "probability": None,
                "probability_pct": None,
                "reason": readiness.get("reason", "Insufficient information to evaluate Thyroid risk."),
                "model_name": self.thyroid_meta.get("selected_model", "Random Forest").replace("_", " ").title(),
                "features_found": readiness.get("found_features", []),
                "features_missing": readiness.get("missing_features", []),
                "feature_coverage": readiness.get("coverage_str", "0"),
                "imputed_features": [],
            }

        # Build feature dict handling categorical mapping properly
        # The parser needs to supply these exact string values or we set sensible defaults for missing
        feature_dict = {
            "Age": raw_params.get("age", {}).get("normalized_value", np.nan),
            "Gender": raw_params.get("sex", {}).get("original_text", "F"),  # Defaulting to female if missing
            "Smoking": raw_params.get("smoking", {}).get("original_text", "No"),
            "Hx Smoking": raw_params.get("hx_smoking", {}).get("original_text", "No"),
            "Hx Radiothreapy": raw_params.get("hx_radiotherapy", {}).get("original_text", "No"),
            "Thyroid Function": raw_params.get("thyroid_function", {}).get("original_text", "Euthyroid"),
            "Physical Examination": raw_params.get("physical_examination", {}).get("original_text", "Normal"),
            "Adenopathy": raw_params.get("adenopathy", {}).get("original_text", "No"),
            "Pathology": raw_params.get("pathology", {}).get("original_text", "Papillary"),
            "Focality": raw_params.get("focality", {}).get("original_text", "Uni-Focal"),
            "Risk": raw_params.get("risk", {}).get("original_text", "Low"),
            "T": raw_params.get("t_stage", {}).get("original_text", "T1a"),
            "N": raw_params.get("n_stage", {}).get("original_text", "N0"),
            "M": raw_params.get("m_stage", {}).get("original_text", "M0"),
            "Stage": raw_params.get("stage", {}).get("original_text", "I"),
            "Response": raw_params.get("response", {}).get("original_text", "Excellent"),
        }
        
        # Gender map 0: F, 1: M since parser returns 1 for M
        if raw_params.get("sex", {}).get("normalized_value") == 1:
            feature_dict["Gender"] = "M"

        # Missing values handling
        for k in feature_dict:
            if pd.isna(feature_dict[k]):
                if k == "Age":
                    feature_dict[k] = 40  # median/mean substitute
                else:
                    feature_dict[k] = "Unknown"

        imputed = [] # We're defaulting strings so technically all imputed if unknown
        df_row = pd.DataFrame([feature_dict])[THYROID_COLS]
        processed = self.thyroid_prep.transform(df_row)

        prob = float(self.thyroid_model.predict_proba(processed)[0, 1])
        pct = round(prob * 100, 1)
        pred_class = int(prob >= 0.5)

        return {
            "evaluated": True,
            "status": "prediction_available",
            "disease": "Thyroid Cancer Recurrence",
            "predicted_class": pred_class,
            "risk_label": "risk_detected" if pred_class == 1 else "no_risk_detected",
            "probability": prob,
            "probability_pct": pct,
            "reason": readiness.get("reason", "Model prediction available."),
            "model_name": self.thyroid_meta.get("selected_model", "Random Forest").replace("_", " ").title(),
            "features_used": feature_dict,
            "features_found": readiness.get("found_features", []),
            "features_missing": readiness.get("missing_features", []),
            "feature_coverage": readiness.get("coverage_str", "0"),
            "imputed_features": imputed,
            "processed_vector": processed[0],
            "feature_names": getattr(self.thyroid_model, "feature_names_in_", THYROID_COLS),
        }

    def compute_overall_health_risk_index(self, disease_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate unified Overall Health Risk Index (0–100).
        Strictly labeled as research/prototype risk score, not a medical diagnosis.
        """
        valid_probs = [
            res["probability"] for res in disease_results.values()
            if res.get("evaluated") and res.get("probability") is not None
        ]

        if not valid_probs:
            return {
                "score": 0,
                "category": "Insufficient Data",
                "description": "Insufficient clinical parameters to calculate overall health risk index.",
            }

        # Weighted composite score emphasizing highest individual risk factor
        mean_risk = float(np.mean(valid_probs))
        max_risk = float(np.max(valid_probs))
        composite = 0.6 * max_risk + 0.4 * mean_risk
        score = int(round(composite * 100))
        score = min(100, max(0, score))

        if score < 40:
            category = "Lower estimated risk"
            badge_class = "risk-low"
        elif score < 70:
            category = "Moderate estimated risk"
            badge_class = "risk-medium"
        else:
            category = "Higher estimated risk"
            badge_class = "risk-high"

        return {
            "score": score,
            "category": category,
            "badge_class": badge_class,
            "eval_count": len(valid_probs),
            "total_diseases": len(disease_results),
            "disclaimer": "This score is an academic research prototype estimate synthesized from experimental models. It is not a clinical diagnosis.",
        }

    def predict_all(self, raw_params: Dict[str, Any], readiness_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Run all disease predictions and calculate overall index."""
        diabetes_res = self.predict_diabetes(raw_params, readiness_dict.get("diabetes", {}))
        heart_res = self.predict_heart(raw_params, readiness_dict.get("heart_disease", {}))
        kidney_res = self.predict_kidney(raw_params, readiness_dict.get("kidney_disease", {}))
        thyroid_res = self.predict_thyroid(raw_params, readiness_dict.get("thyroid_disease", {}))

        disease_results = {
            "diabetes": diabetes_res,
            "heart_disease": heart_res,
            "kidney_disease": kidney_res,
            "thyroid_disease": thyroid_res,
        }

        overall_index = self.compute_overall_health_risk_index(disease_results)

        return {
            "disease_results": disease_results,
            "overall_health_risk_index": overall_index,
        }
