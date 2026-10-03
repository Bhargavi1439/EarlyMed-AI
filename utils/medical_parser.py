import re
from typing import Any, Dict, Optional, Tuple


# Regex patterns for clinical parameter detection
PATTERNS = {
    # ── Demographics ────────────────────────────────────────────────────────
    "age": [
        r"(?:patient\s+age|age\s*/\s*sex|age\s*:\s*|\bage\b)[^\d\n\r]{0,30}?(\d{1,3})\s*(?:years?|yrs?|y)?\b",
        r"\b(\d{1,3})\s*(?:years?|yrs?)\s*old\b",
    ],
    "sex": [
        r"(?:age\s*/\s*sex|gender\s*/\s*sex|sex\s*/\s*gender|gender|\bsex\b)[^\n\r]{0,50}?\b(male|female)\b",
        r"(?:gender|sex)\s*[:/]?\s*\b([mf])\b",
    ],

    # ── Diabetes & Metabolic ────────────────────────────────────────────────
    "glucose_fasting": [
        r"\b(?:fasting\s+blood\s+sugar|fasting\s+plasma\s+glucose|fasting\s+blood\s+glucose|fasting\s+glucose|glucose[,\s]+fasting(?:\s*\([^\)]*\))?(?:\s*,\s*plasma)?|fbs|fpg)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
    ],
    "glucose_pp": [
        r"\b(?:post[- ]prandial\s+blood\s+sugar|post[- ]prandial\s+blood\s+glucose|post[- ]prandial\s+glucose|postprandial\s+blood\s+sugar|postprandial\s+glucose|2\s*hours?\s*pp\s*glucose|pp\s+blood\s+sugar|pp\s+blood\s+glucose|pp\s+glucose|ppbs)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
    ],
    "glucose_random": [
        r"\b(?:random\s+blood\s+sugar|random\s+blood\s+glucose|random\s+plasma\s+glucose|random\s+glucose|rbs)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
    ],
    "glucose_plasma": [
        r"\b(?:blood\s+glucose|plasma\s+glucose|blood\s+sugar|serum\s+glucose)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
        r"(?:^|[\r\n|])\s*(?:serum\s+|plasma\s+|blood\s+)?glucose\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
    ],
    "glucose_eag": [
        r"\b(?:estimated\s+average\s+glucose(?:\s*\(eag\))?|eag)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l)?\b",
    ],
    "hba1c": [
        r"\b(?:glycated\s+hemoglobin|glycosylated\s+hemoglobin|glycohemoglobin|hba1c|a1c)\b(?:\s*\([^\)]*\))?[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(%|\b)",
    ],
    "insulin": [
        r"\b(?:2-?hour\s+serum\s+insulin|fasting\s+insulin|serum\s+insulin|insulin)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(µu/ml|uiu/ml|uu/ml|u/ml|pmol/l)?\b",
    ],
    "bmi": [
        r"\b(?:body\s+mass\s+index|bmi)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(kg/m2|kg/m²)?\b",
    ],
    "pregnancies": [
        r"\b(?:number\s+of\s+pregnancies|pregnancies|gravida|parity)\b[^\d\n\r]{0,50}?(\d+)\b",
    ],
    "skin_thickness": [
        r"\b(?:triceps\s+skin\s+fold\s+thickness|triceps\s+skinfold|skin\s+fold\s+thickness|skin\s+thickness)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mm)?\b",
    ],
    "diabetes_pedigree": [
        r"\b(?:diabetes\s+pedigree\s+function|pedigree\s+function|dpf)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\b",
    ],

    # ── Cardiovascular ──────────────────────────────────────────────────────
    "blood_pressure": [
        r"\b(?:blood\s+pressure|b\.?p\.?)[^\d\n\r]{0,30}?(\d{2,3})\s*[/xX]\s*(\d{2,3})\s*(?:mm\s*hg)?\b",
    ],
    "systolic_bp": [
        r"\b(?:systolic\s+blood\s+pressure|systolic\s+bp|systolic)[^\d\n\r]{0,30}?(\d{2,3})\s*(?:mm\s*hg)?\b",
    ],
    "diastolic_bp": [
        r"\b(?:diastolic\s+blood\s+pressure|diastolic\s+bp|diastolic)[^\d\n\r]{0,30}?(\d{2,3})\s*(?:mm\s*hg)?\b",
    ],
    "heart_rate": [
        r"\b(?:heart\s+rate|pulse\s+rate|pulse|resting\s+heart\s+rate|max\s+heart\s+rate|thalach)\b[^\d\n\r]{0,50}?(\d{2,3})\s*(?:[^\d\n\r]{0,15}?)(bpm|beats/min)?\b",
    ],
    "cholesterol": [
        r"\b(?:total\s+(?:serum\s+)?cholesterol|serum\s+cholesterol|cholesterol\s*,?\s*total)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
        r"(?:^|[\r\n|])\s*(?:serum\s+)?cholesterol\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "triglycerides": [
        r"\b(?:serum\s+triglycerides|triglycerides|tg)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "hdl": [
        r"(?<!non-)(?<!non\s)\b(?:hdl\s+cholesterol|high\s+density\s+lipoprotein|hdl-c|hdl)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "ldl": [
        r"(?<!vldl\s)(?<!v)\b(?:ldl\s+cholesterol(?:,\s*direct)?|low\s+density\s+lipoprotein|ldl-c|ldl)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "vldl": [
        r"\b(?:vldl\s+cholesterol|very\s+low\s+density\s+lipoprotein|vldl-c|vldl)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "non_hdl": [
        r"\b(?:non[- ]hdl\s+cholesterol|non[- ]hdl)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "chest_pain": [
        r"\b(?:chest\s+pain\s+type|chest\s+pain|angina\s+type)\b[^\d\n\r]{0,50}?(\d|typical|atypical|non-anginal|asymptomatic)\b",
    ],

    # ── Renal & Hematology ──────────────────────────────────────────────────
    "creatinine": [
        r"\b(?:serum\s+creatinine|creatinine)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|µmol/l|umol/l)?\b",
    ],
    "egfr": [
        r"\b(?:egfr(?:\s*\([^\)]*\))?|estimated\s+(?:glomerular\s+filtration\s+rate|gfr))\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)",
    ],
    "urea": [
        r"\b(?:serum\s+urea|blood\s+urea|\burea\b)[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "bun": [
        r"\b(?:blood\s+urea\s+nitrogen|bun)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|mmol/l)?\b",
    ],
    "uric_acid": [
        r"\b(?:serum\s+uric\s+acid|uric\s+acid)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(mg/dl|µmol/l|umol/l)?\b",
    ],
    "hemoglobin": [
        r"(?<!glycosylated\s)(?<!glycated\s)\b(?:serum\s+hemoglobin|hemoglobin(?!\s*variants)|haemoglobin|hb(?!\s*a1c)(?!\s*1c)(?!\s*a1)(?!\s*f))\b(?:\s*\([^\)]*\))?[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(g/dl|gm/dl|g/l)?\b",
    ],
    "albumin": [
        r"\b(?:serum\s+albumin|\balbumin\b)\b(?!\s*[/|]\s*globulin)[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(g/dl|gm/dl)?\b",
    ],
    "packed_cell_volume": [
        r"\b(?:packed\s+cell\s+volume|pcv|hematocrit|hct)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(%)?\b",
    ],
    "wbc": [
        r"\b(?:white\s+blood\s+cells?|white\s+blood\s+count|wbc|total\s+leukocyte\s+count|tlc)\b[^\d\n\r]{0,50}?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(/µl|/ul|cells/cumm|cells/mm3|x10\^3/ul)?\b",
    ],
    "rbc": [
        r"\b(?:red\s+blood\s+cells?|red\s+blood\s+count|rbc)\b[^\d\n\r]{0,50}?(\d+(?:\.\d+)?)\s*(?:[^\d\n\r]{0,15}?)(million/µl|million/ul|x10\^6/ul|m/ul)?\b",
    ],
    "specific_gravity": [
        r"\b(?:specific\s+gravity|urine\s+specific\s+gravity|sg)\b[^\d\n\r]{0,50}?(1(?:\.\d{2,3})?)\b",
    ],
}

