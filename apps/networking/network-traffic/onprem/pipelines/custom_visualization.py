
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt
rd = pd.read_excel('network_source.xlsx',index=None,sheet_name='Sheet1')
precision, recall, _ = precision_recall_curve(np.array(rd['actual']),np.array(rd['pred']))
plt.step(recall, precision, color='g', alpha=0.2, where='post')
plt.fill_between(recall, precision, alpha=0.2, color='g', step='post')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.0])
plt.xlim([0.0, 1.0])
plt.title('Precision-Recall curve')
plt.show()

print("sklearn ROC AUC Score:")
rd = pd.read_excel('network_source.xlsx',index=None,sheet_name='Sheet1')
fpr, tpr, _ = roc_curve(np.array(rd['actual']),np.array(rd['pred']))
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
