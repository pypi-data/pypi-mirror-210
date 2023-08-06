# pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline

# feature scaling
from sklearn.preprocessing import MinMaxScaler

from bhousing_model.config.core import config

# set up the pipeline
bhousing_pipe = Pipeline(
    [
        # scale
        ("scaler", MinMaxScaler()),
        (
            "GDB",
            GradientBoostingRegressor(
                learning_rate=config.model_config.learning_rate,
                max_depth=config.model_config.max_depth,
                n_estimators=config.model_config.n_estimators,
            ),
        ),
    ]
)
