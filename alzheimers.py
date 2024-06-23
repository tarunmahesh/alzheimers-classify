# -*- coding: utf-8 -*-
"""Alzheimers.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rngiH6OeuYPYMMIGqX17jLejg4nzm65X

Importing Models and Setting up Data
"""

#Importing Models
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from lightgbm import LGBMClassifier
from xgboost.sklearn import XGBClassifier


import matplotlib.pyplot as plt
from matplotlib import pyplot
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics  import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import sklearn
from sklearn.model_selection import StratifiedKFold
print(sklearn.__version__)

from google.colab import drive
drive.mount('/content/gdrive')
datapath="/content/gdrive/My Drive"

df_alzheimer = pd.read_csv(os.path.join(datapath,'Alzheimer_Data.csv'))
df_alzheimer = df_alzheimer.drop(["SubjectID"], axis=1)
df_alzheimer.head()

print("HC Patients: ", df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[0])
print("MCI Patients: ", df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[1])
print("AD Patients: ", df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[2])
print("Total Patients: ", df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[0]+df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[1]+df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"].value_counts()[2])

!pip install mrmr_selection
!import mrmr

"""Test for all data"""

from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import precision_score
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import RFE
from sklearn.neural_network import MLPClassifier

import mrmr
from mrmr import mrmr_classif

from sklearn.model_selection import cross_val_score
import statistics
from sklearn.decomposition import PCA
import random
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import ExtraTreesClassifier

X = df_alzheimer.drop(["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"], axis=1)
y = df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"]

#Add another standardization step here
scaler = StandardScaler().set_output(transform="pandas")
X = scaler.fit_transform(X)

selected_features = mrmr_classif(X=X, y=y, K=5)
X = df_alzheimer[selected_features]
print(selected_features)

score = []

for i in range(100):
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.30, random_state = i
  )
  scaled_X_train = scaler.fit_transform(X_train)

  gbc_best = GradientBoostingClassifier(learning_rate = 0.1, n_estimators = 100, min_samples_split = 0.1, max_features = 0.1, min_samples_leaf = 0.2)
  gbc_best.fit(X_train, y_train)

  score.append(gbc_best.score(X_test, y_test))

print(score.index(max(score)))

print(max(score))

from sklearn.model_selection import GridSearchCV

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state = score.index(max(score))
)
scaled_X_train = scaler.fit_transform(X_train)

# Model 1: Gradient Booster Classification
'''
'learning_rate': 0.1, 'n_estimators': 8,'min_samples_split': 1.0, 'max_features': 1, 'min_samples_leaf': 0.2
'''
gbc_best = GradientBoostingClassifier(learning_rate = 0.1, n_estimators = 100, min_samples_split = 0.1, max_features = 0.1, min_samples_leaf = 0.2)
gbc_best.fit(X_train, y_train)
# Model 2: Random Trees Classifier
'''
'min_samples_split': 0.1, 'n_estimators': 200, 'max_features': 6, 'min_samples_leaf': 0.1
'''
rf_best = RandomForestClassifier(min_samples_leaf = 0.1, min_samples_split = 0.1, n_estimators = 32)
rf_best.fit(X_train, y_train)

from sklearn.svm import LinearSVC

# Model 3: SVC Classifier
svc_best = LinearSVC(penalty="l1", loss="squared_hinge", dual=False, tol=1e-3)
svc_best.fit(X_train, y_train)

#Model 4: LGBM Classifier
lgbm_best = LGBMClassifier(num_class=3, objective='multiclass')
lgbm_best.fit(X_train, y_train)

#SVC and Logistic Regression Use L1
#Model 5: Logistic Regression
logreg_best = LogisticRegression(C=1, penalty='l1', solver='liblinear')
logreg_best.fit(X_train, y_train)

#Model 6: KNN
knn_best = KNeighborsClassifier(n_neighbors = 25, p = 1)
knn_best.fit(X_train, y_train)


