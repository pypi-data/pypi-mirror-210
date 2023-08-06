from typing import Union

from assertpy import assert_that

from deepdriver.sdk.chart.chart import Chart, TYPE_HISTOGRAM
from deepdriver.sdk.data_types.dataFrame import DataFrame
import numpy as np
import pandas as pd
def histogram(data: DataFrame = None, x: str ="", y: str = "", title: str = "", seq: Union[np.ndarray, list]=None) -> Chart:
    # assert_that(data).is_not_none()
    # assert_that(x).is_not_none()
    assert_that([data, seq]).is_not_none()

    if not data:
        pd_dataframe = pd.DataFrame(np.hstack(seq).tolist(), columns=["x"])
        data = DataFrame(dataframe=pd_dataframe)
        x = "x"

    return Chart(chart_type=TYPE_HISTOGRAM, data=data, data_fields={"x": x, "y": y}, label_fields={"title": title})
