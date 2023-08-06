from sklearn.base import BaseEstimator
from joltml.model import Model


class Sklearn(Model):
    def __init__(self, native_model: BaseEstimator = None, joltml_version: str = ..., model_path='.', utc_time_created=None, model_id=None, **kwargs):
        super().__init__(native_model, joltml_version,
                         model_path, utc_time_created, model_id, **kwargs)

    def classification_on(self):
        super().classification_on()

    def regression_on(self):
        super().regression_on()

    def fit(self, X, y, X_test, y_test):
        super().fit(X, y, X_test, y_test)
        self.native_model.fit(X, y)

    def predict(self, X):
        return self.native_model.predict(X)
    
    def fit_optimize(self, X, y, X_test, y_test, params, n_trials, score):
        return super().fit_optimize(X, y, X_test, y_test, params, n_trials, score)
    
    def save_model(self, path):
        from joblib import dump, load
        print('Saving model', self.model_id, 'in', path)
        dump(self.native_model, path + '.joblib') 
    
