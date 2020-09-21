
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

rd = pd.read_excel('xray_source.xlsx',index=None,sheet_name='Sheet2')
rc = pd.read_excel('xray_source.xlsx',index=None,sheet_name='Sheet1')

#ROC
print("sklearn ROC AUC Score:")
fpr, tpr, _ = roc_curve(np.array(rc['actual']),np.array(rc['pred']))
plt.figure()
plt.plot(fpr, tpr, color='darkorange',
         lw=2, label='ROC curve')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--') #center line
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()

print("Precision-Recall Curve:")
precision, recall, _ = precision_recall_curve(np.array(rc['actual']),np.array(rc['pred']))
plt.step(recall, precision, color='g', alpha=0.2, where='post')
plt.fill_between(recall, precision, alpha=0.2, color='g', step='post')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.0])
plt.xlim([0.0, 1.0])
plt.title('Precision-Recall curve')
plt.show()

print("Loss , Accuracy , F1Score , Precision")
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,figsize=(7,7))
# fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
ax1.plot(rd['loss'], label='train_loss')
ax1.plot(rd['val_loss'], label='test_test')
ax1.set_title('loss')
ax1.legend()

fig.tight_layout(pad=1.0)
ax2.plot(rd['acc'], label='train_acc')
ax2.plot(rd['val_acc'], label='test_acc')
ax2.set_title('acc')
ax2.legend()

fig.tight_layout(pad=1.0)
ax3.plot(rd['f1_m'], label='f1_m')
ax3.plot(rd['val_f1_m'], label='val_f1_m')
ax3.set_title('f1_metrics')
ax3.legend()

fig.tight_layout(pad=1.0)
ax4.plot(rd['precision_m'], label='precision_m')
ax4.plot(rd['val_precision_m'], label='val_precision_m')
ax4.set_title('precision')
ax4.legend()


