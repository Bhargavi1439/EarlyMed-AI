import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. HTML Replacement
new_html = '''      <div class="q-grid-2" style="margin-bottom: 1.5rem;">
        <!-- Diabetes -->
        <div class="stat-box" style="display:flex; justify-content: space-between; align-items:center; text-align:left;">
          <div style="display:flex; align-items:center; gap: 1rem;">
            <span style="font-size: 2rem;">🩸</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Diabetes Dataset</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_rows }} records</div>
            </div>
          </div>
          <div style="width: 80px; height: 80px; position:relative;">
            <canvas id="distChartDiab"></canvas>
          </div>
        </div>
        <!-- Heart -->
        <div class="stat-box" style="display:flex; justify-content: space-between; align-items:center; text-align:left;">
          <div style="display:flex; align-items:center; gap: 1rem;">
            <span style="font-size: 2rem;">❤️</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Heart Disease</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_heart_rows }} records</div>
            </div>
          </div>
          <div style="width: 80px; height: 80px; position:relative;">
            <canvas id="distChartHeart"></canvas>
          </div>
        </div>
        <!-- Kidney -->
        <div class="stat-box" style="display:flex; justify-content: space-between; align-items:center; text-align:left;">
          <div style="display:flex; align-items:center; gap: 1rem;">
            <span style="font-size: 2rem;">🫘</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Kidney Disease</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_kidney_rows }} records</div>
            </div>
          </div>
          <div style="width: 80px; height: 80px; position:relative;">
            <canvas id="distChartKidney"></canvas>
          </div>
        </div>
        <!-- Thyroid -->
        <div class="stat-box" style="display:flex; justify-content: space-between; align-items:center; text-align:left;">
          <div style="display:flex; align-items:center; gap: 1rem;">
            <span style="font-size: 2rem;">🦋</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Thyroid Cancer</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_thyroid_rows }} records</div>
            </div>
          </div>
          <div style="width: 80px; height: 80px; position:relative;">
            <canvas id="distChartThyroid"></canvas>
          </div>
        </div>
      </div>'''

html = re.sub(r'<div class="q-grid-2" style="margin-bottom: 1\.5rem;">.*?<div class="chart-container" style="height: 220px;">\s*<canvas id="classDistChart"></canvas>\s*</div>\s*</div>\s*</div>', new_html, html, flags=re.DOTALL)

# 2. JS Replacement
new_js = '''
    function makeMiniDoughnut(canvasId, data, bgColors) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['No', 'Yes'],
          datasets: [{
            data: data,
            backgroundColor: bgColors,
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          cutout: '70%', 
          plugins: { legend: { display: false }, tooltip: { enabled: true } },
          layout: { padding: 0 }
        }
      });
    }

    makeMiniDoughnut('distChartDiab', [classCountsData['0'] || 0, classCountsData['1'] || 0], ['#3b82f6', '#f43f5e']);
    makeMiniDoughnut('distChartHeart', [heartCounts['0'] || 0, heartCounts['1'] || 0], ['#10b981', '#f43f5e']);
    makeMiniDoughnut('distChartKidney', [kidneyCounts['0'] || 0, kidneyCounts['1'] || 0], ['#10b981', '#f59e0b']);
    makeMiniDoughnut('distChartThyroid', [thyroidCounts['0'] || 0, thyroidCounts['1'] || 0], ['#10b981', '#8b5cf6']);
'''

html = re.sub(r'window\.updateOverviewChart = function.*?(?=\s*window\.metricCharts = \{\};)', new_js, html, flags=re.DOTALL)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