PARAMETER_METADATA = {
    "age": {"label": "Age", "unit": "years", "range": (1, 120)},
    "sex": {"label": "Gender/Sex", "unit": "", "range": (0, 1)},
    "glucose": {"label": "Glucose (Plasma/Blood)", "unit": "mg/dL", "range": (40, 450)},
    "glucose_fasting": {"label": "Fasting Blood Sugar (FBS)", "unit": "mg/dL", "range": (40, 450)},
    "glucose_pp": {"label": "Post-Prandial Blood Sugar (PPBS)", "unit": "mg/dL", "range": (40, 450)},
    "glucose_eag": {"label": "Estimated Average Glucose (eAG)", "unit": "mg/dL", "range": (40, 450)},
    "systolic_bp": {"label": "Systolic Blood Pressure", "unit": "mmHg", "range": (60, 240)},
    "diastolic_bp": {"label": "Diastolic Blood Pressure", "unit": "mmHg", "range": (40, 150)},
    "bmi": {"label": "Body Mass Index (BMI)", "unit": "kg/m²", "range": (10.0, 70.0)},
    "hba1c": {"label": "HbA1c", "unit": "%", "range": (3.5, 18.0)},
    "insulin": {"label": "Serum Insulin", "unit": "µU/mL", "range": (1.0, 900.0)},
    "pregnancies": {"label": "Pregnancies", "unit": "", "range": (0, 20)},
    "skin_thickness": {"label": "Triceps Skin Fold", "unit": "mm", "range": (1.0, 100.0)},
    "diabetes_pedigree": {"label": "Diabetes Pedigree Function", "unit": "", "range": (0.05, 2.5)},
    "cholesterol": {"label": "Serum Cholesterol (Total)", "unit": "mg/dL", "range": (80, 600)},
    "triglycerides": {"label": "Triglycerides", "unit": "mg/dL", "range": (30, 800)},
    "hdl": {"label": "HDL Cholesterol", "unit": "mg/dL", "range": (10, 120)},
    "ldl": {"label": "LDL Cholesterol", "unit": "mg/dL", "range": (20, 300)},
    "vldl": {"label": "VLDL Cholesterol", "unit": "mg/dL", "range": (5.0, 100.0)},
    "non_hdl": {"label": "Non-HDL Cholesterol", "unit": "mg/dL", "range": (30.0, 300.0)},
    "heart_rate": {"label": "Maximum / Resting Heart Rate", "unit": "bpm", "range": (40, 220)},
    "creatinine": {"label": "Serum Creatinine", "unit": "mg/dL", "range": (0.2, 20.0)},
    "urea": {"label": "Serum Urea", "unit": "mg/dL", "range": (5.0, 300.0)},
    "bun": {"label": "Blood Urea Nitrogen (BUN)", "unit": "mg/dL", "range": (3.0, 150.0)},
    "egfr": {"label": "Estimated GFR (eGFR)", "unit": "mL/min/1.73m²", "range": (5.0, 200.0)},
    "uric_acid": {"label": "Serum Uric Acid", "unit": "mg/dL", "range": (1.0, 15.0)},
    "hemoglobin": {"label": "Hemoglobin", "unit": "g/dL", "range": (3.0, 22.0)},
    "albumin": {"label": "Albumin", "unit": "g/dL", "range": (0.0, 6.0)},
    "packed_cell_volume": {"label": "Packed Cell Volume (PCV)", "unit": "%", "range": (10.0, 65.0)},
    "wbc": {"label": "White Blood Cell Count", "unit": "/µL", "range": (1000, 40000)},
    "rbc": {"label": "Red Blood Cell Count", "unit": "M/µL", "range": (1.5, 8.5)},
    "specific_gravity": {"label": "Specific Gravity", "unit": "", "range": (1.000, 1.040)},
}


