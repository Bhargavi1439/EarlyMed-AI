import json
import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename

import numpy as np
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for, flash

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import db
from explainability.lime_explainer import explain_with_lime
from explainability.shap_explainer import explain_with_shap
from src.config import (
    DIABETES_MODELS_DIR,
    FEATURE_COLUMNS,
    FEATURE_LABELS,
    HEART_DATA_PATH,
    HEART_FEATURE_COLUMNS,
    HEART_FEATURE_LABELS,
    HEART_MODELS_DIR,
    KIDNEY_DATA_PATH,
    KIDNEY_FEATURE_LABELS,
    KIDNEY_MODELS_DIR,
    RAW_DATA_PATH,
    RESULTS_DIR,
    THYROID_MODELS_DIR,
    THYROID_FEATURE_COLUMNS,
    THYROID_FEATURE_LABELS,
    THYROID_DATA_PATH,
)

from src.decision_support import generate_clinical_decision_support
from src.multi_disease_predictor import MultiDiseasePredictor
from utils.medical_parser import parse_medical_report_text
from utils.pdf_extractor import extract_document_content
from utils.validator import validate_extracted_data

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
app.secret_key = "healthcare-disease-prediction-secret-key"

UPLOAD_FOLDER = ROOT / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR = ROOT / "data" / "sample_reports"

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}

_predictor = None


def get_multi_predictor():
    global _predictor
    if _predictor is None:
        _predictor = MultiDiseasePredictor()
    return _predictor


@app.route("/")
def index():
    """First / Home Page - Strictly preserved UI layout and design."""
    return render_template("index.html")


@app.route("/predict", methods=["GET"])
def predict():
    """
    Medical Report Upload Workflow.
    Replaces the previous manual 8-input form completely.
    """
    error = request.args.get("error")
    return render_template("predict.html", error=error)


@app.route("/upload", methods=["POST"])
def upload_report():
    """Handle uploaded medical report document (PDF or Image)."""
    if "report_file" not in request.files:
        return redirect(url_for("predict", error="No file selected for upload."))

    file = request.files["report_file"]
    if file.filename == "":
        return redirect(url_for("predict", error="Please choose a valid file."))

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return redirect(url_for("predict", error=f"Unsupported format '{ext}'. Please upload a PDF or image (PNG, JPG)."))

    filename = secure_filename(file.filename)
    if not filename:
        filename = f"uploaded_report{ext}"

    save_path = UPLOAD_FOLDER / filename
    file.save(str(save_path))

    return process_document_and_render_review(save_path, filename)


@app.route("/demo/<sample_name>")
def load_demo_report(sample_name):
    """Load one-click demonstration report for quick evaluation during testing/viva."""
    mapping = {
        "diabetic": SAMPLE_DIR / "Patient_Medical_Report.pdf",
        "normal": SAMPLE_DIR / "Patient_Normal_Report.pdf",
        "image": SAMPLE_DIR / "Patient_Report_Image.png",
    }
    target_path = mapping.get(sample_name, SAMPLE_DIR / "Patient_Medical_Report.pdf")
    if not target_path.exists():
        return redirect(url_for("predict", error=f"Demo file {sample_name} not found."))

    return process_document_and_render_review(target_path, target_path.name)


