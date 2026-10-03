# Pima Indians Diabetes dataset

File: `data/raw/diabetes.csv`

Source: public Pima Indians Diabetes Database (UCI / commonly redistributed; this copy was obtained from the Plotly datasets mirror).

Original study population: women of Pima Indian heritage near Phoenix, Arizona. The outcome is whether diabetes was diagnosed according to WHO criteria used in that study.

## Columns

| Column | Meaning |
|---|---|
| Pregnancies | Number of times pregnant |
| Glucose | Plasma glucose concentration (2-hour OGTT), mg/dL |
| BloodPressure | Diastolic blood pressure, mm Hg |
| SkinThickness | Triceps skin fold thickness, mm |
| Insulin | 2-hour serum insulin, µU/mL |
| BMI | Body mass index |
| DiabetesPedigreeFunction | Diabetes pedigree function |
| Age | Age in years |
| Outcome | 0 = no diabetes, 1 = diabetes |

Zeros in Glucose, BloodPressure, SkinThickness, Insulin, and BMI are treated as missing during preprocessing. Pregnancies = 0 is valid.
