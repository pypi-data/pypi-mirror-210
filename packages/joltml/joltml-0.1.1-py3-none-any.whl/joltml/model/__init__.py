import os
from typing import Union, List
import uuid
from datetime import datetime
from joltml.version import VERSION
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class Model(ABC):
    def __init__(
        self,
        native_model=None,
        joltml_version: str = VERSION,
        model_path='.',
        utc_time_created=None,
        model_id=None,
        **kwargs,
    ):
        if native_model:
            self.native_model = native_model
        self.utc_time_created = str(utc_time_created or datetime.utcnow())

        self.metrics = []
        self.splits = 0.2
        self.train_loss_history = None
        self.test_loss_history = None
        if model_id is None:
            self.model_id = str(uuid.uuid4())
        else:
            self.model_id = model_id
        self.joltml_version = joltml_version

    @abstractmethod
    def classification_on(self):
        '''
        '''

    @abstractmethod
    def regression_on(self):
        '''
        '''

    @abstractmethod
    def fit(self, X, y, X_test, y_test):
        '''
        '''

    def prepare_data(self, X):
        return X
    
    def evaluate_metrics(self, metrics, X_test, y_test):
        values = {}
        if y_test is not None and X_test is not None:
            for metric in metrics:
                values[metric.name] = metric.evaluate(
                    y_test, self.prepare_data(self.predict(X_test)))
        return values

    @abstractmethod
    def predict(self, X):
        '''
        '''

    @abstractmethod
    def save_model(self, path):
        '''
        '''

    @abstractmethod
    def fit_optimize(self, X, y, X_test, y_test, params, n_trials, score):
        '''
        '''

    def plot_history(self, path):
        if self.train_loss_history is not None and self.test_loss_history is not None:
            plt.plot(self.train_loss_history, label="Train loss")
            plt.plot(self.test_loss_history, label="Test loss")
            plt.title("Training and test loss curves")
            plt.ylabel("Loss")
            plt.xlabel("Epochs")
            plt.legend()
            plt.savefig(path+'/loss_history')
    
    def explain(self):
        print('No explanation has been implemented for this model.')    
