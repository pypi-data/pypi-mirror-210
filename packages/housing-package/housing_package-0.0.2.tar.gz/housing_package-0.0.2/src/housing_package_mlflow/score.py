import argparse
import logging
import os
import pickle
import sys

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from prettytable import PrettyTable
from sklearn.metrics import mean_absolute_error, mean_squared_error

LINEAR_MODEL_FILE = "linear_regression.pkl"
DECISION_TREE_MODEL_FILE = "tree_regression.pkl"
RANDOM_FOREST_MODEL_FILE = "randomforest_regression.pkl"


def score(argv=None):
    parser = argparse.ArgumentParser(description="Scoring the model")
    parser.add_argument("--model-folder", help="path for the model folder", type=str)
    parser.add_argument("--data-folder", help="path for the data folder", type=str)
    parser.add_argument(
        "--log-level",
        help="logging level",
        type=str,
        choices=["DEBUG", "WARNING", "INFO", "ERROR"],
        const="DEBUG",
        nargs="?",
    )
    parser.add_argument("--log-path", help="Log file path", type=str)
    parser.add_argument(
        "--no-console-log",
        help="Log to console",
        type=str,
        choices=["False", "True"],
    )

    args = parser.parse_args()

    if args.model_folder is not None:
        MODEL_PATH = os.path.join(args.model_folder, "models")
    else:
        MODEL_PATH = os.path.join("data", "models")

    if args.data_folder is not None:
        OUTPUT_FOLDER = os.path.join(args.data_folder, "test")
    else:
        OUTPUT_FOLDER = os.path.join("data", "test")

    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

    if args.log_level == "INFO":
        logger.setLevel(logging.INFO)
    elif args.log_level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif args.log_level == "ERROR":
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.DEBUG)

    if args.log_path is not None:
        os.makedirs(args.log_path, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(args.log_path, "score.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if args.no_console_log == "False" or args.no_console_log is None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.debug("Loading test data")
    X_test = pd.read_csv(os.path.join(OUTPUT_FOLDER, "test.csv"))
    y_test = pd.read_csv(os.path.join(OUTPUT_FOLDER, "test_labels.csv"))
    y_test = np.array(y_test).ravel()

    table = PrettyTable(["Model", "MSE", "RMSE", "MAE"])

    linear_list = ["Linear Regression"]
    decision_tree_list = ["Decision Tree"]
    rf_list = ["Random Forest"]

    logger.debug("Predicting and calculating metric for Linear Model")
    with open(os.path.join(MODEL_PATH, LINEAR_MODEL_FILE), "rb") as file:
        model = pickle.load(file=file)

    housing_predictions = model.predict(X_test)
    lin_mse = mean_squared_error(y_test, housing_predictions)
    lin_rmse = np.sqrt(lin_mse)
    lin_mae = mean_absolute_error(y_test, housing_predictions)
    linear_list.extend([lin_mse, lin_rmse, lin_mae])
    linear_regression_metrics = {
        "lr_mse": lin_mse,
        "lr_rmse": lin_rmse,
        "lr_mae": lin_mae,
    }

    logger.debug("Predicting and calculating metric for Decision Tree Model")
    with open(os.path.join(MODEL_PATH, DECISION_TREE_MODEL_FILE), "rb") as file:
        model = pickle.load(file=file)

    housing_predictions = model.predict(X_test)
    tree_mse = mean_squared_error(y_test, housing_predictions)
    tree_rmse = np.sqrt(tree_mse)
    tree_mae = mean_absolute_error(y_test, housing_predictions)
    decision_tree_list.extend([tree_mse, tree_rmse, tree_mae])
    decision_tree_metrics = {
        "dt_mse": tree_mse,
        "dt_rmse": tree_rmse,
        "dt_mae": tree_mae,
    }

    logger.debug("Predicting and calculating metric for Random Forest Model")
    with open(os.path.join(MODEL_PATH, RANDOM_FOREST_MODEL_FILE), "rb") as file:
        model = pickle.load(file=file)

    housing_predictions = model.predict(X_test)
    rf_mse = mean_squared_error(y_test, housing_predictions)
    rf_rmse = np.sqrt(rf_mse)
    rf_mae = mean_absolute_error(y_test, housing_predictions)
    rf_list.extend([rf_mse, rf_rmse, rf_mae])
    random_forest_metrics = {"rf_mse": rf_mse, "rf_rmse": rf_rmse, "rf_mae": rf_mae}

    logger.debug("Printing the scores in a table")
    table.add_row(linear_list)
    table.add_row(decision_tree_list)
    table.add_row(rf_list)

    print(table)

    # score = pd.DataFrame(table, columns=["Model", "MSE", "RMSE", "MAE"])
    SCORE_PATH = os.path.join("data", "models")
    # table.to_csv(os.path.join(SCORE_PATH, "score.csv"), index=False)
    tbl_as_csv = table.get_csv_string().replace("\r", "")
    text_file = open(os.path.join(SCORE_PATH, "score.csv"), "w")
    n = text_file.write(tbl_as_csv)
    text_file.close()

    logger.debug("Completed")
    with mlflow.start_run(experiment_id=1, run_name="Score", nested=True):
        mlflow.log_metrics(linear_regression_metrics)
        mlflow.log_metrics(decision_tree_metrics)
        mlflow.log_metrics(random_forest_metrics)


if __name__ == "__main__":
    score(sys.argv)
