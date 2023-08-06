#!/usr/bin/env python3
from tensorflow.keras import Model
from typing import List
import tensorflow as tf

class BaselineModel(Model):

    def __init__(self, labels: 'object' = None):
        super().__init__()
        self.labels: List[int] = labels

    def call(self, inputs):

        if self.labels == None:
            return inputs

        elif isinstance(self.labels, List):

            tensors: List = []
            for index in self.labels:
                result = inputs[:, :, index]
                result = result[:, :, tf.newaxis]
                tensors.append(result)

            return tf.concat(tensors, axis=-1)

        result = inputs[:, :, self.labels]
        return result[:, :, tf.newaxis]

class MultiStepLastBaselineModel(Model):

    def __init__(self, labels: 'object' =None, step_back: int = 1):
        self.step: int = step_back
        super().__init__()
        self.labels: List[int] = labels

    def call(self, inputs):
        if self.labels is None:
            return tf.tile(inputs[:, -1:, :], [1, self.step, 1])

        return tf.tile(inputs[:, -1:, self.labels:], [1, self.step, 1])


class RepeatBaselineModel(Model):
    def __init__(self, labels: 'object' =None):
        super().__init__()
        self.labels: List[int] = labels

    def call(self, inputs):
        return inputs[:, :, self.labels:]