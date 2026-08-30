"""Evaluation and plotting utilities for legacy adaptation-rule models."""

import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.preprocessing import binarize

import machine_learning


DATASET_PATH = "data/dataset.csv"
CONFIGURATIONS_PATH = "data/configurations.csv"
EVALUATION_DATASET_PATH = "data/model_evaluation_data.csv"


def _load_evaluation_data(dataset_path=DATASET_PATH, header="infer"):
    data = pd.read_csv(dataset_path, header=header)
    features = machine_learning.transform_dataset(
        data.iloc[:, :-1].values,
        list(range(data.shape[1] - 1)),
    )
    targets = np.asarray(data.iloc[:, -1].values).ravel()
    return features, targets


def _train_comparison_models():
    return [
        machine_learning.train_linear_regression(DATASET_PATH),
        machine_learning.train_neural_network(DATASET_PATH),
        machine_learning.train_lasso_regression(DATASET_PATH),
    ]


def evaluate_autoencoder():
    """Train the autoencoder and write predictions for generated configurations."""
    model = machine_learning.train_autoencoder()
    predictions = machine_learning.predict_model_results(model, CONFIGURATIONS_PATH)
    machine_learning.save_predictions(
        predictions,
        "data/autoencoder_predictions.csv",
    )


def plot_roc_curves():
    test_features, test_targets = _load_evaluation_data()
    figure, axis = plt.subplots()
    for model in _train_comparison_models():
        predicted_targets = np.asarray(model.predict(test_features)).ravel()
        area = roc_auc_score(test_targets, predicted_targets, multi_class="ovo", average=None)
        metrics.plot_roc_curve(
            model,
            test_features,
            test_targets,
            ax=axis,
            name=f"{type(model).__name__}, AUC={area:.2f}",
        )
    axis.plot([0, 1], [0, 1], linestyle="--", color="r", label="Random classifier")
    axis.legend()
    axis.set_title("Receiver Operating Characteristic Curves")
    plt.show()


def plot_regression_comparison():
    test_features, test_targets = _load_evaluation_data()
    models = _train_comparison_models()
    predictions = [np.asarray(model.predict(test_features)).ravel() for model in models]
    labels = [
        "Multiple linear regression",
        "Neural network",
        "Regularized linear regression",
    ]
    plt.figure(figsize=(8, 6))
    for model_label, predicted_targets in zip(labels, predictions):
        score = r2_score(test_targets, predicted_targets)
        print(f"{model_label}: {len(predicted_targets)} predictions")
        plt.scatter(
            test_targets,
            predicted_targets,
            label=f"{model_label} (R-squared={score:.2f})",
        )
    plt.plot(
        [test_targets.min(), test_targets.max()],
        [test_targets.min(), test_targets.max()],
        "k--",
        linewidth=3,
    )
    plt.xlabel("Observed value")
    plt.ylabel("Predicted value")
    plt.title("Regression Model Comparison")
    plt.legend()
    plt.show()


def plot_unlabeled_data_comparison():
    data = pd.read_csv(CONFIGURATIONS_PATH, header=None)
    prediction_features = machine_learning.transform_dataset(
        data.values,
        list(range(data.shape[1])),
    )
    figure, axis = plt.subplots()
    axis.set_xlabel("Configuration index")
    axis.set_ylabel("Predicted adaptation rule")
    axis.set_title("Regression Model Comparison on Unlabeled Data")
    for model in _train_comparison_models():
        predicted_targets = model.predict(prediction_features)
        axis.scatter(
            range(1, len(predicted_targets) + 1),
            predicted_targets,
            alpha=0.5,
            label=type(model).__name__,
        )
    axis.legend()
    plt.show()


def plot_binarized_roc_curves():
    test_features, test_targets = _load_evaluation_data()
    figure, axis = plt.subplots()
    for model in _train_comparison_models():
        predicted_targets = np.asarray(model.predict(test_features)).ravel()
        if type(model).__name__ == "LinearRegression":
            predicted_targets = binarize(
                predicted_targets.reshape(1, -1), threshold=0.5
            )[0]
        area = roc_auc_score(test_targets, predicted_targets, multi_class="ovo", average=None)
        metrics.plot_roc_curve(
            model,
            test_features,
            test_targets,
            ax=axis,
            name=f"{type(model).__name__}, AUC={area:.2f}",
        )
    axis.plot([0, 1], [0, 1], linestyle="--", color="r", label="Random classifier")
    axis.legend()
    axis.set_title("Binarized Receiver Operating Characteristic Curves")
    plt.show()


def plot_model_evaluation_comparison():
    test_features, test_targets = _load_evaluation_data(
        EVALUATION_DATASET_PATH,
        header=None,
    )
    models = _train_comparison_models()
    predicted_targets = [
        np.asarray(model.predict(test_features)).ravel() for model in models
    ]
    labels = [
        "Multiple linear regression",
        "Neural network",
        "Regularized linear regression",
    ]
    print(f"Evaluation rows: {len(test_features)}")
    plt.figure(figsize=(8, 6))
    for model_label, predictions in zip(labels, predicted_targets):
        score = r2_score(test_targets, predictions)
        print(f"{model_label}: {len(predictions)} predictions")
        plt.scatter(
            test_targets,
            predictions,
            label=f"{model_label} (R-squared={score:.2f})",
        )
    plt.plot(
        [test_targets.min(), test_targets.max()],
        [test_targets.min(), test_targets.max()],
        "k--",
        linewidth=3,
    )
    plt.xlabel("Observed value")
    plt.ylabel("Predicted value")
    plt.title("Evaluation-Dataset Regression Comparison")
    plt.legend()
    plt.show()


def filter_csv(input_path, output_path, column_index, expected_value):
    """Write rows whose selected column equals the requested value."""
    with open(input_path, "r", newline="", encoding="utf-8") as input_file:
        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            reader = csv.reader(input_file, delimiter=",")
            writer = csv.writer(output_file, delimiter=",")
            writer.writerow(next(reader))
            for row in reader:
                if row[column_index] == expected_value:
                    writer.writerow(row)


if __name__ == "__main__":
    staged_predictions = machine_learning.train_staged_transfer_model()
    if staged_predictions is not None:
        machine_learning.save_predictions(
            staged_predictions,
            "data/deep_neural_network_predictions.csv",
        )