from sklearn.ensemble import VotingClassifier
#create a dictionary of our models
estimators=[('lgbm', lgbm_best), ('gbc', gbc_best), ('logreg', logreg_best)]
#create our voting classifier, inputting our models
ensemble = VotingClassifier(estimators, voting='soft')
#ensemble = KNeighborsClassifier(n_neighbors = 25, p = 1)

#fit model to training data

ensemble.fit(X_train, y_train)
ensemble_pred = ensemble.predict(X_test)
print("Average Accuracy: ", ensemble.score(X_test, y_test))
print("GBC Accuracy: ", gbc_best.score(X_test, y_test))
print("RF Accuracy: ", rf_best.score(X_test, y_test))
print("KNN Accuracy: ", knn_best.score(X_test, y_test))
print("LGBM Accuracy: ", lgbm_best.score(X_test, y_test))
print("SVC Accuracy: ", svc_best.score(X_test, y_test))
print("LogReg Accuracy: ", logreg_best.score(X_test, y_test))

from sklearn.metrics import classification_report

#import scikitplot as skplt
import matplotlib.pyplot as plt
from sklearn import metrics



print("GBC Accuracy")

gbc_predict = gbc_best.predict(X_test)
print(classification_report(y_test, gbc_predict))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [0,1,2]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(gbc_predict)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])

print(pd.DataFrame(res,columns = ['class','sensitivity','specificity']))

print("LGBM Accuracy")

lgbm_predict = lgbm_best.predict(X_test)
print(classification_report(y_test, lgbm_predict))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [0,1,2]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(lgbm_predict)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])

print(pd.DataFrame(res,columns = ['class','sensitivity','specificity']))

print("Emsemble Accuracy")

print(classification_report(y_test, ensemble_pred))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [0,1,2]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(ensemble_pred)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])

print(pd.DataFrame(res,columns = ['class','sensitivity','specificity']))
#Sensitivty: Measures ability to classify positives
#Specificity: Measure ability to classify negatives

!pip install scikit-plot

import scikitplot as skplt
import matplotlib.pyplot as plt

y_probas = gbc_best.predict_proba(X_test)
skplt.metrics.plot_roc_curve(y_test, y_probas)
plt.show()

cm = confusion_matrix(y_test, ensemble_pred, labels=ensemble.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=ensemble.classes_)
disp.plot()
plt.show()
print(type(cm))
l = ['hc', 'mci', 'ad']
for i in range(3):
  print(l[i], ": ", (cm[i][i])/(cm[i][0] + cm[i][1] + cm[i][2]))

from sklearn.model_selection import cross_validate
from sklearn.metrics import f1_score

modelKNN = KNeighborsClassifier(n_neighbors = 3)
modelKNN.fit(X_train, y_train)

print("Training Accuracy", modelKNN.score(X_train, y_train))
print("Testing Accuracy", modelKNN.score(X_test, y_test))

def cross_validation(model, _X, _y, _cv):
      '''Function to perform 5 Folds Cross-Validation
       Parameters
       ----------
      model: Python Class, default=None
              This is the machine learning algorithm to be used for training.
      _X: array
           This is the matrix of features.
      _y: array
           This is the target variable.
      _cv: int, default=5
          Determines the number of folds for cross-validation.
       Returns
       -------
       The function returns a dictionary containing the metrics 'accuracy', 'precision',
       'recall', 'f1' for both training set and validation set.
      '''
      _scoring = ['accuracy', 'precision', 'recall', 'f1']
      results = cross_validate(estimator=model,
                               X=_X,
                               y=_y,
                               cv=_cv,
                               scoring=_scoring,
                               return_train_score=True)

      return {"Training Accuracy scores": results['train_accuracy'],
              "Mean Training Accuracy": results['train_accuracy'].mean()*100,
              "Validation Accuracy scores": results['test_accuracy'],
              "Mean Validation Accuracy": results['test_accuracy'].mean()*100
              }

