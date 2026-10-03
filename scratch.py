import os

html_content = """{% extends "base.html" %}
{% block title %}Healthcare Analytics Dashboard{% endblock %}
{% block content %}
<script src="{{ url_for('static', filename='js/chart.umd.js') }}"></script>

<style>
/* Widen container */
main.wrap { max-width: 1400px; } 

.dashboard-container {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 1.5rem;
  position: sticky;
  top: 1.5rem;
  height: max-content;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.sidebar h3 {
  margin-top: 0;
  font-size: 1.15rem;
  color: var(--ink);
  margin-bottom: 1.2rem;
}

.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-nav li { margin-bottom: 0.5rem; }
.sidebar-nav a {
  text-decoration: none;
  color: var(--muted);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 0.95rem;
}
.sidebar-nav a:hover {
  background: var(--notice);
  color: var(--accent-dark);
}
.sidebar-nav a.active-nav {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
}

.dashboard-content {
  flex-grow: 1;
  min-width: 0;
}

.dashboard-section {
  display: none;
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* Quadrant Card Themes */
.quadrant-card {
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.04);
}
.quadrant-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid rgba(0,0,0,0.05);
  padding-bottom: 1rem;
}
.quadrant-num {
  width: 40px; height: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; font-weight: 800; color: #fff;
  flex-shrink: 0;
}
.quadrant-header h2 { margin: 0; font-size: 1.6rem; color: #1e293b; }
.quadrant-header p { margin: 0; font-size: 0.9rem; color: #64748b; font-weight: 500; }

.q-blue { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1px solid #bfdbfe; }
.q-blue .quadrant-num { background: #3b82f6; }
.q-pink { background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%); border: 1px solid #fecdd3; }
.q-pink .quadrant-num { background: #f43f5e; }
.q-green { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; }
.q-green .quadrant-num { background: #10b981; }
.q-purple { background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); border: 1px solid #e9d5ff; }
.q-purple .quadrant-num { background: #a855f7; }

/* Internal Grid/Layouts */
.q-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.q-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }

.stat-box {
  background: rgba(255,255,255,0.7);
  border-radius: 12px;
  padding: 1.2rem;
  border: 1px solid rgba(255,255,255,0.9);
  text-align: center;
}
.stat-val { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0.3rem 0; }
.stat-lbl { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #64748b; }

.chart-wrapper {
  background: rgba(255,255,255,0.7);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(255,255,255,0.9);
}
.chart-container { position: relative; height: 260px; width: 100%; }

/* Predict Form embedded */
.predict-form-container {
  background: rgba(255,255,255,0.8);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255,255,255,0.9);
}
.upload-zone {
  border: 2px dashed #a855f7;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  background: rgba(168, 85, 247, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}
.upload-zone:hover { background: rgba(168, 85, 247, 0.1); }
</style>

<div class="dashboard-container">
  
  <aside class="sidebar">
    <h3>Dashboard Menu</h3>
    <ul class="sidebar-nav">
      <li><a href="#overview-tab" class="nav-link" onclick="switchDashboardNav(event, 'overview-tab')">📊 Health Overview</a></li>
      <li><a href="#risk-factor-tab" class="nav-link" onclick="switchDashboardNav(event, 'risk-factor-tab')">📈 Risk Factor Analysis</a></li>
      <li><a href="#models-tab" class="nav-link" onclick="switchDashboardNav(event, 'models-tab')">🤖 Model Performance</a></li>
      <li><a href="#predict-tab" class="nav-link" onclick="switchDashboardNav(event, 'predict-tab')">🩺 Risk Prediction</a></li>
    </ul>
  </aside>

  <div class="dashboard-content">

    <!-- 1. Health Overview (Blue) -->
    <div id="overview-tab" class="dashboard-section quadrant-card q-blue">
      <div class="quadrant-header">
        <div class="quadrant-num">1</div>
        <div>
          <h2>Health Overview</h2>
          <p>Get a quick understanding of the datasets and overall health distributions.</p>
        </div>
      </div>
      
      <div class="q-grid-2" style="margin-bottom: 1.5rem;">
        <div style="display:flex; flex-direction: column; gap: 0.8rem;">
          <div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">
            <span style="font-size: 2rem;">🩸</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Diabetes Dataset</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_rows }} records • 8 features</div>
            </div>
          </div>
          <div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">
            <span style="font-size: 2rem;">❤️</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Heart Disease Dataset</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_heart_rows }} records • 13 features</div>
            </div>
          </div>
          <div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">
            <span style="font-size: 2rem;">🫘</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Kidney Disease Dataset</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_kidney_rows }} records • 13 features</div>
            </div>
          </div>
        </div>
        
        <div class="chart-wrapper">
          <h3 style="margin-top:0; font-size: 1rem; text-align:center;">Disease Distribution (Diabetes)</h3>
          <div class="chart-container" style="height: 220px;">
            <canvas id="classDistChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Risk Factor Analysis (Pink) -->
    <div id="risk-factor-tab" class="dashboard-section quadrant-card q-pink">
      <div class="quadrant-header">
        <div class="quadrant-num">2</div>
        <div>
          <h2>Risk Factor Analysis (EDA)</h2>
          <p>Explore how different health factors are related to disease risk across datasets.</p>
        </div>
      </div>

      <div class="q-grid-2">
        <div class="chart-wrapper">
          <h3 style="margin-top:0; font-size: 1rem; text-align:center;">Feature Profiles by Outcome</h3>
          <div class="chart-container">
            <canvas id="featureMeansChart"></canvas>
          </div>
        </div>
        <div class="chart-wrapper">
          <h3 style="margin-top:0; font-size: 1rem; text-align:center;">Glucose vs Diabetes Risk</h3>
          <div class="chart-container">
            <canvas id="glucoseClassChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Model Performance (Green) -->
    <div id="models-tab" class="dashboard-section quadrant-card q-green">
      <div class="quadrant-header">
        <div class="quadrant-num">3</div>
        <div>
          <h2>Model Performance</h2>
          <p>Compare accuracy, precision, and other metrics of different machine learning models.</p>
        </div>
      </div>

      <div class="chart-wrapper" style="margin-bottom: 2rem;">
        <h3 style="margin-top:0; font-size: 1rem; text-align:center;">Model Comparison Visualizations</h3>
        <div class="chart-container" style="height: 280px;">
          <canvas id="modelCompChart"></canvas>
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.7); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.9);">
        <h3 style="margin-top:0; font-size: 1.1rem;">Detailed Model Metrics</h3>
        
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 2px solid #bbf7d0; padding-bottom: 0.8rem;">
          <button type="button" class="demo-chip active" id="tab-btn-diabetes" onclick="switchDiseaseTab('diabetes')" style="background: #10b981; border-color: #10b981; color: #fff;">Diabetes</button>
          <button type="button" class="demo-chip" id="tab-btn-heart" onclick="switchDiseaseTab('heart')" style="background: #fff; border-color: #10b981; color: #10b981;">Heart Disease</button>
          <button type="button" class="demo-chip" id="tab-btn-kidney" onclick="switchDiseaseTab('kidney')" style="background: #fff; border-color: #10b981; color: #10b981;">Kidney Disease</button>
        </div>

        <div id="table-diabetes" class="disease-table-container">
          <table class="data-table" style="width: 100%; text-align: left;">
            <thead style="background: rgba(16,185,129,0.1);">
              <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th></tr>
            </thead>
            <tbody>
              {% for m_name, m_mets in diab_metrics.items() %}
                <tr>
                  <td style="padding: 0.6rem 0.4rem;"><strong>{{ m_name|replace('_', ' ')|title }}</strong></td>
                  <td>{{ "%.1f"|format(m_mets.accuracy * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.precision * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.recall * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.f1 * 100) }}%</td>
                  <td><strong>{{ "%.1f"|format(m_mets.roc_auc * 100) }}%</strong></td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        
        <div id="table-heart" class="disease-table-container" style="display: none;">
          <table class="data-table" style="width: 100%; text-align: left;">
            <thead style="background: rgba(16,185,129,0.1);">
              <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th></tr>
            </thead>
            <tbody>
              {% for m_name, m_mets in heart_metrics.items() %}
                <tr>
                  <td style="padding: 0.6rem 0.4rem;"><strong>{{ m_name|replace('_', ' ')|title }}</strong></td>
                  <td>{{ "%.1f"|format(m_mets.accuracy * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.precision * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.recall * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.f1 * 100) }}%</td>
                  <td><strong>{{ "%.1f"|format(m_mets.roc_auc * 100) }}%</strong></td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>

        <div id="table-kidney" class="disease-table-container" style="display: none;">
          <table class="data-table" style="width: 100%; text-align: left;">
            <thead style="background: rgba(16,185,129,0.1);">
              <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th></tr>
            </thead>
            <tbody>
              {% for m_name, m_mets in kidney_metrics.items() %}
                <tr>
                  <td style="padding: 0.6rem 0.4rem;"><strong>{{ m_name|replace('_', ' ')|title }}</strong></td>
                  <td>{{ "%.1f"|format(m_mets.accuracy * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.precision * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.recall * 100) }}%</td>
                  <td>{{ "%.1f"|format(m_mets.f1 * 100) }}%</td>
                  <td><strong>{{ "%.1f"|format(m_mets.roc_auc * 100) }}%</strong></td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 4. Individual Risk Prediction (Purple) -->
    <div id="predict-tab" class="dashboard-section quadrant-card q-purple">
      <div class="quadrant-header">
        <div class="quadrant-num">4</div>
        <div>
          <h2>Individual Risk Prediction</h2>
          <p>Upload a patient health report to extract parameters and run multi-disease risk prediction.</p>
        </div>
      </div>
      <div class="predict-form-container">
        <form id="uploadForm" method="post" action="{{ url_for('upload_report') }}" enctype="multipart/form-data">
          <div class="upload-zone" id="dropZone">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📄</div>
            <p style="font-weight: 700; color: #1e293b; margin: 0;">Drag & Drop Medical Report Here</p>
            <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">or click to browse (PDF/PNG/JPG)</p>
            <input type="file" id="fileInput" name="report_file" accept=".pdf,.png,.jpg,.jpeg" style="display: none;">
            <button type="button" class="button" id="browseBtn" style="pointer-events: auto; background: #a855f7;">Browse Report File</button>
          </div>

          <div id="fileCard" style="display: none; align-items: center; justify-content: space-between; background: #fff; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #e9d5ff;">
            <div style="display:flex; align-items: center; gap: 1rem;">
              <span style="font-size: 1.5rem;">📋</span>
              <div>
                <div id="fileName" style="font-weight: 600; color:#1e293b;">Report.pdf</div>
                <div id="fileSize" style="font-size: 0.8rem; color:#64748b;">0 KB</div>
              </div>
            </div>
            <button type="button" id="removeFileBtn" style="background: none; border: none; color: #ef4444; cursor: pointer; font-weight: 600;">Remove</button>
          </div>

          <div id="progressContainer" class="progress-bar-container" style="margin-top: 1rem; display:none;">
            <div id="progressBar" class="progress-bar-fill" style="background:#a855f7;"></div>
          </div>

          <div style="margin-top: 1.5rem;">
            <button type="submit" id="analyzeBtn" class="button" style="width: 100%; padding: 1rem; font-size: 1.1rem; background: #7e22ce;" disabled>
              🔍 Predict Health Risk
            </button>
          </div>
        </form>
        
        <div style="margin-top: 2rem; border-top: 1px solid #e9d5ff; padding-top: 1rem;">
          <p style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Try a Demo Report:</p>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <a href="{{ url_for('load_demo_report', sample_name='diabetic') }}" class="button" style="background: #fff; color: #a855f7; border: 1px solid #a855f7;">📄 Sample High Risk</a>
            <a href="{{ url_for('load_demo_report', sample_name='normal') }}" class="button" style="background: #fff; color: #a855f7; border: 1px solid #a855f7;">📄 Sample Low Risk</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  // JSON Data Injection
  const classCountsData = JSON.parse('{{ class_counts_json|safe }}');
  const featureMeansData = JSON.parse('{{ feature_means_json|safe }}');
  const modelChartData = JSON.parse('{{ model_chart_json|safe }}');
  const glucoseByClassData = JSON.parse('{{ hist_glucose_by_class_json|safe }}');
  const glucoseBins = JSON.parse('{{ glucose_bins_json|safe }}');
  const confusionData = JSON.parse('{{ confusion_json|safe }}');

  // Sidebar Tab Navigation
  function switchDashboardNav(event, sectionId) {
    if (event) event.preventDefault();
    document.querySelectorAll('.dashboard-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(el => el.classList.remove('active-nav'));
    
    document.getElementById(sectionId).style.display = 'block';
    if (event) {
      event.target.classList.add('active-nav');
    } else {
      const activeLink = document.querySelector(`.sidebar-nav a[href="#${sectionId}"]`);
      if (activeLink) activeLink.classList.add('active-nav');
    }
  }

  // Disease Table Nested Tab Navigation
  function switchDiseaseTab(disease) {
    document.querySelectorAll('.disease-table-container').forEach(el => el.style.display = 'none');
    document.querySelectorAll('#models-tab .demo-chip').forEach(el => {
      el.style.background = '#fff';
      el.style.color = '#10b981';
    });

    const target = document.getElementById(`table-${disease}`);
    const btn = document.getElementById(`tab-btn-${disease}`);
    if (target) target.style.display = 'block';
    if (btn) {
      btn.style.background = '#10b981';
      btn.style.color = '#fff';
    }
  }

  // Predict Form Logic
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseBtn');
  const fileCard = document.getElementById('fileCard');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const uploadForm = document.getElementById('uploadForm');
  const progressContainer = document.getElementById('progressContainer');
  const progressBar = document.getElementById('progressBar');

  if(browseBtn) {
    browseBtn.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });
    dropZone.addEventListener('click', () => { fileInput.click(); });
    ['dragenter', 'dragover'].forEach(ev => dropZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dropZone.style.background = 'rgba(168, 85, 247, 0.15)'; }));
    ['dragleave', 'drop'].forEach(ev => dropZone.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); dropZone.style.background = 'rgba(168, 85, 247, 0.05)'; }));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault(); e.stopPropagation(); dropZone.style.background = 'rgba(168, 85, 247, 0.05)';
      const files = e.dataTransfer.files;
      if (files.length > 0) { fileInput.files = files; handleSelectedFile(files[0]); }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) handleSelectedFile(fileInput.files[0]);
    });
    removeFileBtn.addEventListener('click', () => {
      fileInput.value = '';
      fileCard.style.display = 'none';
      analyzeBtn.disabled = true;
      analyzeBtn.style.opacity = '0.6';
    });
    uploadForm.addEventListener('submit', () => {
      progressContainer.style.display = 'block';
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = '⏳ Extracting & Analyzing Report...';
      let width = 10;
      const interval = setInterval(() => {
        if (width >= 90) clearInterval(interval);
        else { width += 15; progressBar.style.width = width + '%'; }
      }, 200);
    });
  }

  function handleSelectedFile(file) {
    fileName.textContent = file.name + " ✓";
    fileSize.textContent = (file.size / 1024).toFixed(1) + " KB";
    fileCard.style.display = 'flex';
    analyzeBtn.disabled = false;
    analyzeBtn.style.opacity = '1';
  }

  // Chart Rendering
  document.addEventListener("DOMContentLoaded", function () {
    switchDashboardNav(null, 'overview-tab');

    if (typeof Chart === "undefined") { console.error("Chart.js failed to load."); return; }

    Chart.defaults.font.family = 'Segoe UI, system-ui, -apple-system, sans-serif';
    Chart.defaults.color = '#64748b';

    const classCtx = document.getElementById('classDistChart');
    if (classCtx) {
      new Chart(classCtx, {
        type: 'doughnut',
        data: {
          labels: ['Non-Diabetic', 'Diabetic'],
          datasets: [{
            data: [classCountsData['0'] || 500, classCountsData['1'] || 268],
            backgroundColor: ['#3b82f6', '#f43f5e'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom' } } }
      });
    }

    const modelCtx = document.getElementById('modelCompChart');
    if (modelCtx) {
      new Chart(modelCtx, {
        type: 'bar',
        data: {
          labels: modelChartData.labels,
          datasets: [
            { label: 'Accuracy', data: modelChartData.metrics.accuracy, backgroundColor: '#3b82f6' },
            { label: 'Precision', data: modelChartData.metrics.precision, backgroundColor: '#10b981' },
            { label: 'F1 Score', data: modelChartData.metrics.f1, backgroundColor: '#f59e0b' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 50, max: 100 } } }
      });
    }

    const featCtx = document.getElementById('featureMeansChart');
    if (featCtx) {
      new Chart(featCtx, {
        type: 'bar',
        data: {
          labels: featureMeansData.labels,
          datasets: [
            { label: 'Non-Diabetic Mean', data: featureMeansData.non_diabetic, backgroundColor: '#3b82f6' },
            { label: 'Diabetic Mean', data: featureMeansData.diabetic, backgroundColor: '#f43f5e' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    const glucCtx = document.getElementById('glucoseClassChart');
    if (glucCtx) {
      new Chart(glucCtx, {
        type: 'bar',
        data: {
          labels: glucoseBins,
          datasets: [
            { label: 'Non-diabetic', data: glucoseByClassData['Non-diabetic'], backgroundColor: '#3b82f6' },
            { label: 'Diabetic', data: glucoseByClassData['Diabetic'], backgroundColor: '#f43f5e' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  });
</script>
{% endblock %}
"""

with open('c:/Users/krish/.gemini/antigravity-ide/scratch/EarlyMed-AI/app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
