# EarlyMed-AI

3rd-year CSE Project Title:

**An Explainable Machine Learning Framework for Early Multi-Disease Risk Prediction Using Healthcare Data Analytics**

---

## 📌 Project Overview

**EarlyMed-AI** is an advanced, explainable machine learning framework designed for early multi-disease risk prediction, medical report data extraction, and clinical decision support.

The system processes structured or unstructured medical lab reports (PDF documents and scanned image slips via OCR and diagnostic text parsing), extracts key physiological biomarkers, evaluates risk across **4 major clinical conditions** (Diabetes, Heart Disease, Chronic Kidney Disease, and Thyroid Cancer Recurrence), computes a weighted composite **Overall Health Risk Index (0–100 scale)**, and delivers **Explainable AI (XAI)** insights via SHAP feature attributions and LIME surrogate decision rules.

---

## 📊 Datasets Actually Used

The framework utilizes **4 benchmark healthcare datasets**:

1. **Pima Indians Diabetes Dataset**
   - **Records**: 768 patient cases
   - **Features (8)**: Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, Age
   - **Target**: Binary Diabetes Outcome (`0` vs `1`)

2. **UCI Heart Disease Dataset**
   - **Records**: 303 patient cases
   - **Features (13)**: Age, Sex, Chest Pain Type (`cp`), Resting BP (`trestbps`), Cholesterol (`chol`), Fasting Blood Sugar (`fbs`), Rest ECG (`restecg`), Max Heart Rate (`thalach`), Exercise Angina (`exang`), ST Depression (`oldpeak`), ST Slope (`slope`), Major Vessels (`ca`), Thalassemia (`thal`)
   - **Target**: Binary Heart Disease Risk (`0` vs `1`)

3. **UCI Chronic Kidney Disease (CKD) Dataset**
   - **Records**: 400 patient cases
   - **Features (13)**: Age, Blood Pressure (`bp`), Blood Glucose Random (`bgr`), Blood Urea (`bu`), Serum Creatinine (`sc`), Hemoglobin (`hemo`), Packed Cell Volume (`pcv`), White Blood Cell Count (`wc`), Red Blood Cell Count (`rc`), Albumin (`al`), Specific Gravity (`sg`), Hypertension (`htn`), Diabetes Mellitus (`dm`)
   - **Target**: Binary CKD Risk (`0` vs `1`)

4. **Differentiated Thyroid Cancer Recurrence Dataset**
   - **Records**: 383 patient cases
   - **Features (16)**: Age, Gender, Smoking, Hx Smoking, Hx Radiotherapy, Thyroid Function, Physical Examination, Adenopathy, Pathology, Focality, Risk Level, T Stage, N Stage, M Stage, Clinical Stage, Treatment Response
   - **Target**: Binary Recurrence Risk (`0` vs `1`)

---

## 🤖 Algorithms Actually Implemented

For each of the 4 disease modules, **5 Machine Learning algorithms** are trained, cross-validated, and evaluated:

1. **XGBoost Classifier** (`xgboost.XGBClassifier`)
2. **Random Forest Classifier** (`sklearn.ensemble.RandomForestClassifier`)
3. **Decision Tree Classifier** (`sklearn.tree.DecisionTreeClassifier`)
4. **Logistic Regression** (`sklearn.linear_model.LogisticRegression`)
5. **Gaussian Naive Bayes** (`sklearn.naive_bayes.GaussianNB`)

The best performing model per disease module is selected based on held-out test ROC-AUC / F1 metrics and deployed in the multi-disease inference pipeline:
- **Diabetes Module**: Random Forest / XGBoost Classifier
- **Heart Disease Module**: Random Forest Classifier
- **Chronic Kidney Disease Module**: XGBoost Classifier
- **Thyroid Recurrence Module**: XGBoost Classifier

---

## 🔄 Hybridization & Multi-Disease Architecture

The framework performs **hybrid multi-disease risk synthesis** through a multi-tiered pipeline:

1. **Multi-Model Pipeline Synergy**: Integrates 4 separate specialized ML models into a unified screening engine (`MultiDiseasePredictor`).
2. **Clinical Biomarker Proxy Derivation**: Automatically derives missing parameters using established clinical formulas (e.g., estimating average glucose $eAG = 28.7 \times \text{HbA1c} - 46.7$ when fasting glucose is not directly reported).
3. **Composite Health Risk Index (0–100)**: Calculates a composite risk index emphasizing the highest individual disease risk factor alongside mean patient vulnerability:
   $$\text{Composite Risk} = 0.6 \times \max(P_i) + 0.4 \times \text{mean}(P_i)$$
   where $P_i \in [0, 1]$ represents individual evaluated disease risk probabilities.
4. **Hybrid Machine Learning + Explainable AI (XAI) + Rule-Based Decision Support**: Combines statistical tree models with local model-agnostic surrogate explainers (SHAP & LIME) and deterministic Clinical Decision Support (CDS) rules.

---

## 🧹 Data Preprocessing & Document Pipeline

