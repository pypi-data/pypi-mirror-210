import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import pickle
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier, XGBRFClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import classification_report,precision_score, recall_score,f1_score

class BestClassifier:

    def __init__(self):
        self.classifiers = {
            'LogisticRegression': LogisticRegression(),
            'DecisionTree': DecisionTreeClassifier(criterion = 'entropy', random_state = 0),
            'RandomForest': RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 0),
            'GaussianNB': GaussianNB(),
            'KNN': KNeighborsClassifier(n_neighbors = 5, metric = 'minkowski', p = 2),
            'SVM': SVC(),
            'KernelSVM':SVC(kernel = 'rbf', random_state = 0),
            'XGboots': XGBClassifier(),
            'AdaBoostClassifier': AdaBoostClassifier(),
            'GradientBoostingClassifier': GradientBoostingClassifier(),
            'XGBRFClassifier': XGBRFClassifier(objective='binary:logistic', eval_metric=['logloss']),
            'CatBoostClassifier': CatBoostClassifier(verbose=0),

        }
        self.models =[]
        self.best_classifier = None
        self.best_model = None

    def fit(self, x_train, y_train, x_test, y_test):
        for clf_name, clf in self.classifiers.items():
            clf.fit(x_train, y_train)
            y_predA = clf.predict(x_train)
            model_score_A = clf.score(x_train, y_train)
            recall_score_A = recall_score(y_train, y_predA)
            f1_score_A = f1_score(y_train, y_predA)
            precision_score_A = precision_score(y_train, y_predA)
            acuracy_score_A = accuracy_score(y_train, y_predA)


            y_predB = clf.predict(x_test)
            model_score_B = clf.score(x_test, y_test)
            recall_score_B = recall_score(y_test, y_predB)
            f1_score_B = f1_score(y_test, y_predB)
            precision_score_B = precision_score(y_test, y_predB)
            acuracy_score_B = accuracy_score(y_test, y_predB)


            self.models.append({"Algorithm": clf_name,
                                "train_model_score": model_score_A,
                                "train_recall_score": recall_score_A,
                                "train_f1_score_A": f1_score_A,
                                "train_precision_score": precision_score_A,
                                "train_acuracy_score": acuracy_score_A,

                                "test_model_score": model_score_B,
                                "test_recall_score": recall_score_B,
                                "test_f1_score_A": f1_score_B,
                                "test_precision_score": precision_score_B,
                                "test_acuracy_score": acuracy_score_B,
                                "Model": clf,
                                })

        return self.models

    def get_bestmodel(self):
        best_accuracy = -1
        for item in self.models:
            if item["test_acuracy_score"] > best_accuracy:
                best_accuracy = item["test_acuracy_score"]
                self.best_classifier = item["Algorithm"]
                self.best_model = item["Model"]

        return {"Algorithm":self.best_classifier, "Model":self.best_model, "test_Accuracy":best_accuracy}

    def saveModelweight(self, index):
        with open(f'best_model_weights_{index}.pkl', 'wb') as f:
            pickle.dump(self.get_bestmodel()["Model"].coef_, f)

    def predict(self, value):
        return self.get_bestmodel()["Model"].predict(value)



