import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add table-thyroid
table_thyroid = '''      <div id="table-thyroid" class="disease-table-container" style="display: none;">
        <table class="data-table" style="width: 100%; text-align: left;">
          <thead style="background: rgba(16,185,129,0.1);">
            <tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th></tr>
          </thead>
          <tbody>
            {% for m_name, m_mets in thyroid_metrics.items() %}
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
'''
if 'id="table-thyroid"' not in html:
    html = html.replace('      <!-- Graphical Metrics Section -->', table_thyroid + '      <!-- Graphical Metrics Section -->')

# 2. Add dmThyroidChart
thyroid_chart = '''        <div class="chart-wrapper">
          <h3 style="margin:0; font-size:1.05rem;">Thyroid Cancer</h3>
          <div class="chart-container" style="height:250px"><canvas id="dmThyroidChart"></canvas></div>
        </div>
'''
if 'id="dmThyroidChart"' not in html:
    html = html.replace(
        '      <div class="q-grid-2">\n        <div class="chart-wrapper">\n          <h3 style="margin:0; font-size:1.05rem;">Diabetes</h3>',
        '      <div class="q-grid-2">\n' + thyroid_chart + '        <div class="chart-wrapper">\n          <h3 style="margin:0; font-size:1.05rem;">Diabetes</h3>'
    )

# 3. Update createCombinedMetricChart
old_func = '''    function createCombinedMetricChart(canvasId, metricKey) {
      const getMet = (obj, m) => {
        const vals = Object.values(obj).map(v => (v[m]||0)*100);
        return vals.length ? (vals.reduce((a,b)=>a+b)/vals.length).toFixed(1) : 0;
      };
      
      const diabVal = getMet(diabMetricsObj, metricKey);
      const heartVal = getMet(heartMetricsObj, metricKey);
      const kidneyVal = getMet(kidneyMetricsObj, metricKey);

      const ctx = document.getElementById(canvasId);
      if(ctx) {
        window.metricCharts[canvasId] = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Diabetes', 'Heart Disease', 'Kidney Disease'],
            datasets: [{
              label: metricKey.toUpperCase(),
              data: [diabVal, heartVal, kidneyVal],
              backgroundColor: ['#3b82f6', '#ef4444', '#f59e0b']
            }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 50, max: 100 } } }
        });
      }
    }'''

new_func = '''    function createCombinedMetricChart(canvasId, metricKey) {
      const getMet = (obj, m) => {
        const vals = Object.values(obj).map(v => (v[m]||0)*100);
        return vals.length ? (vals.reduce((a,b)=>a+b)/vals.length).toFixed(1) : 0;
      };
      
      const diabVal = getMet(diabMetricsObj, metricKey);
      const heartVal = getMet(heartMetricsObj, metricKey);
      const kidneyVal = getMet(kidneyMetricsObj, metricKey);
      const thyroidVal = getMet(thyroidMetricsObj, metricKey);

      const ctx = document.getElementById(canvasId);
      if(ctx) {
        window.metricCharts[canvasId] = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Diabetes', 'Heart', 'Kidney', 'Thyroid'],
            datasets: [{
              label: metricKey.toUpperCase(),
              data: [diabVal, heartVal, kidneyVal, thyroidVal],
              backgroundColor: ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6']
            }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 50, max: 100 } } }
        });
      }
    }'''

html = html.replace(old_func, new_func)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
