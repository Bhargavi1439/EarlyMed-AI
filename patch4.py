import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Canvas Wrappers
html = html.replace('width: 80px; height: 80px;', 'width: 160px; height: 120px;')

# 2. JS Replacement
new_js = '''
    function makeMiniDoughnut(canvasId, labels, data, bgColors) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
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
          cutout: '65%', 
          plugins: { 
            legend: { 
              display: true, 
              position: 'right',
              labels: {
                boxWidth: 8,
                padding: 5,
                font: { size: 9 }
              }
            }, 
            tooltip: { enabled: true } 
          },
          layout: { padding: 0 }
        }
      });
    }

    makeMiniDoughnut('distChartDiab', ['Non-Diabetic', 'Diabetic'], [classCountsData['0'] || 0, classCountsData['1'] || 0], ['#3b82f6', '#f43f5e']);
    makeMiniDoughnut('distChartHeart', ['No Disease', 'Disease'], [heartCounts['0'] || 0, heartCounts['1'] || 0], ['#10b981', '#f43f5e']);
    makeMiniDoughnut('distChartKidney', ['No CKD', 'CKD'], [kidneyCounts['0'] || 0, kidneyCounts['1'] || 0], ['#10b981', '#f59e0b']);
    makeMiniDoughnut('distChartThyroid', ['No Recurrence', 'Recurrence'], [thyroidCounts['0'] || 0, thyroidCounts['1'] || 0], ['#10b981', '#8b5cf6']);
'''

html = re.sub(r'function makeMiniDoughnut.*?\}\s*makeMiniDoughnut.*?makeMiniDoughnut.*?makeMiniDoughnut.*?makeMiniDoughnut.*?\);', new_js, html, flags=re.DOTALL)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
