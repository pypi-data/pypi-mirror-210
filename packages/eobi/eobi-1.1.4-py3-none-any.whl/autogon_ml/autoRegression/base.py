import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, r2_score

class BestRegressor:

    def __init__(self):
        self.regressors = {
            'LinearRegression': LinearRegression(),
            'DecisionTree': DecisionTreeRegressor(random_state=0),
            'RandomForest': RandomForestRegressor(n_estimators=10, random_state=0),
            'SVR': SVR(),
            'XGboots': XGBRegressor(),
            'CatBoostRegressor': CatBoostRegressor()
        }
        self.models =[]
        self.best_regressor = None
        self.best_model = None

    def fit(self, x_train, y_train, x_test, y_test):
        for reg_name, reg in self.regressors.items():
            reg.fit(x_train, y_train)
            y_predA = reg.predict(x_train)
            mseA = mean_squared_error(y_train, y_predA)
            r2A = r2_score(y_train, y_predA)

            y_predB = reg.predict(x_test)
            mseB = mean_squared_error(y_test, y_predB)
            r2B = r2_score(y_test, y_predB)

            self.models.append({"Algorithm": reg_name,
                                "train_MSE": mseA,
                                "train_R2": r2A,
                                "test_MSE": mseB,
                                "test_R2": r2B,
                                "Model": reg,
                                })

        return self.models

    def get_bestmodel(self, metric='mse'):
        if metric == 'mse':
            best_metric = np.inf
            for item in self.models:
                if item["test_MSE"] < best_metric:
                    best_metric = item["test_MSE"]
                    self.best_regressor = item["Algorithm"]
                    self.best_model = item["Model"]
        elif metric == 'r2':
            best_metric = -np.inf
            for item in self.models:
                if item["test_R2"] > best_metric:
                    best_metric = item["test_R2"]
                    self.best_regressor = item["Algorithm"]
                    self.best_model = item["Model"]
        else:
            raise ValueError("metric must be either 'mse' or 'r2'")

        return {"Algorithm":self.best_regressor, "Model":self.best_model, f"test_{metric.upper()}":best_metric}

    def save_model_weights(self, index):
        import pickle
        with open(f'best_model_weights_{index}.pkl', 'wb') as f:
            pickle.dump(self.get_bestmodel()["Model"].coef_, f)

    def predict(self, value):
        return self.get_bestmodel()["Model"].predict(value)
