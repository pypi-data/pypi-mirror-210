import logging
from pathlib import Path

import numpy as np
from config.core import LOG_DIR, config
from pipeline import bhousing_pipe
from processing.data_manager import load_dataset, save_pipeline
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from bhousing_model import __version__ as _version


def run_training() -> None:
    """Train the model."""
    # Update logs
    log_path = Path(f"{LOG_DIR}/log_{_version}.log")
    if Path.exists(log_path):
        log_path.unlink()
    logging.basicConfig(filename=log_path, level=logging.DEBUG)

    # read training data
    data = load_dataset(file_name=config.app_config.data_file)

    data["ID"] = data["ID"].astype("int")
    data["CRIM"] = data["CRIM"].astype("float")
    data["ZN"] = data["ZN"].astype("float")
    data["INDUS"] = data["INDUS"].astype("float")
    data["CHAS"] = data["CHAS"].astype("float")
    data["NOX"] = data["NOX"].astype("float")
    data["RM"] = data["RM"].astype("float")
    data["AGE"] = data["AGE"].astype("float")
    data["DIS"] = data["DIS"].astype("float")
    data["RAD"] = data["RAD"].astype("float")
    data["TAX"] = data["TAX"].astype("float")
    data["PTRATIO"] = data["PTRATIO"].astype("float")
    data["B"] = data["B"].astype("float")
    data["LSTAT"] = data["LSTAT"].astype("float")

    data.drop(labels=config.model_config.variables_to_drop, axis=1, inplace=True)

    # divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data[config.model_config.features],  # predictors
        data[config.model_config.target],
        test_size=config.model_config.test_size,
    )

    # fit model
    bhousing_pipe.fit(X_train, y_train)

    # make predictions for train set
    pred = bhousing_pipe.predict(X_train)

    mse_train = mean_squared_error(y_train, pred)
    rmse_train = np.sqrt(mse_train)

    print(f"train RMSE: {rmse_train}")
    print()

    logging.info(f"train RMSE: {rmse_train}")

    # make predictions for test set
    pred = bhousing_pipe.predict(X_test)

    # determine test accuracy and roc-auc
    mse_test = mean_squared_error(y_test, pred)
    rmse_test = np.sqrt(mse_test)

    print(f"test RMSE: {rmse_test}")
    print()

    logging.info(f"test RMSE: {rmse_test}")

    # persist trained model
    save_pipeline(pipeline_to_persist=bhousing_pipe)


if __name__ == "__main__":
    run_training()