def process_document_and_render_review(file_path: Path, display_name: str):
    """
    Extract text from PDF/image, parse medical parameters, validate bounds,
    save report record to database, and render extracted_data review preview.
    """
    try:
        doc_info = extract_document_content(file_path)
    except Exception as exc:
        return redirect(url_for("predict", error=f"Document extraction error: {str(exc)}"))

    if not doc_info["text"].strip() and not doc_info.get("warnings"):
        return redirect(
            url_for("predict", error="The uploaded document contains no readable text or characters.")
        )

    # Parse clinical parameters from text
    print(f"[PDF Extraction] Document received: {display_name} ({doc_info['file_size_kb']} KB, {doc_info['doc_type']})")
    print(f"[PDF Extraction] Raw text extracted: {len(doc_info['text'])} characters")
    if doc_info["text"]:
        print(f"[PDF Extraction] First 300 chars of extracted text:\n{doc_info['text'][:300]}\n---")

    parser_output = parse_medical_report_text(doc_info["text"])
    extracted_params = parser_output["extracted_parameters"]
    fields_missing = parser_output["fields_missing"]
    print(f"[Parser] Identified {len(extracted_params)} clinical parameters: {list(extracted_params.keys())}")

    # Validate against physiological boundaries and determine disease model readiness
    validation_output = validate_extracted_data(extracted_params)

    # Save report and extracted biomarkers into SQLite database
    report_id = db.save_report_and_extraction(
        filename=display_name,
        file_type=doc_info["doc_type"],
        file_size_kb=doc_info["file_size_kb"],
        extracted_params=extracted_params,
    )

    report_meta = {
        "file_name": display_name,
        "file_size_kb": doc_info["file_size_kb"],
        "ocr_used": doc_info["ocr_used"],
        "doc_type": doc_info["doc_type"],
    }

    combined_warnings = doc_info.get("warnings", []) + validation_output.get("warnings", [])

    return render_template(
        "extracted_data.html",
        report_id=report_id,
        report_meta=report_meta,
        extracted_parameters=extracted_params,
        parameters_json=json.dumps(extracted_params),
        fields_missing=fields_missing,
        readiness=validation_output["model_readiness"],
        warnings=combined_warnings,
        flagged_keys=validation_output.get("flags", []),
    )