- **Physiologically Invalid Zero Normalization**: Custom transformer (`InvalidZeroToNaN`) converts impossible zero values (in Glucose, BP, Skin Thickness, Insulin, BMI) to `NaN`.
- **Missing Value Imputation**: `SimpleImputer(strategy="median")` for continuous numerical biomarkers; mode/string default fallback for categorical fields.
- **Feature Scaling**: `StandardScaler()` standardizes features to zero mean and unit variance.
- **Categorical Encoding**: One-Hot Encoding and label mapping for clinical categorical variables.
- **Medical Report Extraction & OCR**:
  - **PyMuPDF (`fitz`) & `pdfplumber`**: Parses text directly from digital PDF lab reports.
  - **Diagnostic Font Encoding Normalization**: Automatically converts custom font encodings mapped to Unicode Private Use Area (`0xF000–0xF0FF`) to standard ASCII characters.
  - **Tesseract OCR (`pytesseract` + `PIL`)**: Extracts text from scanned image lab slips and image-based PDFs.
  - **Clinical Regex Parser (`medical_parser.py`)**: Extracts 30+ medical parameters using fuzzy regex patterns.

---

## 📈 Actual Model Metrics

Exact benchmark metrics recorded on held-out test sets across all 4 disease datasets and 5 algorithms:

### 🩸 1. Diabetes Risk Module (Held-out Test: 154 rows)

| Algorithm | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** 🌲 | **76.62%** | **70.45%** | **57.41%** | **63.27%** | **81.67%** | ✅ **Selected Best** |
| **XGBoost Classifier** 🚀 | 74.03% | 63.46% | 61.11% | 62.26% | 83.00% | Evaluated |
| **Decision Tree** 🌳 | 73.38% | 68.57% | 44.44% | 53.93% | 81.19% | Evaluated |
| **Logistic Regression** 📈 | 70.78% | 60.00% | 50.00% | 54.55% | 81.30% | Evaluated |
| **Naive Bayes** 📊 | 70.13% | 56.67% | 62.96% | 59.65% | 76.46% | Evaluated |

---

### 🫀 2. Heart Disease Module (Held-out Test: 61 rows)

| Algorithm | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** 🌲 | **90.16%** | **86.67%** | **92.86%** | **89.66%** | **96.00%** | ✅ **Selected Best** |
| **XGBoost Classifier** 🚀 | 88.52% | 81.82% | 96.43% | 88.52% | 94.81% | Evaluated |
| **Naive Bayes** 📊 | 86.89% | 79.41% | 96.43% | 87.10% | 95.24% | Evaluated |
| **Logistic Regression** 📈 | 86.89% | 81.25% | 92.86% | 86.67% | 95.13% | Evaluated |
| **Decision Tree** 🌳 | 78.69% | 72.73% | 85.71% | 78.69% | 88.47% | Evaluated |

---

### 🩺 3. Chronic Kidney Disease (CKD) Module (Held-out Test: 80 rows)

| Algorithm | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost Classifier** 🚀 | **100.00%** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | ✅ **Selected Best** |
| **Random Forest** 🌲 | 98.75% | 98.04% | 100.00% | 99.01% | 100.00% | Evaluated |
| **Logistic Regression** 📈 | 97.50% | 98.00% | 98.00% | 98.00% | 99.93% | Evaluated |
| **Decision Tree** 🌳 | 97.50% | 98.00% | 98.00% | 98.00% | 99.80% | Evaluated |
| **Naive Bayes** 📊 | 95.00% | 100.00% | 92.00% | 95.83% | 100.00% | Evaluated |

---

### 🦋 4. Thyroid Cancer Recurrence Module (Held-out Test: 77 rows)

| Algorithm | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost Classifier** 🚀 | **97.40%** | **100.00%** | **90.91%** | **95.24%** | **99.42%** | ✅ **Selected Best** |
| **Logistic Regression** 📈 | 97.40% | 100.00% | 90.91% | 95.24% | 99.01% | Evaluated |
| **Random Forest** 🌲 | 96.10% | 100.00% | 86.36% | 92.68% | 99.50% | Evaluated |
| **Decision Tree** 🌳 | 94.81% | 95.00% | 86.36% | 90.48% | 96.94% | Evaluated |
| **Naive Bayes** 📊 | 93.51% | 94.74% | 81.82% | 87.80% | 97.89% | Evaluated |

---

## 📦 Actual Prediction Outputs

For any patient input or parsed report, the prediction system generates:

1. **Disease-Specific Predictions**:
   - `evaluated`: `True` / `False` readiness check
   - `predicted_class`: `1` (Risk Detected) or `0` (No Risk Detected)
   - `risk_label`: `"risk_detected"` / `"no_risk_detected"` / `"Not Evaluated"`
   - `probability`: Risk probability (e.g., `0.842`) and percentage (`84.2%`)
   - `features_used`, `features_found`, `features_missing`, `imputed_features` list
2. **Overall Health Risk Index**:
   - `score`: Composite integer score from `0` to `100`
   - `category`: `"Lower estimated risk"`, `"Moderate estimated risk"`, or `"Higher estimated risk"`
   - `badge_class`: CSS styling class (`risk-low`, `risk-medium`, `risk-high`)
