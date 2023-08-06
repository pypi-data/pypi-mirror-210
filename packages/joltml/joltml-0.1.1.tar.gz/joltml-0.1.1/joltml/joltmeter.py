from sklearn.metrics import *
import numpy as np


class JoltMeter:
    def __init__(self, name: str, greater_is_better: bool, function):
        self.name = name
        self.greater_is_better = greater_is_better
        self.function = function

    def evaluate(self, y_true, y_pred):
        return self.function(y_true, y_pred)


def root_mean_squared_error(y, y_pred):
    return np.sqrt(mean_squared_error(y, y_pred))


class RegressionMetrics:
    mean_absolute_error = JoltMeter(name="mean_absolute_error", greater_is_better=False,
                                    function=mean_absolute_error)
    mean_squared_error = JoltMeter(name="mean_squared_error", greater_is_better=False,
                                   function=mean_squared_error)
    root_mean_squared_error = JoltMeter(name="root_mean_squared_error", greater_is_better=False,
                                        function=root_mean_squared_error)
    max_error = JoltMeter(
        name="max_error", greater_is_better=False, function=max_error)
    mean_absolute_percentage_error = JoltMeter(name="mean_absolute_percentage_error",
                                               greater_is_better=False, function=mean_absolute_percentage_error),
    r2_score = JoltMeter(name="r2_score", greater_is_better=True,
                         function=r2_score)


class ClassificationMetrics:
    f1_score = JoltMeter(name="f1_score", greater_is_better=True,
                         function=f1_score)
    auc = JoltMeter(name="auc", greater_is_better=True,
                    function=auc)
