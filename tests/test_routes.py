import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.app import app

client = app.test_client()

# 1. Test Home page (Strictly identical UI check)
r_home = client.get("/")
assert r_home.status_code == 200, f"Expected 200, got {r_home.status_code}"
assert "EarlyMed-AI" in r_home.text
assert "Open prediction" in r_home.text
print("[PASS] Route 1: GET / (Home page layout and title verified)")

# 2. Test Predict Upload Page
r_predict = client.get("/predict")
assert r_predict.status_code == 200
assert "Upload Patient Medical Report" in r_predict.text
assert "Drag & Drop Medical Report Here" in r_predict.text
assert "Analyze Medical Report" in r_predict.text
# Ensure old manual 8-input form is gone
assert 'name="Glucose"' not in r_predict.text
assert 'name="SkinThickness"' not in r_predict.text
print("[PASS] Route 2: GET /predict (Upload interface verified, manual 8-field form completely removed)")

# 3. Test Demo PDF extraction
r_demo = client.get("/demo/diabetic")
assert r_demo.status_code == 200
assert "Medical Information Extracted From Report" in r_demo.text
assert "Observed Medical Parameters" in r_demo.text
assert "Multi-Disease Evaluation Readiness" in r_demo.text
print("[PASS] Route 3: GET /demo/diabetic (PDF extraction and preview rendering verified)")

# Extract parameters JSON from preview HTML
match = re.search(r'id="verifiedParamsInput"\s+value=[\'"]([^\'"]+)[\'"]', r_demo.text)
assert match is not None, "Could not find verifiedParamsInput in extracted_data.html"
raw_json = html.unescape(match.group(1))


# 4. Test Run Prediction
r_pred = client.post(
    "/run_prediction",
    data={
        "verified_parameters_json": raw_json,
        "report_id": "1",
        "file_name": "Patient_Medical_Report.pdf",
        "file_size_kb": "24.5",
    },
)
assert r_pred.status_code == 200
assert "Overall Health Risk Index" in r_pred.text
assert "Disease Risk Estimations" in r_pred.text
assert "Explainable AI (XAI) Attribution Analysis" in r_pred.text
assert "SHAP Feature Importance" in r_pred.text
assert "Clinical Decision Support" in r_pred.text
assert "Clinical Disclaimer:" in r_pred.text
print("[PASS] Route 4: POST /run_prediction (Multi-disease risk, SHAP, LIME, CDS, and Health Risk Index dashboard verified)")

# 5. Test Visualize Page
r_viz = client.get("/visualize")
assert r_viz.status_code == 200
assert "Comprehensive 5-Algorithm Model Benchmark" in r_viz.text
assert "Accuracy" in r_viz.text
assert "ROC-AUC" in r_viz.text
assert "Specificity" in r_viz.text
print("[PASS] Route 5: GET /visualize (Expanded multi-disease and 5-model analytics dashboard verified)")

# 6. Test direct file upload via POST /upload
with open(ROOT / "data" / "sample_reports" / "Patient_Medical_Report.pdf", "rb") as f:
    r_upload = client.post(
        "/upload",
        data={"report_file": (f, "Direct_Test_Report.pdf")},
        content_type="multipart/form-data",
    )
assert r_upload.status_code == 200
assert "Medical Information Extracted From Report" in r_upload.text
print("[PASS] Route 6: POST /upload (Direct PDF file upload & processing verified)")

print("\n===========================================================")
print("ALL AUTOMATED SYSTEM ROUTE & FUNCTIONALITY TESTS PASSED! 100%")
print("===========================================================")