def normalize_unit(param_key: str, raw_val: float, detected_unit: Optional[str]) -> Tuple[float, str, Optional[str]]:
    """
    Safely convert clinical units to standard units expected by ML models.
    Never invent values.
    Returns: (normalized_value, standard_unit, conversion_note)
    """
    detected_unit = (detected_unit or "").lower().replace(" ", "").replace("·", "")
    conversion_note = None

    # Glucose conversion: mmol/L to mg/dL
    if "glucose" in param_key:
        if "mmol" in detected_unit or (raw_val < 30 and detected_unit != "mg/dl"):
            # Physiological plausibility check for mmol/L
            if raw_val <= 35:
                conv_val = round(raw_val * 18.0182, 1)
                conversion_note = f"Converted from {raw_val} mmol/L to {conv_val} mg/dL (factor 18.0182)"
                return conv_val, "mg/dL", conversion_note
        return raw_val, "mg/dL", conversion_note

    # Creatinine conversion: µmol/L to mg/dL
    if param_key == "creatinine":
        if "umol" in detected_unit or "µmol" in detected_unit or raw_val > 30:
            conv_val = round(raw_val / 88.4, 2)
            conversion_note = f"Converted from {raw_val} µmol/L to {conv_val} mg/dL (divided by 88.4)"
            return conv_val, "mg/dL", conversion_note
        return raw_val, "mg/dL", conversion_note

    # Uric Acid conversion: µmol/L to mg/dL
    if param_key == "uric_acid":
        if "umol" in detected_unit or "µmol" in detected_unit or raw_val > 50:
            conv_val = round(raw_val / 59.48, 2)
            conversion_note = f"Converted from {raw_val} µmol/L to {conv_val} mg/dL (divided by 59.48)"
            return conv_val, "mg/dL", conversion_note
        return raw_val, "mg/dL", conversion_note

    # Cholesterol conversion: mmol/L to mg/dL
    if param_key in {"cholesterol", "hdl", "ldl", "vldl", "non_hdl"}:
        if "mmol" in detected_unit or (raw_val < 20 and detected_unit != "mg/dl"):
            conv_val = round(raw_val * 38.67, 1)
            conversion_note = f"Converted from {raw_val} mmol/L to {conv_val} mg/dL (factor 38.67)"
            return conv_val, "mg/dL", conversion_note
        return raw_val, "mg/dL", conversion_note

    # Hemoglobin conversion: g/L to g/dL
    if param_key == "hemoglobin":
        if "g/l" in detected_unit or raw_val > 30:
            conv_val = round(raw_val / 10.0, 1)
            conversion_note = f"Converted from {raw_val} g/L to {conv_val} g/dL (divided by 10)"
            return conv_val, "g/dL", conversion_note
        return raw_val, "g/dL", conversion_note

    # Standard unit from dictionary
    std_unit = PARAMETER_METADATA.get(param_key, {}).get("unit", detected_unit)
    return raw_val, std_unit, conversion_note


