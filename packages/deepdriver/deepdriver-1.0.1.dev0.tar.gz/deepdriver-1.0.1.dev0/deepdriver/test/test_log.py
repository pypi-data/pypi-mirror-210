import logging
from unittest import TestCase

import PIL
from setting import Setting
import deepdriver

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestLog(TestCase):
    _artifact_name = "arti_1"
    _artifact_type = "arti_type"
    _exp_name = "test_log_project2"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)
        run = deepdriver.init(exp_name=TestLog._exp_name,run_name="run-1",
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    @classmethod
    def tearDownClass(cls):
        deepdriver.finish()

    def test_table_log(self):
        deep_df = deepdriver.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        table = deepdriver.Table(data=deep_df)
        print(table.to_json("table"))
        # table.upload()    # not use
        deepdriver.log({"table": table, "a": "b"})

    def test_value_log(self):
        deepdriver.log({"acc": 0.8})

    def test_image_log_str(self):
        image = deepdriver.Image("./cat_dog/cat/cat.png")
        print(image.to_json("image"))
        deepdriver.log({"image_str": image, "a": "b"})

    def test_image_log_PIL(self):
        pil_data = PIL.Image.open("./cat_dog/cat/cat.png")
        image = deepdriver.Image(pil_data)
        print(image.to_json("image"))
        deepdriver.log({"image_pil": image, "a": "b"})

    def test_line_chart_log(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        line = deepdriver.line(df, "step", "acc", title="line_chart")
        print(line.to_json("line", only_meta=True))
        deepdriver.log({"line": line, "a": "b"})

    def test_scatter_chart_log(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        scatter = deepdriver.scatter(df, "step", "acc", title="scatter_chart")
        deepdriver.log({"scatter": scatter, "a": "b"})

    def test_histogram_chart_log(self):
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])
        histogram = deepdriver.histogram(df, "step", "acc", title="scatter_chart")
        deepdriver.log({"histogram": histogram, "a": "b"})

    def test_confusion_matrix_chart_log(self):
        y_true = [0, 1, 0, 1, 0]  # 실제값
        preds = [0, 1, 0, 1, 1]  # 예측값
        labels = ["cat", "dog"]
        confusion_matrix = deepdriver.confusion_matrix(probs=None, y_true=y_true,
                                                       preds=preds, class_names=labels,
                                                       title="my_confusion_matrix")
        deepdriver.log({"confusion_matrix": confusion_matrix, "a": "b"})

    def test_log_type_check(self):
        deep_df = deepdriver.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        table = deepdriver.Table(data=deep_df)
        print(table.to_json("table", only_meta=True))

        import datetime
        with self.assertRaises(Exception) as e:
            print(e)
            deepdriver.log({"table": table, "a": "b",
                            "datetime_instance": datetime.datetime.now()})  # datetime instance not support