3. **Explainable AI (XAI) Output Objects**:
   - SHAP feature contribution list with directional impact & percentage bar widths
   - LIME decision rules list with condition thresholds & weights
4. **Clinical Decision Support (CDS)**:
   - Rule-based research observations and clinical follow-up points without replacing professional medical advice.

---

## 🔍 SHAP & LIME Implementation

### 1. SHAP (SHapley Additive exPlanations)
- **Implementation**: [`explainability/shap_explainer.py`](explainability/shap_explainer.py)
- **Method**: Uses `shap.TreeExplainer` for exact feature attribution on tree-based models (XGBoost, Random Forest, Decision Tree).
- **Features**:
  - Calculates patient-specific Shapley values $\phi_i$ for each input parameter.
  - Classifies contribution directions (`higher_risk` vs `lower_risk`).
  - Computes relative impact percentage bars (`bar_percentage`).
  - Generates plain-language narrative summaries explaining key risk drivers.
  - Includes linear model fallback ($x_i \cdot w_i$) if SHAP library is not installed or model is non-tree.

### 2. LIME (Local Interpretable Model-agnostic Explanations)
- **Implementation**: [`explainability/lime_explainer.py`](explainability/lime_explainer.py)
- **Method**: Uses `LimeTabularExplainer` to fit a local linear surrogate model around the patient's feature vector.
- **Features**:
  - Perturbs local background distribution around patient data points.
  - Returns human-readable IF-THEN rules (e.g., `Serum Creatinine (mg/dL) > 1.20`).
  - Assigns rule weights and directional impact indicators.

---

## 💻 Dashboard Functionality

Built with **Flask**, **Jinja2 templates**, **Vanilla CSS**, and **Chart.js**:

- **`/` (Home Dashboard)**: Project overview, clinical disclaimer, module summary cards.
- **`/predict` (Medical Report Upload & Editor)**:
  - File upload drag-and-drop zone accepting PDF, PNG, JPG, BMP, TIFF, WebP.
  - Automated extraction preview & interactive parameter correction form.
- **`/demo/<sample>` (Instant Lab Demos)**:
  - Pre-configured diagnostic shortcuts (`diabetic`, `heart`, `ckd`, `thyroid`, `normal`).
- **`/run_prediction` (Multi-Disease XAI Dashboard)**:
  - Overall Health Risk Index Gauge (0–100).
  - Disease-specific risk probability cards.
  - Interactive SHAP feature attribution bar charts & narrative callouts.
  - LIME decision rule breakdown.
  - Clinical Decision Support (CDS) recommendations.
- **`/visualize` (5-Algorithm Model Analytics Workbench)**:
  - Dataset EDA charts (class distribution, glucose distribution).
  - Interactive Chart.js performance comparisons across all 5 algorithms.
  - Confusion matrix displays and feature importance rankings.

---

## 🗄️ Database & API Architecture

### Database Schema (SQLite3)
Managed via [`database/db.py`](database/db.py) and [`database/schema.sql`](database/schema.sql) stored at `database/healthcare.db`:
- **`patients`**: Patient records and timestamps.
- **`uploaded_reports`**: File metadata, file size, extraction status.
- **`extracted_parameters`**: Extracted biomarker values, raw text, units, confidence scores.
- **`predictions`**: Model predictions, disease type, probabilities, risk labels.
- **`risk_scores`**: Overall Health Risk Index scores and risk categories.
- **`explanations`**: SHAP and LIME top factors JSON and text narratives.
- **`model_performance`**: Accuracy, precision, recall, F1, ROC-AUC metric persistence.

### API Architecture
- **Web Routes**:
  - `GET /` — Home Page
  - `GET /predict` — Report Upload Form
  - `POST /upload` — Document parsing & parameter extraction endpoint
  - `GET /demo/<sample_name>` — Demo report loader
  - `POST /run_prediction` — Risk calculation, XAI execution & dashboard rendering
  - `GET /visualize` — Model analytics workbench
- **REST API Endpoint**:
  - `POST /api/predict` — Accepts JSON request body with patient biomarker values, returns full JSON payload containing disease probabilities, composite risk score, SHAP attributions, and LIME surrogate rules.

---

## 🚀 Setup & Execution

### 1. Environment Setup
```powershell
# Navigate to project root
cd c:\Users\krish\.gemini\antigravity-ide\scratch\EarlyMed-AI

# Create and activate virtual environment (optional)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 2. Model Training (Optional - Pre-trained models included)
```powershell
# Train Diabetes models
python src/train_diabetes.py

# Train Thyroid models
python src/train_thyroid.py
```

### 3. Run the Web Application
```powershell
python app/app.py
```

Open your browser at: **[http://127.0.0.1:5050/](http://127.0.0.1:5050/)**

---

## ⚠️ Clinical Disclaimer

This software framework is developed for **academic research, educational demonstration, and clinical decision support prototyping only**. Model outputs, SHAP/LIME explanations, and overall risk indices are statistical estimates derived from public research datasets and do not constitute a medical diagnosis, certified medical device, or prescription for clinical treatment.
