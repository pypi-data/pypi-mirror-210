#!/usr/bine/env python3
from tensorflow.keras.preprocessing import timeseries_dataset_from_array
import tensorflow as tf
import pandas as pd
import numpy as np
from typing import List, Dict
import matplotlib.pyplot as plt

class Window(object):

    def __init__(self,
                 input_width: int,
                 label_width: int,
                 shift: int,
                 df: 'DataFrame',
                 cols: List[str],
                 splits: tuple = (0.7, 0.9)):

        self.input_width: int = input_width
        self.label_width: int = label_width
        self.shift: int = shift
        self.columns: List[str] = cols

        a, b = splits
        size: int = df.shape[0]
        self.train_df: 'DataFrame' = df.iloc[:int(size * a)]
        self.val_df: 'DataFrame' = df[int(size * a): int(size * b)]
        self.test_df: 'DataFrame' = df[int(size * b):]

        self.lookup_tbl: Dict = {col: index for index, col in enumerate(cols)}
        self.column_index: Dict = {col: index for index, col in enumerate(self.train_df)}

        # inputs
        self.window_size: int = self.input_width + self.shift
        self.input_slice: 'slice' = slice(0, self.input_width)
        self.input_index: 'np.arange' = np.arange(self.window_size)[self.input_slice]

        # labels
        self.label_start: int = self.window_size - self.label_width
        self.label_slice: 'slice' = slice(self.label_start, None)
        self.label_index: 'np.arange' = np.arange(self.window_size)[self.label_slice]

        if size == 0:
            raise ValueError("DataFrame cannot be empty.")

    def split_input(self, features):

        inputs = features[:, self.input_slice, :]
        labels = features[:, self.label_slice, :]

        if self.columns:
            labels = tf.stack([labels[:, :, self.column_index[col]] for col in self.columns], axis=-1)

        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])

        return inputs, labels

    def to_timeseries(self, data: 'np.array') -> 'timeseries':

        data: 'np.array' = np.array(data, dtype=np.float32)
        df: 'timeseries' = timeseries_dataset_from_array(data=data,
                                                         targets=None,
                                                         sequence_length=self.window_size,
                                                         sequence_stride=1,
                                                         shuffle=True,
                                                         batch_size=32)

        return df.map(self.split_input)

    def plot(self, model: 'Model', col_name: str, plt_title: str, y_label: str, max_subplt: int = 3) -> 'ax':

        if not all([model, col_name, plt_title, y_label]):
            raise ValueError("The following parameters are required model, col_name, plt_title, y_label" )

        plt.rcParams['figure.figsize'] = (20, 10)
        inputs, labels = self.get_sample_batch
        col_index: int = self.column_index[col_name]
        max_n: int = max(max_subplt, len(inputs))

        for n in range(max_n):
            if n + 1 > 3:
                continue

            plt.subplot(3, 1, n + 1)
            plt.ylabel(y_label, fontweight='bold')
            plt.plot(self.input_index,
                     inputs[n, :, col_index],
                     label="Inputs",
                     marker=".",
                     mec='black',
                     mew=1.8,
                     zorder=-10)

            if self.columns:
                label_index = self.column_index.get(col_name, None)

            else:
                label_index: int = col_index

            if label_index == None:
                continue

            plt.scatter(self.label_index,
                        labels[n, :, label_index],
                        marker="s",
                        s=32,
                        color='green',
                        label="Labels",
                        edgecolor='k')

            if model:
                predictions: 'Model' = model(inputs)
                plt.scatter(self.label_index,
                            predictions[n, :, label_index],
                            marker="X",
                            s=32,
                            color='red',
                            label="Predictions",
                            edgecolor='k')
            if n == 0:
                plt.title(plt_title, fontweight='bold', fontsize=20)
                plt.legend(title="Description", fancybox=True, shadow=True, bbox_to_anchor=(1, 1))

            plt.grid(True)

        plt.xlabel("Time", fontweight='bold')
        return plt

    @property
    def train(self):
        return self.to_timeseries(data=self.train_df)

    @property
    def validation(self):
        return self.to_timeseries(data=self.val_df)

    @property
    def test(self):
        return self.to_timeseries(data=self.test_df)

    @property
    def get_sample_batch(self):
        current_batch = getattr(self, "_sample_batch", None)
        if current_batch == None:
            current_batch = next(iter(self.train))
            self._sample_batch = current_batch

        return current_batch

