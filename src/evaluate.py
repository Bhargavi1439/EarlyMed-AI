from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    fbeta_score,
    average_precision_score,
    log_loss,
    matthews_corrcoef
)


def compute_classification_metrics(y_true, y_pred, y_proba):
    matrix = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = (int(x) for x in matrix.ravel())
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": specificity,
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "f_beta": float(fbeta_score(y_true, y_pred, beta=2.0, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "log_loss": float(log_loss(y_true, y_proba)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
        },
    }

