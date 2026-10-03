import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent / "healthcare.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables using schema.sql."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def save_report_and_extraction(
    filename: str,
    file_type: str,
    file_size_kb: float,
    extracted_params: Dict[str, Any],
) -> int:
    """Save report record and extracted clinical parameters. Returns report_id."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create patient record (anonymized)
    cursor.execute("INSERT INTO patients DEFAULT VALUES")
    patient_id = cursor.lastrowid

    # Create uploaded report record
    cursor.execute(
        """
        INSERT INTO uploaded_reports (patient_id, filename, file_type, file_size_kb, extraction_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (patient_id, filename, file_type, file_size_kb, "success"),
    )
    report_id = cursor.lastrowid

    # Insert parameters
    for key, p in extracted_params.items():
        cursor.execute(
            """
            INSERT INTO extracted_parameters (report_id, parameter_name, raw_value, normalized_value, unit, confidence, source_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                key,
                str(p.get("raw_value", "")),
                p.get("normalized_value"),
                p.get("standard_unit", ""),
                p.get("confidence", 1.0),
                p.get("source_text", ""),
            ),
        )

    conn.commit()
    conn.close()
    return report_id


def save_predictions_and_explanations(
    report_id: int,
    prediction_results: Dict[str, Any],
    shap_explanations: Dict[str, Any],
) -> None:
    """Save disease predictions, overall risk index, and XAI explanations."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Save predictions
    disease_results = prediction_results.get("disease_results", {})
    for d_key, res in disease_results.items():
        if res.get("evaluated") and res.get("probability") is not None:
            cursor.execute(
                """
                INSERT INTO predictions (report_id, disease, model_name, probability, risk_label)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    res.get("disease", d_key),
                    res.get("model_name", "ML Model"),
                    res.get("probability"),
                    res.get("risk_label"),
                ),
            )

    # 2. Save overall risk score
    overall = prediction_results.get("overall_health_risk_index", {})
    if overall.get("score") is not None:
        cursor.execute(
            """
            INSERT INTO risk_scores (report_id, overall_risk, category)
            VALUES (?, ?, ?)
            """,
            (report_id, overall.get("score"), overall.get("category")),
        )

    # 3. Save explanations
    for d_key, expl in shap_explanations.items():
        top_contribs = expl.get("top_contributions", [])
        narrative = " ".join(expl.get("summary_bullets", []))
        cursor.execute(
            """
            INSERT INTO explanations (report_id, disease, method, top_factors_json, narrative)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                report_id,
                d_key,
                "SHAP",
                json.dumps(top_contribs),
                narrative,
            ),
        )

    conn.commit()
    conn.close()


# Auto-initialize database on import
init_db()
