import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import FEATURE_COLUMNS, INVALID_ZERO_COLUMNS, TARGET_COLUMN


class InvalidZeroToNaN(BaseEstimator, TransformerMixin):
    """Replace physiologically invalid zeros with NaN (fit is a no-op)."""

    def __init__(self, columns=None):
        self.columns = list(columns) if columns is not None else list(INVALID_ZERO_COLUMNS)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        frame = pd.DataFrame(X, columns=FEATURE_COLUMNS).copy()
        for column in self.columns:
            if column in frame.columns:
                frame.loc[frame[column] == 0, column] = pd.NA
        return frame


def load_diabetes_dataframe(csv_path):
    data = pd.read_csv(csv_path)
    missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    return data


def build_preprocessor():
    return Pipeline(
        steps=[
            ("invalid_zeros", InvalidZeroToNaN(INVALID_ZERO_COLUMNS)),
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
