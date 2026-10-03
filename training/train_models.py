import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    DIABETES_MODELS_DIR,
    FEATURE_COLUMNS,
    HEART_DATA_PATH,
    HEART_FEATURE_COLUMNS,
    HEART_MODELS_DIR,
    HEART_TARGET_COLUMN,
    KIDNEY_DATA_PATH,
    KIDNEY_FEATURE_COLUMNS,
    KIDNEY_MODELS_DIR,
    KIDNEY_TARGET_COLUMN,
    RANDOM_STATE,
    RAW_DATA_PATH,
    RESULTS_DIR,
    SELECTION_METRIC,
    TARGET_COLUMN,
    TEST_SIZE,
)
from src.evaluate import compute_classification_metrics
from src.preprocessing import build_preprocessor as build_diabetes_preprocessor
from src.preprocessing import load_diabetes_dataframe


def get_candidate_models():
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            random_state=RANDOM_STATE,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_leaf=6,
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            min_samples_leaf=3,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
        ),
        "naive_bayes": GaussianNB(),
    }


def train_disease(
    name: str,
    data_path: Path,
    feature_cols: list,
    target_col: str,
    models_dir: Path,
    metrics_file: Path,
    custom_preprocessor=None,
):
    print(f"\n==========================================")
    print(f"Training models for: {name.upper()}")
    print(f"==========================================")
    if not data_path.exists():
        raise FileNotFoundError(f"Missing dataset at {data_path}")

    data = pd.read_csv(data_path)
    X = data[feature_cols]
    y = data[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    if custom_preprocessor is not None:
        preprocessor = custom_preprocessor
    else:
        preprocessor = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    candidate_models = get_candidate_models()
    all_metrics = {}
    fitted_models = {}

    for model_name, estimator in candidate_models.items():
        estimator.fit(X_train_processed, y_train)
        y_pred = estimator.predict(X_test_processed)
        if hasattr(estimator, "predict_proba"):
            y_proba = estimator.predict_proba(X_test_processed)[:, 1]
        else:
            y_proba = y_pred.astype(float)

        metrics = compute_classification_metrics(y_test, y_pred, y_proba)
        all_metrics[model_name] = metrics
        fitted_models[model_name] = estimator

    # Model selection based on SELECTION_METRIC (ROC-AUC)
    selected_name = max(all_metrics, key=lambda k: all_metrics[k][SELECTION_METRIC])
    selected_model = fitted_models[selected_name]

    models_dir.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(preprocessor, models_dir / "preprocessor.joblib")
    joblib.dump(selected_model, models_dir / "model.joblib")

    # Also save all models so the user/UI can compare and examine them
    for m_name, m_inst in fitted_models.items():
        joblib.dump(m_inst, models_dir / f"{m_name}.joblib")

    metadata = {
        "disease": name,
        "n_rows": int(len(data)),
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "target": target_col,
        "class_counts": {str(k): int(v) for k, v in y.value_counts().items()},
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "selection_metric": SELECTION_METRIC,
        "selected_model": selected_name,
        "selected_metrics": all_metrics[selected_name],
        "all_models": all_metrics,
        "split": {
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
        },
    }

    (models_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metrics_file.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")

    print(f"Dataset: {len(data)} rows ({len(X_train)} train, {len(X_test)} test)")
    print(f"Selected model: {selected_name} ({SELECTION_METRIC} = {all_metrics[selected_name][SELECTION_METRIC]:.4f})")
    for m_name, m_mets in all_metrics.items():
        marker = " [SELECTED]" if m_name == selected_name else ""
        print(
            f"  {m_name:<20}: Acc={m_mets['accuracy']:.4f}  "
            f"F1={m_mets['f1']:.4f}  Recall={m_mets['recall']:.4f}  "
            f"Spec={m_mets['specificity']:.4f}  ROC-AUC={m_mets['roc_auc']:.4f}{marker}"
        )
    return metadata, all_metrics


def train_all():
    # 1. Diabetes
    train_disease(
        name="diabetes",
        data_path=RAW_DATA_PATH,
        feature_cols=FEATURE_COLUMNS,
        target_col=TARGET_COLUMN,
        models_dir=DIABETES_MODELS_DIR,
        metrics_file=RESULTS_DIR / "diabetes_metrics.json",
        custom_preprocessor=build_diabetes_preprocessor(),
    )

    # 2. Heart Disease
    train_disease(
        name="heart_disease",
        data_path=HEART_DATA_PATH,
        feature_cols=HEART_FEATURE_COLUMNS,
        target_col=HEART_TARGET_COLUMN,
        models_dir=HEART_MODELS_DIR,
        metrics_file=RESULTS_DIR / "heart_metrics.json",
    )

    # 3. Kidney Disease
    train_disease(
        name="kidney_disease",
        data_path=KIDNEY_DATA_PATH,
        feature_cols=KIDNEY_FEATURE_COLUMNS,
        target_col=KIDNEY_TARGET_COLUMN,
        models_dir=KIDNEY_MODELS_DIR,
        metrics_file=RESULTS_DIR / "kidney_metrics.json",
    )
    print("\n[SUCCESS] All 3 disease models successfully trained across 5 algorithms!")


if __name__ == "__main__":
    train_all()
