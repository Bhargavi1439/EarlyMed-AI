import re

with open('app/templates/visualize.html', 'r', encoding='utf-8') as f:
    html = f.read()

header_old = r'<tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th></tr>'
header_new = r'<tr><th>Algorithm</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>ROC-AUC</th><th>F-Beta</th><th>PR-AUC</th><th>Log Loss</th><th>MCC</th><th>Conf Matrix</th></tr>'

html = html.replace(header_old, header_new)

row_old = r'''                <td style="padding: 0.6rem 0.4rem;"><strong>{{ m_name|replace('_', ' ')|title }}</strong></td>
                <td>{{ "%.1f"|format(m_mets.accuracy * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.precision * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.recall * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.f1 * 100) }}%</td>
                <td><strong>{{ "%.1f"|format(m_mets.roc_auc * 100) }}%</strong></td>'''

row_new = r'''                <td style="padding: 0.6rem 0.4rem;"><strong>{{ m_name|replace('_', ' ')|title }}</strong></td>
                <td>{{ "%.1f"|format(m_mets.accuracy * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.precision * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.recall * 100) }}%</td>
                <td>{{ "%.1f"|format(m_mets.f1 * 100) }}%</td>
                <td><strong>{{ "%.1f"|format(m_mets.roc_auc * 100) }}%</strong></td>
                <td>{{ "%.1f"|format((m_mets.f_beta|default(0)) * 100) }}%</td>
                <td>{{ "%.1f"|format((m_mets.pr_auc|default(0)) * 100) }}%</td>
                <td>{{ "%.2f"|format(m_mets.log_loss|default(0)) }}</td>
                <td>{{ "%.3f"|format(m_mets.mcc|default(0)) }}</td>
                <td style="font-size: 0.85em; white-space: nowrap;">[{{ m_mets.confusion_matrix.true_negative }}, {{ m_mets.confusion_matrix.false_positive }}, {{ m_mets.confusion_matrix.false_negative }}, {{ m_mets.confusion_matrix.true_positive }}]</td>'''

html = html.replace(row_old, row_new)

with open('app/templates/visualize.html', 'w', encoding='utf-8') as f:
    f.write(html)