def parse_medical_report_text(report_text: str) -> Dict[str, Any]:
    """
    Extract clinical parameters from raw text using medical terminology patterns.
    Strictly preserves privacy (no name, phone, or address stored).
    """
    extracted = {}
    notes = []

    # 1. Process Blood Pressure (combined Systolic/Diastolic)
    for pat in PATTERNS["blood_pressure"]:
        match = re.search(pat, report_text, re.IGNORECASE)
        if match and "systolic_bp" not in extracted:
            sys_val = float(match.group(1))
            dia_val = float(match.group(2))
            raw_unit = "mmHg"
            source = match.group(0).replace("\n", " ").strip()
            extracted["systolic_bp"] = {
                "param_key": "systolic_bp",
                "label": "Systolic Blood Pressure",
                "raw_value": str(match.group(1)),
                "value": sys_val,
                "unit": raw_unit,
                "normalized_value": sys_val,
                "standard_unit": "mmHg",
                "conversion_note": None,
                "source_text": source,
                "confidence": 0.95,
            }
            extracted["diastolic_bp"] = {
                "param_key": "diastolic_bp",
                "label": "Diastolic Blood Pressure",
                "raw_value": str(match.group(2)),
                "value": dia_val,
                "unit": raw_unit,
                "normalized_value": dia_val,
                "standard_unit": "mmHg",
                "conversion_note": None,
                "source_text": source,
                "confidence": 0.95,
            }
            break

    # 2. Extract Demographic Sex
    if "sex" not in extracted:
        for pat in PATTERNS["sex"]:
            match = re.search(pat, report_text, re.IGNORECASE)
            if match:
                s_str = match.group(1).lower()
                sex_num = 1 if s_str in {"male", "m"} else 0
                source = match.group(0).replace("\n", " ").strip()
                extracted["sex"] = {
                    "param_key": "sex",
                    "label": "Gender / Sex",
                    "raw_value": match.group(1),
                    "value": sex_num,
                    "unit": "",
                    "normalized_value": sex_num,
                    "standard_unit": "1=Male, 0=Female",
                    "conversion_note": None,
                    "source_text": source,
                    "confidence": 0.98,
                }
                break

    # 3. Extract Specific Glucose Measurements
    glucose_types = [
        ("glucose_fasting", "Fasting Blood Sugar (FBS)"),
        ("glucose_pp", "Post-Prandial Blood Sugar (PPBS)"),
        ("glucose_random", "Random Blood Sugar"),
        ("glucose_plasma", "Blood Glucose"),
        ("glucose_eag", "Estimated Average Glucose (eAG)"),
    ]
    for gkey, glabel in glucose_types:
        for pat in PATTERNS.get(gkey, []):
            match = re.search(pat, report_text, re.IGNORECASE)
            if match and gkey not in extracted:
                val = float(match.group(1))
                unit = match.group(2) if len(match.groups()) >= 2 and match.group(2) else "mg/dL"
                norm_val, std_unit, conv_note = normalize_unit("glucose", val, unit)
                source = match.group(0).replace("\n", " ").strip()
                extracted[gkey] = {
                    "param_key": gkey,
                    "label": glabel,
                    "raw_value": match.group(1),
                    "value": val,
                    "unit": unit,
                    "normalized_value": norm_val,
                    "standard_unit": std_unit,
                    "conversion_note": conv_note,
                    "source_text": source,
                    "confidence": 0.95,
                }
                if conv_note:
                    notes.append(conv_note)
                break

    # Assign primary "glucose" for ML models (priority: fasting -> plasma/random -> pp -> eag)
    if "glucose" not in extracted:
        primary_source = None
        if "glucose_fasting" in extracted:
            primary_source = extracted["glucose_fasting"]
        elif "glucose_plasma" in extracted:
            primary_source = extracted["glucose_plasma"]
        elif "glucose_random" in extracted:
            primary_source = extracted["glucose_random"]
        elif "glucose_pp" in extracted:
            primary_source = extracted["glucose_pp"]
        elif "glucose_eag" in extracted:
            primary_source = extracted["glucose_eag"]

        if primary_source:
            extracted["glucose"] = {
                "param_key": "glucose",
                "label": "Glucose (Plasma/Blood)",
                "raw_value": primary_source["raw_value"],
                "value": primary_source["value"],
                "unit": primary_source["unit"],
                "normalized_value": primary_source["normalized_value"],
                "standard_unit": primary_source["standard_unit"],
                "conversion_note": primary_source.get("conversion_note"),
                "source_text": primary_source["source_text"],
                "confidence": primary_source.get("confidence", 0.95),
            }

    # 4. Extract other clinical parameters
    for param_key, pat_list in PATTERNS.items():
        if param_key in {
            "blood_pressure",
            "sex",
            "glucose_fasting",
            "glucose_pp",
            "glucose_random",
            "glucose_plasma",
            "glucose_eag",
        }:
            continue
        if param_key in extracted:
            continue

        meta = PARAMETER_METADATA.get(param_key, {"label": param_key.replace("_", " ").title(), "unit": ""})

        for pat in pat_list:
            match = re.search(pat, report_text, re.IGNORECASE)
            if match:
                val_str = match.group(1).replace(",", "")
                try:
                    val = float(val_str)
                except ValueError:
                    continue

                # Qualitative sanity check for urine test interference
                matched_text = match.group(0).lower()
                if any(neg in matched_text for neg in ["absent", "negative", "nil"]):
                    continue

                unit = match.group(2) if len(match.groups()) >= 2 and match.group(2) else meta.get("unit", "")
                norm_val, std_unit, conv_note = normalize_unit(param_key, val, unit)
                source = match.group(0).replace("\n", " ").strip()

                extracted[param_key] = {
                    "param_key": param_key,
                    "label": meta["label"],
                    "raw_value": match.group(1),
                    "value": val,
                    "unit": unit,
                    "normalized_value": norm_val,
                    "standard_unit": std_unit,
                    "conversion_note": conv_note,
                    "source_text": source,
                    "confidence": 0.92,
                }
                if conv_note:
                    notes.append(conv_note)
                break

    # Determine fields found vs not found against standard supported keys
    all_supported_keys = list(PARAMETER_METADATA.keys())
    fields_found = [k for k in all_supported_keys if k in extracted]
    fields_missing = [k for k in all_supported_keys if k not in extracted]

    return {
        "extracted_parameters": extracted,
        "fields_found": fields_found,
        "fields_missing": fields_missing,
        "notes": notes,
    }
