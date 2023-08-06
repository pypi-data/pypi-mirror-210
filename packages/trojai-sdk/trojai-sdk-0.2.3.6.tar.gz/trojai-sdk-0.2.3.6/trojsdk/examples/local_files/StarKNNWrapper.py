"""Some model for testing"""

import copy
import pickle
import numpy as np
from sklearn.preprocessing import FunctionTransformer
import pandas as pd


def process_color(x):
    valid_colors = [
        "red",
        "blue",
        "yellow white",
        "blue white",
        "pale yellow orange",
        "white",
        "orange",
        "white yellow",
        "yellow",
    ]
    x = x.lower()
    x = x.replace("-", " ")
    x = x.replace("ish", "")
    if x == "whit":
        x = "white"
    if x not in valid_colors:
        x = "unknown"
    valid_colors.append("unknown")
    x = valid_colors.index(x)
    return x


def process_spectral(x):
    valid_spectral = ["M", "B", "O", "F", "A", "G", "K"]
    if x.upper() not in valid_spectral:
        x = "unknown"
    valid_spectral.append("unknown")
    x = valid_spectral.index(x)
    return x


def preprocess_strs(X):
    if type(X) == pd.DataFrame:
        X = X.values
    new_dat = []
    if len(np.array(X).shape) == 1:
        X = np.expand_dims(X, axis=1)
    for dat in X:
        dat[1] = process_color(dat[1])
        dat[2] = process_spectral(dat[2])
        new_dat.append(dat)
    return new_dat


class ModelWrapper:

    """Wrapper for"""

    def __init__(self, model_file):
        self.model = pickle.load(open(model_file, "rb"))
        self.string_processor = FunctionTransformer(preprocess_strs)

    def predict(self, x):
        """
        Predict stuff

        :param x:
        :return:
        """
        x = self.string_processor.transform(x)
        probs = self.model.predict(x)
        return probs

    def predict_proba(self, x):
        """
        Predict stuff

        :param x:
        :return:
        """

        x = self.string_processor.transform(x)
        probs = self.model.predict_proba(x)
        return probs

    def predict_dict(self, x):
        """
        Predict stuff from dictionary

        :param x:
        :return:
        """

        transform_dict = copy.copy(x)
        # transform_dict["Color"] = self.process_color(x["Color"])
        # transform_dict["Spectral_Class"] = self.process_spectral(x["Spectral_Class"])
        input_vals = np.array([list(transform_dict.values())])
        input_vals = self.string_processor.transform(input_vals)
        outs = self.predict_proba(input_vals)

        return outs
