import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    THYROID_FEATURE_COLUMNS,
    THYROID_METADATA_PATH,
    THYROID_METRICS_PATH,
    THYROID_MODEL_PATH,
    THYROID_MODELS_DIR,
    THYROID_PREPROCESSOR_PATH,
    RANDOM_STATE,
    THYROID_DATA_PATH,
    RESULTS_DIR,
    SELECTION_METRIC,
    THYROID_TARGET_COLUMN,
    TEST_SIZE,
)
from src.evaluate import compute_classification_metrics


def _candidate_models():
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            random_state=RANDOM_STATE,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_leaf=8,
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=4,
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


def build_thyroid_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    return preprocessor


def train():
    if not THYROID_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {THYROID_DATA_PATH}")

    data = pd.read_csv(THYROID_DATA_PATH)
    
    # Identify numeric and categorical columns
    numeric_cols = [col for col in THYROID_FEATURE_COLUMNS if pd.api.types.is_numeric_dtype(data[col])]
    categorical_cols = [col for col in THYROID_FEATURE_COLUMNS if not pd.api.types.is_numeric_dtype(data[col])]

    X = data[THYROID_FEATURE_COLUMNS]
    y_raw = data[THYROID_TARGET_COLUMN]
    
    # Map target 'Recurred' (Yes/No) to 1/0
    y = y_raw.map({'Yes': 1, 'No': 0}).fillna(0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    preprocessor = build_thyroid_preprocessor(numeric_cols, categorical_cols)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Get feature names after one-hot encoding for feature importances
    try:
        cat_feature_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols)
        feature_names_out = numeric_cols + list(cat_feature_names)
    except:
        feature_names_out = None

    all_metrics = {}
    fitted_models = {}
    for name, estimator in _candidate_models().items():
        estimator.fit(X_train_processed, y_train)
        if feature_names_out is not None and hasattr(estimator, "feature_names_in_"):
            estimator.feature_names_in_ = feature_names_out
            
        y_pred = estimator.predict(X_test_processed)
        if hasattr(estimator, "predict_proba"):
            y_proba = estimator.predict_proba(X_test_processed)[:, 1]
        else:
            y_proba = y_pred.astype(float)
        all_metrics[name] = compute_classification_metrics(y_test, y_pred, y_proba)
        fitted_models[name] = estimator

    selected_name = max(all_metrics, key=lambda key: all_metrics[key][SELECTION_METRIC])
    selected_model = fitted_models[selected_name]

    THYROID_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(preprocessor, THYROID_PREPROCESSOR_PATH)
    joblib.dump(selected_model, THYROID_MODEL_PATH)

    class_counts = y.value_counts().to_dict()
    metadata = {
        "dataset": "Thyroid Disease Dataset",
        "n_rows": int(len(data)),
        "n_features": len(THYROID_FEATURE_COLUMNS),
        "feature_names": THYROID_FEATURE_COLUMNS,
        "target": THYROID_TARGET_COLUMN,
        "class_counts": {str(k): int(v) for k, v in class_counts.items()},
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
    THYROID_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    THYROID_METRICS_PATH.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")

    print(f"Trained on {len(X_train)} rows, evaluated on {len(X_test)} held-out rows.")
    print(f"Selected model ({SELECTION_METRIC}): {selected_name}")
    for name, metrics in all_metrics.items():
        marker = " <-- selected" if name == selected_name else ""
        print(
            f"  {name}: accuracy={metrics['accuracy']:.4f}  "
            f"f1={metrics['f1']:.4f}  roc_auc={metrics['roc_auc']:.4f}{marker}"
        )
    print(f"Saved preprocessor -> {THYROID_PREPROCESSOR_PATH}")
    print(f"Saved model        -> {THYROID_MODEL_PATH}")
    print(f"Saved metrics      -> {THYROID_METRICS_PATH}")


if __name__ == "__main__":
    train()
