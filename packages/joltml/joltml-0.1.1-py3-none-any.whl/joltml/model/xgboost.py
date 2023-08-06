import xgboost
from joltml.model import Model
import optuna
from joltml.joltmeter import RegressionMetrics, ClassificationMetrics


class Xgboost(Model):

    def __init__(self, native_model=None, joltml_version: str = ..., model_path='.', utc_time_created=None, model_id=None, **kwargs):
        super().__init__(native_model, joltml_version,
                         model_path, utc_time_created, model_id, **kwargs)

    def classification_on(self):
        super().classification_on()
        self.native_model = xgboost.XGBClassifier()

    def regression_on(self):
        super().regression_on()
        self.native_model = xgboost.XGBRegressor()

    def fit(self, X, y, X_test, y_test):
        super().fit(X, y, X_test, y_test)
        self.native_model.fit(X, y, eval_set=[(X_test, y_test)])

    def predict(self, X):
        return self.native_model.predict(X)

    def fit_optimize(self, X, y, X_test, y_test, params, n_trials, score):
        if score is None:
            if isinstance(self.native_model, xgboost.XGBRegressor):
                score = RegressionMetrics.mean_absolute_error
            elif isinstance(self.native_model, xgboost.XGBClassifier):
                score = ClassificationMetrics.auc

        def objective(trial):
            for key in params:
                parameter = {}
                value = params[key]
                if value['type'] == 'float':
                    parameter[key] = trial.suggest_float(
                        key, value['minimum'], value['maximum'], log=True)
                elif value['type'] == 'int':
                    parameter[key] = trial.suggest_int(
                        key, value['minimum'], value['maximum'], log=True)
                elif value['type'] == 'categorical':
                    parameter[key] = trial.suggest_categorical(
                        key, value['values'])
                self.native_model.set_params(**parameter)
            self.fit(X, y, eval_set=[(X_test, y_test)])
            return score.evaluate(self.native_model.predict(X_test), y_test)
        if score.greater_is_better:
            study = optuna.create_study(direction="maximize")
        else:
            study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=n_trials)

    def save_model(self, path):
        print('Saving model', self.model_id, 'in', path)
        self.native_model.save_model(path+'.json')