print(cross_validation(ensemble, X, y, 50))

print(cross_validation(modelKNN, X, y, 15))
print(cross_validation(knn_best, X, y, 15))
print(cross_validation(gbc_best, X, y, 15))
print(cross_validation(rf_best, X, y, 15))
print(cross_validation(lgbm_best, X, y, 15))

print(cross_validation(gbc_best, X, y, 10))
print(cross_validation(gbc_best, X, y, 25))
print(cross_validation(gbc_best, X, y, 50))
print(cross_validation(gbc_best, X, y, 100))



"""Test for Data with results 0 and 2

```
# This is formatted as code
```


"""

X_0_2 = X.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 1]

y_0_2 = y.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 1]

skf = StratifiedKFold(n_splits=3)
for train_index, test_index in skf.split(X_0_2, y_0_2):
  X_train, X_test = X_0_2.iloc[train_index], X_0_2.iloc[test_index]
  y_train, y_test = y_0_2.iloc[train_index], y_0_2.iloc[test_index]
# Create and train the logistic regression model
model = SVC(probability=True)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()

print(classification_report(y_test, y_pred))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [0,2]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(y_pred)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])

print(cross_validation(model, X_0_2, y_0_2, 50))

y_probas = model.predict_proba(X_test)
skplt.metrics.plot_roc_curve(y_test, y_probas)
plt.show()

"""Tests for Data with results 1 and 2"""

X_1_2 = df_alzheimer.drop(["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"], axis=1)
X_1_2 = X_1_2.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 0]

y_1_2 = df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"]
y_1_2 = y_1_2.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 0]

skf = StratifiedKFold(n_splits=6)
for train_index, test_index in skf.split(X_1_2, y_1_2):
  X_train, X_test = X_1_2.iloc[train_index], X_1_2.iloc[test_index]
  y_train, y_test = y_1_2.iloc[train_index], y_1_2.iloc[test_index]
# Create and train the logistic regression model
model = LGBMClassifier()
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()

print(classification_report(y_test, y_pred))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [1,2]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(y_pred)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])

#Report sensitivity and specificity
print(cross_validation(model, X_1_2, y_1_2, 50))

y_probas = model.predict_proba(X_test)
skplt.metrics.plot_roc_curve(y_test, y_probas)
plt.show()

"""Test for Data with results 0 and 1"""

X_0_1 = df_alzheimer.drop(["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"], axis=1)
X_0_1 = X_0_1.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 2]

y_0_1 = df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"]
y_0_1 = y_0_1.loc[df_alzheimer["Diagnosis (0 - HC, 1 - MCI, 2 - AD)"] != 2]

skf = StratifiedKFold(n_splits=6)
for train_index, test_index in skf.split(X_0_1, y_0_1):
  X_train, X_test = X_0_1.iloc[train_index], X_0_1.iloc[test_index]
  y_train, y_test = y_0_1.iloc[train_index], y_0_1.iloc[test_index]
# Create and train the logistic regression model
model = LGBMClassifier()
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()
#Look at sensitivity and specificity of the pairwise classification

print(classification_report(y_test, y_pred))

from sklearn.metrics import precision_recall_fscore_support
res = []
for l in [0,1]:
    prec,recall,_,_ = precision_recall_fscore_support(np.array(y_test)==l,
                                                      np.array(y_pred)==l,
                                                      pos_label=True,average=None)
    res.append([l,recall[0],recall[1]])
print(cross_validation(model, X_0_1, y_0_1, 50))

y_probas = model.predict_proba(X_test)
skplt.metrics.plot_roc_curve(y_test, y_probas)
plt.show()

import scipy.io
mat = scipy.io.loadmat("Demographics_ADNI_805Subjects.mat")

print(mat.keys())

import pandas as pd
x = mat["demogdatabl"]

print(x)

df_balls = pd.DataFrame(x)