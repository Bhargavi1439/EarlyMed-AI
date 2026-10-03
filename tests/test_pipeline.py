import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.medical_parser import parse_medical_report_text

from utils.validator import validate_extracted_data
from src.multi_disease_predictor import MultiDiseasePredictor
from explainability.shap_explainer import explain_with_shap
from explainability.lime_explainer import explain_with_lime
from src.decision_support import generate_clinical_decision_support

sample_report = """
Patient Age: 55 Years
Gender: Female
Body Mass Index (BMI): 31.2 kg/m2
Blood Pressure: 142/90 mmHg
Heart Rate: 84 bpm
Fasting Blood Sugar: 175 mg/dL
HbA1c: 7.6 %
Serum Cholesterol: 240 mg/dL
Serum Creatinine: 1.4 mg/dL
Blood Urea: 42 mg/dL
Hemoglobin: 13.1 g/dL
"""

parser_res = parse_medical_report_text(sample_report)
val_res = validate_extracted_data(parser_res["extracted_parameters"])
predictor = MultiDiseasePredictor()
preds = predictor.predict_all(val_res["parameters"], val_res["model_readiness"])

print("Predictions:")
for d, res in preds["disease_results"].items():
    print(f"  {d}: evaluated={res['evaluated']}, prob={res.get('probability_pct')}% ({res.get('risk_label')}) via {res.get('model_name')}")

overall = preds["overall_health_risk_index"]
print(f"Overall Health Risk Index: {overall['score']}/100 ({overall['category']})")

# Test explainability on Diabetes
d_res = preds["disease_results"]["diabetes"]
raw_vals = {k: v["normalized_value"] for k, v in val_res["parameters"].items()}
shap_res = explain_with_shap(predictor.diabetes_model, d_res["processed_vector"], d_res["feature_names"], raw_feature_values=raw_vals)
lime_res = explain_with_lime(predictor.diabetes_model, d_res["processed_vector"], d_res["feature_names"], raw_feature_values=raw_vals)

print("\nTop SHAP contributions for Diabetes:")
for c in shap_res["top_contributions"][:3]:
    print(f"  {c['feature']}: {c['shap_value']} ({c['impact_direction']})")

print("\nLIME local surrogate rules:")
for r in lime_res["rules"][:3]:
    print(f"  {r['condition']} -> weight: {r['weight']} ({r['impact_direction']})")

cds = generate_clinical_decision_support(preds["disease_results"], {"diabetes": shap_res}, overall)
print("\nCDS Title:", cds["title"])
print("CDS Suggestions count:", len(cds["suggested_follow_up"]))
print("\n[SUCCESS] Test pipeline completed successfully!")
