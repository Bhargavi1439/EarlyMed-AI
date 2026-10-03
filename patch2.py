import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add clickable styles
if 'stat-box.clickable' not in html:
    html = html.replace('</style>', '  .stat-box.clickable { cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }\n  .stat-box.clickable:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }\n</style>')

# 2. Add onclick and clickable class to existing stat-boxes
html = html.replace('<div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">🩸</span>', '<div class="stat-box clickable" onclick="updateOverviewChart(\'diabetes\')" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">🩸</span>')

html = html.replace('<div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">❤️</span>', '<div class="stat-box clickable" onclick="updateOverviewChart(\'heart\')" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">❤️</span>')

html = html.replace('<div class="stat-box" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">🫘</span>', '<div class="stat-box clickable" onclick="updateOverviewChart(\'kidney\')" style="display:flex; align-items:center; gap: 1rem; text-align:left;">\n            <span style="font-size: 2rem;">🫘</span>')

# 3. Add Thyroid stat-box
thyroid_box = '''          <div class="stat-box clickable" onclick="updateOverviewChart('thyroid')" style="display:flex; align-items:center; gap: 1rem; text-align:left;">
            <span style="font-size: 2rem;">🦋</span>
            <div>
              <div style="font-weight: 700; color: #1e3a8a;">Thyroid Cancer Dataset</div>
              <div style="font-size:0.85rem; color:#475569;">{{ n_thyroid_rows }} records • 16 features</div>
            </div>
          </div>
'''
if 'Thyroid Cancer Dataset' not in html:
    html = html.replace('{{ n_kidney_rows }} records • 13 features</div>\n            </div>\n          </div>', '{{ n_kidney_rows }} records • 13 features</div>\n            </div>\n          </div>\n' + thyroid_box)

# 4. Modify classCtx to save to window and add update function
update_func = '''
    window.updateOverviewChart = function(disease) {
      if (!window.overviewChart) return;
      
      const titleEl = document.getElementById('overview-chart-title');
      let labels = [];
      let data = [];
      let bgColors = [];
      
      if (disease === 'diabetes') {
        if(titleEl) titleEl.innerText = 'Disease Distribution (Diabetes)';
        labels = ['Non-Diabetic', 'Diabetic'];
        data = [classCountsData['0'] || 0, classCountsData['1'] || 0];
        bgColors = ['#3b82f6', '#f43f5e'];
      } else if (disease === 'heart') {
        if(titleEl) titleEl.innerText = 'Disease Distribution (Heart Disease)';
        labels = ['No Disease', 'Disease'];
        data = [heartCounts['0'] || 0, heartCounts['1'] || 0];
        bgColors = ['#10b981', '#f43f5e'];
      } else if (disease === 'kidney') {
        if(titleEl) titleEl.innerText = 'Disease Distribution (Kidney Disease)';
        labels = ['No CKD', 'CKD'];
        data = [kidneyCounts['0'] || 0, kidneyCounts['1'] || 0];
        bgColors = ['#10b981', '#f59e0b'];
      } else if (disease === 'thyroid') {
        if(titleEl) titleEl.innerText = 'Disease Distribution (Thyroid Cancer)';
        labels = ['No Recurrence', 'Recurrence'];
        data = [thyroidCounts['0'] || 0, thyroidCounts['1'] || 0];
        bgColors = ['#10b981', '#8b5cf6'];
      }
      
      window.overviewChart.data.labels = labels;
      window.overviewChart.data.datasets[0].data = data;
      window.overviewChart.data.datasets[0].backgroundColor = bgColors;
      window.overviewChart.update();
    };

    const classCtx = document.getElementById('classDistChart');
    if (classCtx) {
      window.overviewChart = new Chart(classCtx, {
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
'''

if 'window.updateOverviewChart = function' not in html:
    html = re.sub(r'const classCtx = document.getElementById\(\'classDistChart\'\);.*?\}\n', update_func, html, flags=re.DOTALL)

# Add ID to title to allow updating
if '<h3 style="margin-top:0; font-size: 1rem; text-align:center;">Disease Distribution (Diabetes)</h3>' in html:
    html = html.replace('<h3 style="margin-top:0; font-size: 1rem; text-align:center;">Disease Distribution (Diabetes)</h3>', '<h3 id="overview-chart-title" style="margin-top:0; font-size: 1rem; text-align:center;">Disease Distribution (Diabetes)</h3>')

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
