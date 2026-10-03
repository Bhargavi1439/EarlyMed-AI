import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add new individual charts and combined chart HTML
new_charts_html = r"""
        <div class="chart-wrapper">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; font-size: 1rem;">F-Beta</h3>
            <select class="chart-control" onchange="updateChartType('fbetaChart', this.value)">
              <option value="bar">Bar</option><option value="line">Line</option><option value="pie">Pie</option>
            </select>
          </div>
          <div class="chart-container"><canvas id="fbetaChart"></canvas></div>
        </div>

        <div class="chart-wrapper">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; font-size: 1rem;">PR-AUC</h3>
            <select class="chart-control" onchange="updateChartType('praucChart', this.value)">
              <option value="bar">Bar</option><option value="line">Line</option><option value="pie">Pie</option>
            </select>
          </div>
          <div class="chart-container"><canvas id="praucChart"></canvas></div>
        </div>

        <div class="chart-wrapper">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; font-size: 1rem;">Log Loss</h3>
            <select class="chart-control" onchange="updateChartType('logLossChart', this.value)">
              <option value="bar">Bar</option><option value="line">Line</option><option value="pie">Pie</option>
            </select>
          </div>
          <div class="chart-container"><canvas id="logLossChart"></canvas></div>
        </div>

        <div class="chart-wrapper">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; font-size: 1rem;">MCC</h3>
            <select class="chart-control" onchange="updateChartType('mccChart', this.value)">
              <option value="bar">Bar</option><option value="line">Line</option><option value="pie">Pie</option>
            </select>
          </div>
          <div class="chart-container"><canvas id="mccChart"></canvas></div>
        </div>
      </div>
"""

combined_html = r"""
      <!-- Global Combined Analysis -->
      <h3 style="margin-top:2rem; font-size: 1.1rem; border-bottom: 2px solid #93c5fd; padding-bottom: 0.5rem;">Combined Comparative Analysis (All Metrics)</h3>
      <div style="margin-bottom: 2rem;">
        <div class="chart-wrapper">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h3 style="margin:0; font-size: 1rem;">Average Performance Across All Diseases</h3>
            <select class="chart-control" onchange="updateChartType('globalCombinedChart', this.value)">
              <option value="bar">Bar</option><option value="line">Line</option>
            </select>
          </div>
          <div class="chart-container" style="height: 400px;"><canvas id="globalCombinedChart"></canvas></div>
        </div>
      </div>

      <!-- 5 Separate Metric Charts -->
      <div class="q-grid-2" style="margin-bottom: 2rem;">
"""

html = html.replace('      <!-- 5 Separate Metric Charts -->\n      <div class="q-grid-2" style="margin-bottom: 2rem;">', combined_html)
html = html.replace('        </div>\n      </div>\n    </div>\n\n    <!-- 5. Individual Risk Prediction (Purple) -->', new_charts_html + '    </div>\n\n    <!-- 5. Individual Risk Prediction (Purple) -->')

# 2. Add JS calls to create charts
js_old = r"""    createCombinedMetricChart('accChart', 'accuracy');
    createCombinedMetricChart('precChart', 'precision');
    createCombinedMetricChart('recChart', 'recall');
    createCombinedMetricChart('f1Chart', 'f1');
    createCombinedMetricChart('rocChart', 'roc_auc');"""

js_new = r"""    createCombinedMetricChart('accChart', 'accuracy');
    createCombinedMetricChart('precChart', 'precision');
    createCombinedMetricChart('recChart', 'recall');
    createCombinedMetricChart('f1Chart', 'f1');
    createCombinedMetricChart('rocChart', 'roc_auc');
    createCombinedMetricChart('fbetaChart', 'f_beta');
    createCombinedMetricChart('praucChart', 'pr_auc');
    createCombinedMetricChart('logLossChart', 'log_loss', false);
    createCombinedMetricChart('mccChart', 'mcc', false);"""

html = html.replace(js_old, js_new)

