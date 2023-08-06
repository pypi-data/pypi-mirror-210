import re
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from bhousing_model.config.core import config


def validate_inputs(*, input_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    # cast numerical variables as floats
    input_data["ID"] = input_data["ID"].astype("int")
    input_data["CRIM"] = input_data["CRIM"].astype("float")
    input_data["ZN"] = input_data["ZN"].astype("float")
    input_data["INDUS"] = input_data["INDUS"].astype("float")
    input_data["CHAS"] = input_data["CHAS"].astype("float")
    input_data["NOX"] = input_data["NOX"].astype("float")
    input_data["RM"] = input_data["RM"].astype("float")
    input_data["AGE"] = input_data["AGE"].astype("float")
    input_data["DIS"] = input_data["DIS"].astype("float")
    input_data["RAD"] = input_data["RAD"].astype("float")
    input_data["TAX"] = input_data["TAX"].astype("float")
    input_data["PTRATIO"] = input_data["PTRATIO"].astype("float")
    input_data["B"] = input_data["B"].astype("float")
    input_data["LSTAT"] = input_data["LSTAT"].astype("float")

    input_data.drop(labels=config.model_config.variables_to_drop, axis=1, inplace=True)

    relevant_data = input_data[config.model_config.features].copy()

    errors = None

    try:
        # replace numpy nans so that pydantic can validate
        MultipleBHousingInputs(inputs=relevant_data.replace({np.nan: None}).to_dict(orient="records"))
    except ValidationError as error:
        errors = error.json()

    return relevant_data, errors


class BHousingInputSchema(BaseModel):
    ID: Optional[int]
    CRIM: Optional[np.float64] = Field(None, alias="CRIM")
    ZN: Optional[np.float64] = Field(None, alias="ZN")
    INDUS: Optional[np.float64] = Field(None, alias="INDUS")
    CHAS: Optional[np.float64] = Field(None, alias="CHAS")
    NOX: Optional[np.float64] = Field(None, alias="NOX")
    RM: Optional[np.float64] = Field(None, alias="RM")
    AGE: Optional[np.float64] = Field(None, alias="AGE")
    DIS: Optional[np.float64] = Field(None, alias="DIS")
    RAD: Optional[np.float64] = Field(None, alias="RAD")
    TAX: Optional[np.float64] = Field(None, alias="TAX")
    PTRATIO: Optional[np.float64] = Field(None, alias="PTRATIO")
    B: Optional[np.float64] = Field(None, alias="B")
    LSTAT: Optional[np.float64] = Field(None, alias="LSTAT")


class MultipleBHousingInputs(BaseModel):
    inputs: List[BHousingInputSchema]
