import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove header
html = html.replace('<th>Conf Matrix</th>', '')

# Remove data column
row_td = r'\s*<td style="font-size: 0\.85em; white-space: nowrap;">\[\{\{ m_mets\.confusion_matrix\.true_negative \}\}, \{\{ m_mets\.confusion_matrix\.false_positive \}\}, \{\{ m_mets\.confusion_matrix\.false_negative \}\}, \{\{ m_mets\.confusion_matrix\.true_positive \}\}\]</td>'

html = re.sub(row_td, '', html)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