@app.route("/run_prediction", methods=["POST"])
def run_prediction():
    """
    Execute multi-disease ML predictions, calculate Health Risk Index,
    compute local SHAP and LIME explanations, and render final results dashboard.
    """
    params_json = request.form.get("verified_parameters_json", "{}")
    report_id = request.form.get("report_id")

    try:
        raw_params = json.loads(params_json)
    except Exception:
        raw_params = {}

    if not raw_params:
        return redirect(url_for("predict", error="No verified medical parameters available for prediction."))

    # Validate readiness
    val_output = validate_extracted_data(raw_params)
    readiness = val_output["model_readiness"]

    predictor = get_multi_predictor()
    pred_output = predictor.predict_all(raw_params, readiness)

    disease_results = pred_output["disease_results"]
    overall_risk = pred_output["overall_health_risk_index"]

    # Explainable AI: Compute SHAP & LIME for Primary Active Disease (e.g. Diabetes or Heart)
    shap_explanations = {}
    primary_eval_key = "diabetes" if disease_results["diabetes"].get("evaluated") else (
        "heart_disease" if disease_results["heart_disease"].get("evaluated") else "kidney_disease"
    )

    p_res = disease_results[primary_eval_key]
    if p_res.get("evaluated"):
        model_obj = (
            predictor.diabetes_model if primary_eval_key == "diabetes"
            else (predictor.heart_model if primary_eval_key == "heart_disease" else predictor.kidney_model)
        )
        labels_map = (
            FEATURE_LABELS if primary_eval_key == "diabetes"
            else (HEART_FEATURE_LABELS if primary_eval_key == "heart_disease" else KIDNEY_FEATURE_LABELS)
        )
        raw_vals = {k: v.get("normalized_value") for k, v in raw_params.items()}

        shap_res = explain_with_shap(
            model=model_obj,
            processed_vector=p_res["processed_vector"],
            feature_names=p_res["feature_names"],
            feature_labels=labels_map,
            raw_feature_values=raw_vals,
            top_n=5,
        )
        lime_res = explain_with_lime(
            model=model_obj,
            processed_vector=p_res["processed_vector"],
            feature_names=p_res["feature_names"],
            feature_labels=labels_map,
            raw_feature_values=raw_vals,
            top_n=5,
        )
        shap_explanations[primary_eval_key] = shap_res
    else:
        shap_res = {
            "top_contributions": [],
            "summary_bullets": ["Clinical parameters insufficient for detailed local attribution."],
        }
        lime_res = {"available": False, "rules": []}

    # Generate Clinical Decision Support
    decision_support = generate_clinical_decision_support(
        disease_results=disease_results,
        shap_explanations=shap_explanations,
        overall_risk=overall_risk,
    )

    # Persist predictions and explanations into database
    if report_id:
        try:
            db.save_predictions_and_explanations(
                report_id=int(report_id),
                prediction_results=pred_output,
                shap_explanations=shap_explanations,
            )
        except Exception as e:
            print("DB save error:", e)

    report_meta = {
        "file_name": request.form.get("file_name", "Unknown Report"),
        "file_size_kb": request.form.get("file_size_kb", "0"),
        "ocr_used": request.form.get("ocr_used") == "True",
    }

    return render_template(
        "results.html",
        report_meta=report_meta,
        extracted_parameters=raw_params,
        disease_results=disease_results,
        overall_index=overall_risk,
        shap_explanation=shap_res,
        lime_explanation=lime_res,
        decision_support=decision_support,
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    JSON API for partial-feature predictions.
    Accepts partial extracted data and returns disease predictions and coverage.
    """
    try:
        raw_params = request.get_json() or {}
    except Exception:
        return {"error": "Invalid JSON payload"}, 400

    # Ensure all values are wrapped in a dict with 'normalized_value' so validator/predictor works
    formatted_params = {}
    for k, v in raw_params.items():
        if isinstance(v, dict) and "normalized_value" in v:
            formatted_params[k] = v
        else:
            # Assume raw float/int is passed directly
            try:
                formatted_params[k] = {"normalized_value": float(v)}
            except (ValueError, TypeError):
                pass

    if not formatted_params:
        return {"error": "No valid parameters provided"}, 400

    val_output = validate_extracted_data(formatted_params)
    readiness = val_output["model_readiness"]

    predictor = get_multi_predictor()
    pred_output = predictor.predict_all(formatted_params, readiness)

    # Return exactly the JSON format requested
    return pred_output["disease_results"]


@app.route("/visualize")
def visualize():
    """
    Expanded Visualizations Dashboard covering Diabetes, Heart Disease, and Kidney Disease
    across all 5 candidate machine learning algorithms.
    """
    # 1. Dataset stats
    df_diab = pd.read_csv(RAW_DATA_PATH)
    df_heart = pd.read_csv(HEART_DATA_PATH) if HEART_DATA_PATH.exists() else pd.DataFrame()
    df_kidney = pd.read_csv(KIDNEY_DATA_PATH) if KIDNEY_DATA_PATH.exists() else pd.DataFrame()
    df_thyroid = pd.read_csv(THYROID_DATA_PATH) if THYROID_DATA_PATH.exists() else pd.DataFrame()

    diab_counts = {str(k): int(v) for k, v in df_diab["Outcome"].value_counts().sort_index().items()}
    heart_counts = {str(k): int(v) for k, v in df_heart["target"].value_counts().sort_index().items()} if not df_heart.empty else {}
    kidney_counts = {str(k): int(v) for k, v in df_kidney["classification"].value_counts().sort_index().items()} if not df_kidney.empty else {}
    
    # Handle Recurred string values to int for counting
    thyroid_counts = {}
    if not df_thyroid.empty:
        mapped = df_thyroid["Recurred"].map({'Yes': 1, 'No': 0})
        thyroid_counts = {str(k): int(v) for k, v in mapped.value_counts().sort_index().items()}

    # Feature histograms for key features in Diabetes
    hist_features = ["Glucose", "BMI", "Age", "BloodPressure"]
    hist_data = {}
    for col in hist_features:
        counts, edges = np.histogram(df_diab[col], bins=10)
        hist_data[col] = {
            "counts": counts.tolist(),
            "labels": [f"{edges[i]:.1f}–{edges[i+1]:.1f}" for i in range(len(counts))],
        }

    # Histogram split by class for Glucose
    hist_glucose_by_class = {}
    for outcome, label in [(0, "Non-diabetic"), (1, "Diabetic")]:
        subset = df_diab[df_diab["Outcome"] == outcome]["Glucose"]
        counts, _ = np.histogram(subset, bins=10, range=(df_diab["Glucose"].min(), df_diab["Glucose"].max()))
        hist_glucose_by_class[label] = counts.tolist()
    glucose_bins = [f"{edges[i]:.0f}" for i in range(len(hist_data["Glucose"]["counts"]))]

    # Mean feature values by class
    means_by_class = df_diab.groupby("Outcome")[FEATURE_COLUMNS].mean().round(2)
    feature_means = {
        "labels": FEATURE_COLUMNS,
        "non_diabetic": means_by_class.loc[0].tolist(),
        "diabetic": means_by_class.loc[1].tolist(),
    }

    # --- ADVANCED EDA METRICS ---
    # 1. Data Quality
    eda_quality = {
        "missing_values": int(df_diab.isnull().sum().sum()),
        "duplicate_rows": int(df_diab.duplicated().sum()),
        "total_rows": len(df_diab)
    }

    # 2. Outliers (IQR Method)
    eda_outliers = {}
    for col in FEATURE_COLUMNS:
        if pd.api.types.is_numeric_dtype(df_diab[col]):
            Q1 = df_diab[col].quantile(0.25)
            Q3 = df_diab[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df_diab[(df_diab[col] < lower) | (df_diab[col] > upper)]
            eda_outliers[col] = len(outliers)

    # 3. Patterns / Correlations (Target correlation)
    corr_matrix = df_diab[FEATURE_COLUMNS + ["Outcome"]].corr()
    corr_with_target = corr_matrix["Outcome"].drop("Outcome").fillna(0).round(2).to_dict()
    sorted_corrs = sorted(corr_with_target.items(), key=lambda x: abs(x[1]), reverse=True)
    eda_corr = {
        "labels": [item[0] for item in sorted_corrs],
        "values": [item[1] for item in sorted_corrs]
    }

    # 4. Distributions (Raw data for Box Plots)
    # We pass the full array (768 points) for the frontend BoxPlot plugin to crunch.
    eda_dist = {col: df_diab[col].fillna(0).tolist() for col in FEATURE_COLUMNS}
    # ----------------------------

    # 2. Model Metrics Comparison for Diabetes, Heart Disease, and Kidney Disease
    diab_metrics = json.loads((RESULTS_DIR / "diabetes_metrics.json").read_text(encoding="utf-8")) if (RESULTS_DIR / "diabetes_metrics.json").exists() else {}
    heart_metrics = json.loads((RESULTS_DIR / "heart_metrics.json").read_text(encoding="utf-8")) if (RESULTS_DIR / "heart_metrics.json").exists() else {}
    kidney_metrics = json.loads((RESULTS_DIR / "kidney_metrics.json").read_text(encoding="utf-8")) if (RESULTS_DIR / "kidney_metrics.json").exists() else {}
    thyroid_metrics = json.loads((RESULTS_DIR / "thyroid_metrics.json").read_text(encoding="utf-8")) if (RESULTS_DIR / "thyroid_metrics.json").exists() else {}

    diab_meta = json.loads((DIABETES_MODELS_DIR / "metadata.json").read_text(encoding="utf-8")) if (DIABETES_MODELS_DIR / "metadata.json").exists() else {}
    heart_meta = json.loads((HEART_MODELS_DIR / "metadata.json").read_text(encoding="utf-8")) if (HEART_MODELS_DIR / "metadata.json").exists() else {}
    kidney_meta = json.loads((KIDNEY_MODELS_DIR / "metadata.json").read_text(encoding="utf-8")) if (KIDNEY_MODELS_DIR / "metadata.json").exists() else {}
    thyroid_meta = json.loads((THYROID_MODELS_DIR / "metadata.json").read_text(encoding="utf-8")) if (THYROID_MODELS_DIR / "metadata.json").exists() else {}

    # Format model comparison chart data for Diabetes (5 algorithms)
    model_names = list(diab_metrics.keys())
    metric_keys = ["accuracy", "precision", "recall", "specificity", "f1", "roc_auc", "f_beta", "pr_auc"]
    model_chart_metrics = {mk: [round(diab_metrics[mn].get(mk, 0) * 100, 1) for mn in model_names] for mk in metric_keys}
    model_chart_metrics["log_loss"] = [round(diab_metrics[mn].get("log_loss", 0), 2) for mn in model_names]
    model_chart_metrics["mcc"] = [round(diab_metrics[mn].get("mcc", 0), 3) for mn in model_names]

    model_chart = {
        "labels": [n.replace("_", " ").title() for n in model_names],
        "metrics": model_chart_metrics,
    }

    # Confusion matrix for selected Diabetes model
    selected = diab_meta.get("selected_model", "xgboost")
    cm = diab_metrics.get(selected, {}).get("confusion_matrix", {})
    confusion = {
        "tn": cm.get("true_negative", 0),
        "fp": cm.get("false_positive", 0),
        "fn": cm.get("false_negative", 0),
        "tp": cm.get("true_positive", 0),
        "model": selected.replace("_", " ").title(),
    }

    # Global Feature Importances from Models
    predictor = get_multi_predictor()
    def get_importance(model, labels_map):
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            labels_list = [labels_map.get(k, k) for k in getattr(model, "feature_names_in_", list(labels_map.keys()))]
            if not labels_list or len(labels_list) != len(imp):
                labels_list = list(labels_map.values())[:len(imp)]
            res = sorted(zip(labels_list, imp), key=lambda x: x[1], reverse=True)
            return {"labels": [x[0] for x in res], "values": [float(x[1]) for x in res]}
        return {"labels": [], "values": []}

    diab_imp = get_importance(predictor.diabetes_model, FEATURE_LABELS)
    heart_imp = get_importance(predictor.heart_model, HEART_FEATURE_LABELS)
    kidney_imp = get_importance(predictor.kidney_model, KIDNEY_FEATURE_LABELS)
    thyroid_imp = get_importance(predictor.thyroid_model, THYROID_FEATURE_LABELS)

    return render_template(
        "visualize.html",
        class_counts_json=json.dumps(diab_counts),
        heart_counts_json=json.dumps(heart_counts),
        kidney_counts_json=json.dumps(kidney_counts),
        thyroid_counts_json=json.dumps(thyroid_counts),
        hist_data_json=json.dumps(hist_data),
        hist_glucose_by_class_json=json.dumps(hist_glucose_by_class),
        glucose_bins_json=json.dumps(glucose_bins),
        feature_means_json=json.dumps(feature_means),
        model_chart_json=json.dumps(model_chart),
        confusion_json=json.dumps(confusion),
        eda_quality_json=json.dumps(eda_quality),
        eda_outliers_json=json.dumps(eda_outliers),
        eda_corr_json=json.dumps(eda_corr),
        eda_dist_json=json.dumps(eda_dist),
        diab_imp_json=json.dumps(diab_imp),
        heart_imp_json=json.dumps(heart_imp),
        kidney_imp_json=json.dumps(kidney_imp),
        thyroid_imp_json=json.dumps(thyroid_imp),
        diab_metrics=diab_metrics,
        heart_metrics=heart_metrics,
        kidney_metrics=kidney_metrics,
        thyroid_metrics=thyroid_metrics,
        diab_meta=diab_meta,
        heart_meta=heart_meta,
        kidney_meta=kidney_meta,
        thyroid_meta=thyroid_meta,
        n_rows=len(df_diab),
        n_heart_rows=len(df_heart),
        n_kidney_rows=len(df_kidney),
        n_thyroid_rows=len(df_thyroid),
        n_features=len(FEATURE_COLUMNS),
        selected_model=selected.replace("_", " ").title(),
        selected_roc=round(diab_metrics.get(selected, {}).get("roc_auc", 0) * 100, 1),
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5050)
