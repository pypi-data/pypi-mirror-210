import logging
from unittest import TestCase

import numpy as np
import pandas as pd

from setting import Setting
import PIL

import deepdriver

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestVisualize(TestCase):
    _login_key = "MTdiNzQxZTc0YTlkZDVhZThiNDZjNzdkNTJiMGQ0ZjExYzIxODYwZTNmNjc2M2MxMGViODNiNjcxNDAyN2JiYw=="
    _artifact_name = "horse2"
    _artifact_type = "dataset"
    _exp_name = "test"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)
        run = deepdriver.init(exp_name=TestVisualize._exp_name,
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    @classmethod
    def tearDownClass(cls):
        deepdriver.finish()

    def test_visualize_line(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        line = deepdriver.line(df, "step", "acc", title="line_chart")
        deepdriver.visualize(line)

    def test_visualize_scatter(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        scatter = deepdriver.scatter(df, "step", "acc", title="scatter_chart")
        deepdriver.visualize(scatter)

    def test_visualize_bar(self):
        x = [i for i in range(1, 31)]
        # random_y = np.random.randint(1, 101, 30)
        random_y = [i * 2 for i in range(1, 31)]
        dataframe = pd.DataFrame({"x": x, "y": random_y})
        df = deepdriver.DataFrame(dataframe=dataframe)
        bar_chart = deepdriver.bar(df, x="x", y="y", title="bar chart")
        deepdriver.visualize(bar_chart)

    def test_visualize_histogram_only_x(self):
        import plotly.express as px
        df = deepdriver.DataFrame(dataframe=px.data.tips())
        histogram = deepdriver.histogram(df, x="total_bill", title="historgram chart")
        deepdriver.visualize(histogram)

    def test_visualize_histogram_with_x_and_y(self):
        import plotly.express as px
        df = deepdriver.DataFrame(dataframe=px.data.tips())
        histogram = deepdriver.histogram(df, x="total_bill", y="tip", title="historgram chart")
        deepdriver.visualize(histogram)

    def test_visualize_histogram_with_np_array(self):
        np_array = np.array([1, 2, 2, 3, 4])
        np_list = [1, 2, 2, 3, 4]
        histogram_chart_np_array = deepdriver.histogram(seq=np_array, title="plot1")
        histogram_chart_list = deepdriver.histogram(seq=np_list, title="plot2")
        deepdriver.visualize(histogram_chart_np_array)
        deepdriver.visualize(histogram_chart_list)

        np_array2 = np.array([[1, 2], [2, 3, 4]])
        np_list2 = [[1, 2], [2, 3, 4]]
        histogram_chart_np_array2 = deepdriver.histogram(seq=np_array2, title= "plot3")
        histogram_chart_list2 = deepdriver.histogram(seq=np_list2, title= "plot4")
        deepdriver.visualize(histogram_chart_np_array2)
        deepdriver.visualize(histogram_chart_list2)

    def test_visualize_confusion_matrix(self):
        y_true = [0, 1, 0, 1, 0, 2, 0, 2, 0, 1, 0, 1, 0, 1, 2, 2]  # 실제값
        preds = [0, 1, 0, 1, 1, 2, 1, 2, 0, 1, 0, 1, 0, 2, 0, 2]  # 예측값
        labels = ["cat", "dog", "horse"]
        confusion_matrix = deepdriver.confusion_matrix(probs=None, y_true=y_true,
                                                       preds=preds, class_names=labels,
                                                       title="my_confusion_matrix")
        deepdriver.visualize(confusion_matrix)

    def test_visualize_roc_curve(self):
        y_true = [1, 0, 0, 1, 1, 0, 1, 0, 1]
        probs = [[0.1, 0.9], [0.9, 0.1], [0.75, 0.25], [0.6, 0.4], [0.3, 0.7], [0.6, 0.4], [0.7, 0.3], [0.5, 0.5],
                 [0.8, 0.2]]
        labels = ["cat", "dog"]
        curve = deepdriver.roc_curve(probs=probs, y_true=y_true, class_names=labels, title="my_roc_curve")
        deepdriver.visualize(curve)

    def test_visualize_table(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        print(df.dataframe)
        table = deepdriver.Table(data=df)
        deepdriver.visualize(table)

    def test_visualize_image(self):
        # image by path
        image = deepdriver.Image("./cat_dog/cat/cat.png")
        deepdriver.visualize(image)

        # image by PIL
        pil_data = PIL.Image.open("./cat_dog/cat/cat.png")
        image = deepdriver.Image(pil_data)
        deepdriver.visualize(image)