# 3. Update createCombinedMetricChart to handle log_loss / mcc limits and multiplier
create_old = r"""    function createCombinedMetricChart(canvasId, metricKey) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;
      
      const algos = Object.keys(diabMetricsObj);
      const labels = algos.map(n => n.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()));
      
      const diabData = algos.map(a => parseFloat(((diabMetricsObj[a] || {})[metricKey] || 0) * 100).toFixed(1));
      const heartData = algos.map(a => parseFloat(((heartMetricsObj[a] || {})[metricKey] || 0) * 100).toFixed(1));
      const kidneyData = algos.map(a => parseFloat(((kidneyMetricsObj[a] || {})[metricKey] || 0) * 100).toFixed(1));
      const thyroidData = algos.map(a => parseFloat(((thyroidMetricsObj[a] || {})[metricKey] || 0) * 100).toFixed(1));

      window.metricCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            { label: 'Diabetes', data: diabData, backgroundColor: '#3b82f6' },
            { label: 'Heart Disease', data: heartData, backgroundColor: '#f43f5e' },
            { label: 'Kidney Disease', data: kidneyData, backgroundColor: '#8b5cf6' },
            { label: 'Thyroid Cancer', data: thyroidData, backgroundColor: '#10b981' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 40, max: 100 } } }
      });
    }"""

create_new = r"""    function createCombinedMetricChart(canvasId, metricKey, isPercentage = true) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;
      
      const algos = Object.keys(diabMetricsObj);
      const labels = algos.map(n => n.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()));
      
      const mult = isPercentage ? 100 : 1;
      const diabData = algos.map(a => parseFloat(((diabMetricsObj[a] || {})[metricKey] || 0) * mult).toFixed(isPercentage ? 1 : 3));
      const heartData = algos.map(a => parseFloat(((heartMetricsObj[a] || {})[metricKey] || 0) * mult).toFixed(isPercentage ? 1 : 3));
      const kidneyData = algos.map(a => parseFloat(((kidneyMetricsObj[a] || {})[metricKey] || 0) * mult).toFixed(isPercentage ? 1 : 3));
      const thyroidData = algos.map(a => parseFloat(((thyroidMetricsObj[a] || {})[metricKey] || 0) * mult).toFixed(isPercentage ? 1 : 3));

      let yScales = { min: 40, max: 100 };
      if (!isPercentage) {
         if (metricKey === 'log_loss') yScales = { min: 0 };
         else if (metricKey === 'mcc') yScales = { min: -1, max: 1 };
      }

      window.metricCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            { label: 'Diabetes', data: diabData, backgroundColor: '#3b82f6' },
            { label: 'Heart Disease', data: heartData, backgroundColor: '#f43f5e' },
            { label: 'Kidney Disease', data: kidneyData, backgroundColor: '#8b5cf6' },
            { label: 'Thyroid Cancer', data: thyroidData, backgroundColor: '#10b981' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: yScales } }
      });
    }"""

html = html.replace(create_old, create_new)

# 4. Add Global Combined Chart Data Processing
global_chart_js = r"""    createCombinedMetricChart('logLossChart', 'log_loss', false);
    createCombinedMetricChart('mccChart', 'mcc', false);

    // Global Combined Chart
    const globalCtx = document.getElementById('globalCombinedChart');
    if (globalCtx) {
      const algos = Object.keys(diabMetricsObj);
      const algoLabels = algos.map(n => n.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase()));
      
      // Compute averages across 4 diseases for each metric (using percentage versions where appropriate)
      const getAvg = (algo, metric, mult) => {
         const d = (diabMetricsObj[algo] || {})[metric] || 0;
         const h = (heartMetricsObj[algo] || {})[metric] || 0;
         const k = (kidneyMetricsObj[algo] || {})[metric] || 0;
         const t = (thyroidMetricsObj[algo] || {})[metric] || 0;
         return ((d + h + k + t) / 4) * mult;
      };

      const metricsList = [
         { label: 'Accuracy', key: 'accuracy', mult: 100, color: '#3b82f6' },
         { label: 'Precision', key: 'precision', mult: 100, color: '#10b981' },
         { label: 'Recall', key: 'recall', mult: 100, color: '#f59e0b' },
         { label: 'F1 Score', key: 'f1', mult: 100, color: '#8b5cf6' },
         { label: 'ROC-AUC', key: 'roc_auc', mult: 100, color: '#ef4444' },
         { label: 'F-Beta', key: 'f_beta', mult: 100, color: '#0ea5e9' },
         { label: 'PR-AUC', key: 'pr_auc', mult: 100, color: '#6366f1' }
      ];

      const datasets = metricsList.map(m => {
         return {
            label: m.label,
            data: algos.map(a => getAvg(a, m.key, m.mult).toFixed(1)),
            backgroundColor: m.color
         };
      });

      window.metricCharts['globalCombinedChart'] = new Chart(globalCtx, {
        type: 'bar',
        data: {
          labels: algoLabels,
          datasets: datasets
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } } }
      });
    }"""

html = html.replace(js_new, global_chart_js)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
