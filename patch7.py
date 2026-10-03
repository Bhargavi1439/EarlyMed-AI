import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update initial `mpCombinedChart` definition
old_init = r"""            { label: 'Accuracy', data: modelChartData.metrics.accuracy, backgroundColor: '#3b82f6' },
            { label: 'Precision', data: modelChartData.metrics.precision, backgroundColor: '#10b981' },
            { label: 'Recall', data: modelChartData.metrics.recall, backgroundColor: '#f59e0b' },
            { label: 'F1 Score', data: modelChartData.metrics.f1, backgroundColor: '#8b5cf6' },
            { label: 'ROC-AUC', data: modelChartData.metrics.roc_auc, backgroundColor: '#ef4444' }"""

new_init = r"""            { label: 'Accuracy', data: modelChartData.metrics.accuracy, backgroundColor: '#3b82f6' },
            { label: 'Precision', data: modelChartData.metrics.precision, backgroundColor: '#10b981' },
            { label: 'Recall', data: modelChartData.metrics.recall, backgroundColor: '#f59e0b' },
            { label: 'F1 Score', data: modelChartData.metrics.f1, backgroundColor: '#8b5cf6' },
            { label: 'ROC-AUC', data: modelChartData.metrics.roc_auc, backgroundColor: '#ef4444' },
            { label: 'F-Beta', data: modelChartData.metrics.f_beta || Array(5).fill(0), backgroundColor: '#0ea5e9' },
            { label: 'PR-AUC', data: modelChartData.metrics.pr_auc || Array(5).fill(0), backgroundColor: '#6366f1' },
            { label: 'Log Loss', data: modelChartData.metrics.log_loss || Array(5).fill(0), backgroundColor: '#f43f5e' },
            { label: 'MCC', data: modelChartData.metrics.mcc || Array(5).fill(0), backgroundColor: '#14b8a6' }"""

html = html.replace(old_init, new_init)


# 2. Update `switchDiseaseTab`
old_switch = r"""    if (disease === 'diabetes') metricsObj = diabMetricsObj;
    else if (disease === 'heart') metricsObj = heartMetricsObj;
    else if (disease === 'kidney') metricsObj = kidneyMetricsObj;
    
    if (Object.keys(metricsObj).length > 0) {
      const labels = Object.keys(metricsObj).map(n => n.replace("_", " ").toUpperCase());
      const acc = Object.values(metricsObj).map(m => parseFloat((m.accuracy || 0) * 100).toFixed(1));
      const prec = Object.values(metricsObj).map(m => parseFloat((m.precision || 0) * 100).toFixed(1));
      const rec = Object.values(metricsObj).map(m => parseFloat((m.recall || 0) * 100).toFixed(1));
      const f1 = Object.values(metricsObj).map(m => parseFloat((m.f1 || 0) * 100).toFixed(1));
      const roc = Object.values(metricsObj).map(m => parseFloat((m.roc_auc || 0) * 100).toFixed(1));
      
      const chart = window.metricCharts['mpCombinedChart'];
      if(chart) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = acc;
        chart.data.datasets[1].data = prec;
        chart.data.datasets[2].data = rec;
        chart.data.datasets[3].data = f1;
        chart.data.datasets[4].data = roc;
        chart.update();
      }"""

new_switch = r"""    if (disease === 'diabetes') metricsObj = diabMetricsObj;
    else if (disease === 'heart') metricsObj = heartMetricsObj;
    else if (disease === 'kidney') metricsObj = kidneyMetricsObj;
    else if (disease === 'thyroid') metricsObj = thyroidMetricsObj;
    
    if (Object.keys(metricsObj).length > 0) {
      const labels = Object.keys(metricsObj).map(n => n.replace("_", " ").toUpperCase());
      const acc = Object.values(metricsObj).map(m => parseFloat((m.accuracy || 0) * 100).toFixed(1));
      const prec = Object.values(metricsObj).map(m => parseFloat((m.precision || 0) * 100).toFixed(1));
      const rec = Object.values(metricsObj).map(m => parseFloat((m.recall || 0) * 100).toFixed(1));
      const f1 = Object.values(metricsObj).map(m => parseFloat((m.f1 || 0) * 100).toFixed(1));
      const roc = Object.values(metricsObj).map(m => parseFloat((m.roc_auc || 0) * 100).toFixed(1));
      const fbeta = Object.values(metricsObj).map(m => parseFloat((m.f_beta || 0) * 100).toFixed(1));
      const prauc = Object.values(metricsObj).map(m => parseFloat((m.pr_auc || 0) * 100).toFixed(1));
      const logloss = Object.values(metricsObj).map(m => parseFloat((m.log_loss || 0)).toFixed(2));
      const mcc = Object.values(metricsObj).map(m => parseFloat((m.mcc || 0)).toFixed(3));
      
      const chart = window.metricCharts['mpCombinedChart'];
      if(chart) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = acc;
        chart.data.datasets[1].data = prec;
        chart.data.datasets[2].data = rec;
        chart.data.datasets[3].data = f1;
        chart.data.datasets[4].data = roc;
        if(chart.data.datasets[5]) chart.data.datasets[5].data = fbeta;
        if(chart.data.datasets[6]) chart.data.datasets[6].data = prauc;
        if(chart.data.datasets[7]) chart.data.datasets[7].data = logloss;
        if(chart.data.datasets[8]) chart.data.datasets[8].data = mcc;
        chart.update();
      }"""

html = html.replace(old_switch, new_switch)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
