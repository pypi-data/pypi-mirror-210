import logging
from unittest import TestCase
from setting import Setting
import deepdriver

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestArtifact(TestCase):
    _artifact_name = "horse5"
    _artifact_type = "dataset"
    _exp_name = "test5"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt, use_grpc_tls=True, use_https=True)
        login_result = deepdriver.login(
            id=Setting.ID, pw=Setting.PW)

        run = deepdriver.init(exp_name=TestArtifact._exp_name,
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    @classmethod
    def tearDownClass(cls):
        deepdriver.finish()

    def test_artifact_init(self):
        # artifact 초기화(Artifact())
        arti = deepdriver.Artifacts(name=self._artifact_name, type=self._artifact_type)
        logger.info(f"artfact info : {arti.__dict__}")
        deepdriver.upload_artifact(arti)
        logger.info(f"created arti id : {arti.id}")

    def test_artifact_init_and_add_file(self):
        # artifact 초기화(Artifact())
        arti = deepdriver.Artifacts(name=self._artifact_name, type=self._artifact_type)
        logger.info(f"artfact info : {arti.__dict__}")
        arti.add("cat_dog")
        deepdriver.upload_artifact(arti)

    def test_get_artifact(self):
        arti = deepdriver.get_artifact(name=self._artifact_name, type=self._artifact_type)
        logger.info(f"artfact info : {arti.__dict__}")
        for idx, entry in enumerate(arti.entry_list):
            logger.info(f"artfact entry [{idx}]: {entry.path}")
        deepdriver.upload_artifact(arti)

    def test_artifact_file_upload(self):
        # artifact 파일 업로드
        arti = deepdriver.get_artifact(name=self._artifact_name, type=self._artifact_type)
        logger.info(f"artfact info : {arti.__dict__}")
        arti.add("cat_dog")
        deepdriver.upload_artifact(arti)

    def test_artifact_file_download(self):
        # artifact 파일 다운로드
        arti = deepdriver.get_artifact(name=self._artifact_name, type=self._artifact_type)
        logger.info(f"artfact info : {arti.__dict__}")
        for idx, entry in enumerate(arti.entry_list):
            logger.info(f"artfact entry [{idx}]: {entry.path}")
        arti.download()
        print(arti.get_download_dir())

    def test_artifact_download_and_upload(self):
        # artifact 파일 다운로드
        arti = deepdriver.Artifacts(name="animal", type="dataset")
        arti.add("cat_dog")
        deepdriver.upload_artifact(arti)

        arti2 = deepdriver.get_artifact(name="animal", type="dataset")
        arti2.add("horse")
        deepdriver.upload_artifact(arti2)

    def test_artifact_add_table(self):
        arti = deepdriver.Artifacts(name="result2", type="result")
        deep_df = deepdriver.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        table = deepdriver.Table(data=deep_df)
        arti.add(table, "table1")
        deepdriver.upload_artifact(arti)

    def test_artifact_get_table(self):
        arti2 = deepdriver.get_artifact(name="result2", type="result")
        with self.assertRaises(Exception):  # 존재하지 않는 key
            arti2.get("not_exist")
        table = arti2.get("table1")
        deepdriver.visualize(table)

    def test_artifact_add_image(self):
        arti = deepdriver.Artifacts(name="result11_1", type="result")
        class_labels = {
            0: "person",
            1: "car",
            2: "road",
            3: "building"
        }
        image = deepdriver.Image("./cat_dog/dog/dog.png")
        image_with_boxes = deepdriver.Image("./cat_dog/dog/dog.png", boxes={
            "predictions": {
                "box_data": [
                    {
                        # one box expressed in the default relative/fractional unit
                        "position": {
                            "minX": 0.1,
                            "maxX": 0.2,
                            "minY": 0.3,
                            "maxY": 0.4
                        },
                        "class_id": 1,
                        "caption": class_labels[1],
                        "scores": {
                            "acc": 0.2,
                            "loss": 1.2
                        }
                    },
                    {
                        # another box expressed in the pixel domain
                        "position": {
                            "minX": 300,
                            "maxX": 350,
                            "minY": 100,
                            "maxY": 200
                        },
                        "domain": "pixel",
                        "class_id": 3,
                        "caption": "a building",
                        "scores": {
                            "acc": 0.5,
                            "loss": 0.7
                        }
                    },
                    # Log as many boxes an as needed
                ],
                "class_labels": class_labels
            }
        }, caption="test_caption")
        arti.add(image, "image")
        arti.add(image_with_boxes, "image_with_boxes")
        deepdriver.upload_artifact(arti)

    def test_artifact_get_image(self):
        arti2 = deepdriver.get_artifact(name="result11_1", type="result")
        image_with_boxes = arti2.get("image_with_boxes")
        print(image_with_boxes.to_dict(""))   # json 파싱하여 Image 객체로 생성했는지 확인
        image = arti2.get("image")
        print(image.to_dict(""))  # json 파싱없이 Image 객체로 생성했는지 확인
        # deepdriver.visualize(image)


    def test_artifact_add_image_array(self):
        arti = deepdriver.get_artifact(name="result10_1", type="result")
        image1 = deepdriver.Image("./cat_dog/dog/dog.png")
        image2 = deepdriver.Image("./cat_dog/cat/cat.png")
        arti.add(data=[image1, image2], name="image_array")
        deepdriver.upload_artifact(arti)

    def test_artifact_get_image_array(self):
        arti = deepdriver.get_artifact(name="result10_1", type="result")
        image_list = arti.get("image_array")
        deepdriver.visualize(image_list[0])
        deepdriver.visualize(image_list[1])

    def test_artifact_add_chart(self):
        arti = deepdriver.Artifacts(name="result5", type="result")
        # make line chart
        accuracy = [0.81, 0.82, 0.83, 0.84, 0.90, 0.92, 0.94, 0.93, 0.94, 0.93]
        df = deepdriver.DataFrame(columns=["step", "acc"], data=[[idx, acc] for idx, acc in enumerate(accuracy)])

        line = deepdriver.line(df, "step", "acc", title="line_chart")
        scatter = deepdriver.scatter(df, "step", "acc", title="scatter_chart")
        histogram = deepdriver.histogram(df, "step", "acc", title="histogram_chart")

        arti.add(line, "line_chart")
        arti.add(scatter, "scatter_chart")
        arti.add(histogram, "histogram_chart")

        deepdriver.upload_artifact(arti)

    def test_artifact_get_chart(self):
        arti = deepdriver.get_artifact(name="result5", type="result")

        line = arti.get("line_chart")
        scatter = arti.get("scatter_chart")
        histogram = arti.get("histogram_chart")

        deepdriver.visualize(line)
        deepdriver.visualize(scatter)
        deepdriver.visualize(histogram)

    def test_get_artifact_with_tag(self):

        arti = deepdriver.get_artifact(name=self._artifact_name, type=self._artifact_type)
        arti.add("cat_dog")
        logger.info(f"artfact info : {arti.__dict__}")
        deepdriver.upload_artifact(arti)

        # 태그를 지정하지 않을때 태그는 "V1"으로 됨
        arti = deepdriver.get_artifact(name=self._artifact_name, type=self._artifact_type)
        arti.download()

        # arti = deepdriver.get_artifact(name="TAG_V1", type=self._artifact_type, tag="V1")
        # arti.download()

    def test_get_upload_and_upload(self):
        arti = deepdriver.get_artifact(name="my_test4", type="dataset")
        arti.add("cat_dog")
        [(ent.path, ent.digest) for ent in arti.entry_list]
        logger.info(f"artfact info : {arti.__dict__}")
        deepdriver.upload_artifact(arti)

        arti2 = deepdriver.get_artifact(name="my_test4", type="dataset")
        arti2.add("cat_dog2")
        [(ent.path, ent.digest) for ent in arti2.entry_list]
        arti2.upload()

    def test_upload_code(self):
        arti = deepdriver.get_artifact(name="cnn", type="CODE")
        # deepdriver.upload_code(name="cnn", path="./src")
