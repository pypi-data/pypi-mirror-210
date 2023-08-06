import json
import uuid
from datetime import datetime
import os
from joltml.joltmeter import RegressionMetrics, ClassificationMetrics
from sklearn.model_selection import train_test_split
from typing import List, Union
from numpy.typing import ArrayLike
import pandas as pd


class Fit:
    def __init__(self, experiment_id, dataset, splits=0.2,
                 inputs: List[str] = None, target_names: Union[List[str], str] = None, targets: Union[ArrayLike, pd.DataFrame] = None, normalizer=None,
                 path='./jolt_lab/',
                 fit_id=None,
                 utc_creation_time=None,
                 utc_last_update_time=None,
                 scaler=None) -> None:
        if fit_id is None:
            self.fit_id = str(uuid.uuid4())
        else:
            self.fit_id = fit_id

        self.dataset = dataset
        self.experiment_id = experiment_id
        self.path = path
        self.utc_creation_time = str(utc_creation_time or datetime.utcnow())
        self.utc_last_update_time = utc_last_update_time

        self.X = None
        self.y = None

        self.normalizer = normalizer

        self._set_axes(inputs=inputs, targets=targets, target_names=target_names)

        self.splits = splits
        if self.X is not None and self.y is not None:
            if isinstance(splits, list):
                if len(splits) == 2:
                    # Split into training and test
                    self.splits = splits[1]
            elif isinstance(splits, float):
                self.splits = splits
            else:
                raise Exception(
                    "The 'splits' parameter should either be a list of 2-3 elements, or just a number.")
            self._split_datasets()

        if scaler:
            self._set_scaler(scaler)

        self.fits_book = {
            'experiment_id': self.experiment_id,
            'fit_id': self.fit_id,
            'utc_creation_time': self.utc_creation_time,
            'utc_last_update_time': self.utc_last_update_time,
            'joltmeter': {}
        }

        os.mkdir(self.path + '/jolt_lab/' +
                 self.experiment_id + '/' + self.fit_id)
        os.mkdir(self.path + '/jolt_lab/' + self.experiment_id +
                 '/' + self.fit_id + '/models')

        self._write_fits_book()

    def _split_datasets(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=self.splits, random_state=42)

    def _set_axes(self, inputs: List[str] = None, target_names: Union[List[str], str] = None, targets: Union[ArrayLike, pd.DataFrame] = None):
        """
        Parameters
        ----------
        inputs : List[str]
            Column names to be used as input
        targets : Union[str, List[str], pd.DataFrame]
            Column names to be used as output, or a DataFrame of the output column
        """
        if target_names is not None and targets is not None:
            raise Exception(
                'Either targets or target_names should be specified, not both.')
        if target_names is not None:
            if isinstance(target_names, list):
                if len(target_names) == 1:
                    target_names = target_names[0]
                else:
                    raise Exception(
                        'Currently supports only one target column.')

            if isinstance(target_names, str) and target_names in self.dataset.columns:
                self.y = self.dataset[target_names]
            elif isinstance(target_names, str) and target_names not in self.dataset.columns:
                raise Exception('No column named '+target_names+' in the dataset.')

        elif isinstance(targets, pd.DataFrame):
            self.y = targets.iloc[:, 0]
        elif isinstance(targets, ArrayLike):
            self.y = targets
        else:
            raise Exception('Target column type not recognized.')

        if inputs is None:
            if target_names is not None:
                inputs = []
                for c in self.dataset.columns:
                    if c != target_names:
                        inputs += [c]
                self.X = self.dataset[inputs]
            elif targets is not None:
                self.X = self.dataset
        elif inputs is not None:
            self.X = self.dataset[inputs]

    def regression(self, model, metrics=None):
        model.regression_on()
        if metrics is None:
            self.metrics = [RegressionMetrics.mean_absolute_error,
                            RegressionMetrics.r2_score, RegressionMetrics.mean_squared_error]
        else:
            self.metrics = metrics
        model.fit(self.X_train, self.y_train, self.X_test, self.y_test)
        model.plot_history(self.path + '/jolt_lab/' +
                           self.experiment_id + '/' + self.fit_id)

    def regression_optimize(self, model, metrics=None, params=None, n_trials=10, score=None):
        model.regression_on()
        if metrics is None:
            self.metrics = [RegressionMetrics.mean_absolute_error,
                            RegressionMetrics.r2_score, RegressionMetrics.mean_squared_error]
        else:
            self.metrics = metrics
        model.fit_optimize(self.X_train, self.y_train,
                           self.X_test, self.y_test, params, n_trials, score)

    def classification(self, model, metrics=None):
        model.classification_on()
        if metrics is None:
            self.metrics = [ClassificationMetrics.f1_score,
                            ClassificationMetrics.auc]
        else:
            self.metrics = metrics
        model.fit(self.X_train, self.y_train, self.X_test, self.y_test)
        model.plot_history(self.path + '/jolt_lab/' +
                           self.experiment_id + '/' + self.fit_id)

    def set_dataset(self, dataset):
        self.dataset = dataset

    def _write_fits_book(self):
        self.fits_book['utc_last_update_time'] = str(datetime.utcnow())
        fits_book_f = open(self.path + '/jolt_lab/' +
                           self.experiment_id + '/' + self.fit_id + '/fits_book.json', 'w')
        json.dump(self.fits_book, fits_book_f)
        fits_book_f.close()

    def save_model(self, model):
        model.save_model(path=self.path + '/jolt_lab/' + self.experiment_id +
                         '/'+self.fit_id + '/models/' + model.model_id)

    def save_metrics(self, model):
        metrics = model.evaluate_metrics(
            self.metrics, self.X_test, self.y_test)
        self.fits_book['joltmeter'][model.model_id] = metrics
        self._write_fits_book()

    def _set_scaler(self, scaler_class):
        self.scaler = scaler_class.fit(self.X_train)
        self.X_train = self.scaler.transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)

    def plot_loss(self):
        pass
