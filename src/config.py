from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RANDOM_STATE = 42
TEST_SIZE = 0.20

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "diabetes.csv"
HEART_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "heart.csv"
KIDNEY_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "kidney.csv"

DIABETES_MODELS_DIR = PROJECT_ROOT / "models" / "diabetes"
HEART_MODELS_DIR = PROJECT_ROOT / "models" / "heart"
KIDNEY_MODELS_DIR = PROJECT_ROOT / "models" / "kidney"

# Backward compatibility alias
MODELS_DIR = DIABETES_MODELS_DIR
RESULTS_DIR = PROJECT_ROOT / "results"

PREPROCESSOR_PATH = DIABETES_MODELS_DIR / "preprocessor.joblib"
MODEL_PATH = DIABETES_MODELS_DIR / "model.joblib"
METADATA_PATH = DIABETES_MODELS_DIR / "metadata.json"
METRICS_PATH = RESULTS_DIR / "diabetes_metrics.json"

HEART_PREPROCESSOR_PATH = HEART_MODELS_DIR / "preprocessor.joblib"
HEART_MODEL_PATH = HEART_MODELS_DIR / "model.joblib"
HEART_METADATA_PATH = HEART_MODELS_DIR / "metadata.json"
HEART_METRICS_PATH = RESULTS_DIR / "heart_metrics.json"

KIDNEY_PREPROCESSOR_PATH = KIDNEY_MODELS_DIR / "preprocessor.joblib"
KIDNEY_MODEL_PATH = KIDNEY_MODELS_DIR / "model.joblib"
KIDNEY_METADATA_PATH = KIDNEY_MODELS_DIR / "metadata.json"
KIDNEY_METRICS_PATH = RESULTS_DIR / "kidney_metrics.json"

# Diabetes features
FEATURE_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]
TARGET_COLUMN = "Outcome"

# Zeros in these columns are physiologically invalid and treated as missing.
INVALID_ZERO_COLUMNS = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]

# Inclusive bounds used by validation
FEATURE_RANGES = {
    "Pregnancies": (0, 20),
    "Glucose": (40, 300),
    "BloodPressure": (30, 200),
    "SkinThickness": (1, 100),
    "Insulin": (1, 900),
    "BMI": (10.0, 70.0),
    "DiabetesPedigreeFunction": (0.05, 2.5),
    "Age": (18, 120),
}

FEATURE_LABELS = {
    "Pregnancies": "Number of pregnancies",
    "Glucose": "Plasma glucose (mg/dL)",
    "BloodPressure": "Diastolic blood pressure (mm Hg)",
    "SkinThickness": "Triceps skin fold thickness (mm)",
    "Insulin": "2-hour serum insulin (µU/mL)",
    "BMI": "Body mass index",
    "DiabetesPedigreeFunction": "Diabetes pedigree function",
    "Age": "Age (years)",
}

# Heart disease features
HEART_FEATURE_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
HEART_TARGET_COLUMN = "target"

HEART_FEATURE_LABELS = {
    "age": "Age (years)",
    "sex": "Sex (1=Male, 0=Female)",
    "cp": "Chest pain type",
    "trestbps": "Resting blood pressure (mm Hg)",
    "chol": "Serum cholesterol (mg/dL)",
    "fbs": "Fasting blood sugar > 120 mg/dL",
    "restecg": "Resting ECG results",
    "thalach": "Maximum heart rate (bpm)",
    "exang": "Exercise induced angina",
    "oldpeak": "ST depression",
    "slope": "Peak exercise ST segment",
    "ca": "Major vessels colored",
    "thal": "Thalassemia status",
}

# Kidney disease features
KIDNEY_FEATURE_COLUMNS = [
    "age",
    "bp",
    "bgr",
    "bu",
    "sc",
    "hemo",
    "pcv",
    "wc",
    "rc",
    "al",
    "sg",
    "htn",
    "dm",
]
KIDNEY_TARGET_COLUMN = "classification"

KIDNEY_FEATURE_LABELS = {
    "age": "Age (years)",
    "bp": "Blood pressure (mm Hg)",
    "bgr": "Blood glucose random (mg/dL)",
    "bu": "Blood urea (mg/dL)",
    "sc": "Serum creatinine (mg/dL)",
    "hemo": "Hemoglobin (g/dL)",
    "pcv": "Packed cell volume (%)",
    "wc": "White blood cell count (/µL)",
    "rc": "Red blood cell count (M/µL)",
    "al": "Albumin (0-5 scale)",
    "sg": "Specific gravity",
    "htn": "Hypertension (1=Yes, 0=No)",
    "dm": "Diabetes mellitus (1=Yes, 0=No)",
}

SELECTION_METRIC = "roc_auc"
CANDIDATE_MODEL_NAMES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "xgboost",
    "naive_bayes",
]

# Thyroid dataset features
THYROID_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Thyroid.csv"
THYROID_MODELS_DIR = PROJECT_ROOT / "models" / "thyroid"
THYROID_PREPROCESSOR_PATH = THYROID_MODELS_DIR / "preprocessor.joblib"
THYROID_MODEL_PATH = THYROID_MODELS_DIR / "model.joblib"
THYROID_METADATA_PATH = THYROID_MODELS_DIR / "metadata.json"
THYROID_METRICS_PATH = RESULTS_DIR / "thyroid_metrics.json"

THYROID_FEATURE_COLUMNS = [
    "Age", "Gender", "Smoking", "Hx Smoking", "Hx Radiothreapy", 
    "Thyroid Function", "Physical Examination", "Adenopathy", 
    "Pathology", "Focality", "Risk", "T", "N", "M", "Stage", "Response"
]
THYROID_TARGET_COLUMN = "Recurred"

THYROID_FEATURE_LABELS = {
    "Age": "Age (years)",
    "Gender": "Gender",
    "Smoking": "Smoking Status",
    "Hx Smoking": "History of Smoking",
    "Hx Radiothreapy": "History of Radiotherapy",
    "Thyroid Function": "Thyroid Function",
    "Physical Examination": "Physical Examination",
    "Adenopathy": "Adenopathy",
    "Pathology": "Pathology",
    "Focality": "Focality",
    "Risk": "Risk Level",
    "T": "T Stage",
    "N": "N Stage",
    "M": "M Stage",
    "Stage": "Clinical Stage",
    "Response": "Treatment Response"
}

