import numpy as np
import tensorflow as tf
from tensorflow.python.ops.metrics_impl import _streaming_confusion_matrix


def get_metrics_ops(labels, predictions, num_labels):
    cm, op = _streaming_confusion_matrix(labels, predictions, num_labels)

    tf.logging.info(type(cm))
    tf.logging.info(type(op))

    return (tf.convert_to_tensor(cm), op)

def get_metrics(conf_mat, num_labels):
    # 得到numpy类型的混淆矩阵，然后计算precision，recall，f1值。
    precisions = []
    recalls = []
    for i in range(num_labels):
        tp = conf_mat[i][i].sum()
        col_sum = conf_mat[:, i].sum()
        row_sum = conf_mat[i].sum()

        precision = tp / col_sum if col_sum > 0 else 0
        recall = tp / row_sum if row_sum > 0 else 0

        precisions.append(precision)
        recalls.append(recall)

    pre = sum(precisions) / len(precisions)
    rec = sum(recalls) / len(recalls)
    f1 = 2 * pre * rec / (pre + rec)

    return pre, rec, f1

#obtain the effect
def get_class_f1(conf_mat, num_labels):
    #obtain confusion matrix, then calculate the precision，recall and F1。
    precisions = []
    recalls = []
    f1_multi = []
    tp_list = []
    for i in range(num_labels):
        tp = conf_mat[i][i].sum()
        col_sum = conf_mat[:, i].sum()
        row_sum = conf_mat[i].sum()

        precision = tp / col_sum if col_sum > 0 else 0
        recall = tp / row_sum if row_sum > 0 else 0

        f1 = 0
        if precision != 0:
            f1 = 2 * precision * recall / (precision + recall)
        f1_multi.append(f1)

        tp_list.append(tp)
        precisions.append(precision)
        recalls.append(recall)

    macro_pre = sum(precisions) / len(precisions)
    macro_rec = sum(recalls) / len(recalls)
    macro_f1 = sum(f1_multi) / len(f1_multi)

    micro_pre = sum(tp_list) / conf_mat.sum()
    micro_rec = sum(tp_list) / conf_mat.sum()
    micro_f1 = 2 * micro_pre * micro_rec / (micro_pre + micro_rec)

    return f1_multi, macro_f1, micro_f1