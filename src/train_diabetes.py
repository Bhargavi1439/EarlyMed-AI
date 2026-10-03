import json
import sys
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    FEATURE_COLUMNS,
    METADATA_PATH,
    METRICS_PATH,
    MODEL_PATH,
    MODELS_DIR,
    PREPROCESSOR_PATH,
    RANDOM_STATE,
    RAW_DATA_PATH,
    RESULTS_DIR,
    SELECTION_METRIC,
    TARGET_COLUMN,
    TEST_SIZE,
)
from src.evaluate import compute_classification_metrics
from src.preprocessing import build_preprocessor, load_diabetes_dataframe


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



def train():
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {RAW_DATA_PATH}")

    data = load_diabetes_dataframe(RAW_DATA_PATH)
    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    all_metrics = {}
    fitted_models = {}
    for name, estimator in _candidate_models().items():
        estimator.fit(X_train_processed, y_train)
        y_pred = estimator.predict(X_test_processed)
        if hasattr(estimator, "predict_proba"):
            y_proba = estimator.predict_proba(X_test_processed)[:, 1]
        else:
            y_proba = y_pred.astype(float)
        all_metrics[name] = compute_classification_metrics(y_test, y_pred, y_proba)
        fitted_models[name] = estimator

    selected_name = max(all_metrics, key=lambda key: all_metrics[key][SELECTION_METRIC])
    selected_model = fitted_models[selected_name]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    joblib.dump(selected_model, MODEL_PATH)

    class_counts = y.value_counts().to_dict()
    metadata = {
        "dataset": "Pima Indians Diabetes Database",
        "n_rows": int(len(data)),
        "n_features": len(FEATURE_COLUMNS),
        "feature_names": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
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
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")

    print(f"Trained on {len(X_train)} rows, evaluated on {len(X_test)} held-out rows.")
    print(f"Selected model ({SELECTION_METRIC}): {selected_name}")
    for name, metrics in all_metrics.items():
        marker = " <-- selected" if name == selected_name else ""
        print(
            f"  {name}: accuracy={metrics['accuracy']:.4f}  "
            f"f1={metrics['f1']:.4f}  roc_auc={metrics['roc_auc']:.4f}{marker}"
        )
    print(f"Saved preprocessor -> {PREPROCESSOR_PATH}")
    print(f"Saved model        -> {MODEL_PATH}")
    print(f"Saved metrics      -> {METRICS_PATH}")


if __name__ == "__main__":
    train()
