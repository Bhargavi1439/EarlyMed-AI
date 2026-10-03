import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import FEATURE_COLUMNS, METADATA_PATH, MODEL_PATH, PREPROCESSOR_PATH
from src.preprocessing import InvalidZeroToNaN  # noqa: F401  (needed for joblib unpickle)


class DiabetesPredictor:
    def __init__(self):
        if not PREPROCESSOR_PATH.exists() or not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Trained artifacts not found. Run: python src/train_diabetes.py"
            )
        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        self.model = joblib.load(MODEL_PATH)
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8")) if METADATA_PATH.exists() else {}

    def predict_one(self, feature_values: dict) -> dict:
        row = pd.DataFrame([{col: feature_values[col] for col in FEATURE_COLUMNS}])
        processed = self.preprocessor.transform(row)
        probability = float(self.model.predict_proba(processed)[0, 1])
        predicted_class = int(probability >= 0.5)
        return {
            "predicted_class": predicted_class,
            "risk_label": "Higher diabetes risk" if predicted_class == 1 else "Lower diabetes risk",
            "probability": probability,
            "model_name": self.metadata.get("selected_model", "unknown"),
        }
