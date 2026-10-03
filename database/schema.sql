-- Healthcare Disease Prediction Database Schema

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploaded_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    filename TEXT NOT NULL,
    file_type TEXT,
    file_size_kb REAL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extraction_status TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS extracted_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL,
    raw_value TEXT,
    normalized_value REAL,
    unit TEXT,
    confidence REAL,
    source_text TEXT,
    FOREIGN KEY(report_id) REFERENCES uploaded_reports(id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    disease TEXT NOT NULL,
    model_name TEXT NOT NULL,
    probability REAL,
    risk_label TEXT,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES uploaded_reports(id)
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    overall_risk INTEGER,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES uploaded_reports(id)
);

CREATE TABLE IF NOT EXISTS explanations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    disease TEXT NOT NULL,
    method TEXT NOT NULL,
    top_factors_json TEXT,
    narrative TEXT,
    FOREIGN KEY(report_id) REFERENCES uploaded_reports(id)
);

CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease TEXT NOT NULL,
    model_name TEXT NOT NULL,
    accuracy REAL,
    precision_val REAL,
    recall_val REAL,
    specificity REAL,
    f1 REAL,
    roc_auc REAL,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
