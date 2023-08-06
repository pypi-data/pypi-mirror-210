import logging
from unittest import TestCase
from setting import Setting
import PIL

import deepdriver
from deepdriver.sdk.data_types.boundingBoxes import BoundingBoxes

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)



class TestImage(TestCase):

    _login_key = "MTdiNzQxZTc0YTlkZDVhZThiNDZjNzdkNTJiMGQ0ZjExYzIxODYwZTNmNjc2M2MxMGViODNiNjcxNDAyN2JiYw=="
    _artifact_name = "horse2"
    _artifact_type = "dataset"
    _exp_name = "krazyhe8_project"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)
        run = deepdriver.init(exp_name=TestImage._exp_name,
                              config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

    def test_image_log_PIL(self):
        pil_data = PIL.Image.open("./cat_dog/cat/cat.png")
        image = deepdriver.Image(pil_data)
        deepdriver.log({"image_pil": image, "a": "b"})

    def test_image_array_log(self):
        pil_data1 = PIL.Image.open("./cat_dog/cat/cat.png")
        image1 = deepdriver.Image(pil_data1)

        pil_data2 = PIL.Image.open("./cat_dog/dog/dog.png")
        image2 = deepdriver.Image(pil_data2)


        deepdriver.log({"image_pil": [image1, image2], "a": "b"})

    def test_BoundingBoxes(self):
        json_info = {
            "predictions": {
                "box_data": [
                    {
                        "position": {
                            "minX": 0,
                            "maxX": 233,
                            "minY": 0,
                            "maxY": 213
                        },
                        "unit": "pixel",
                        "class_id": 3,
                        "caption": "a doga doga doga dog",
                        "scores": {
                            "acc": 0.5,
                            "loss": 0.7
                        }
                    },
                    {
                        "position": {
                            "minX": 256,
                            "maxX": 416,
                            "minY": 152,
                            "maxY": 273
                        },
                        "unit": "pixel",
                        "class_id": 2,
                        "caption": "a cat",
                        "scores": {
                            "acc": 0.5,
                            "loss": 0.7
                        }
                    }
                ],
                "class_labels": {
                    "0": "person",
                    "1": "car",
                    "2": "cat",
                    "3": "dog"
                }
            }
        }
        bb = BoundingBoxes(
            key=list(json_info.keys())[0],
            box_data=list(json_info.values())[0]['box_data'],
            class_labels=list(json_info.values())[0]['class_labels'])
        print(bb.to_json())

        img = deepdriver.Image("./cat_dog/cat/cat.png", boxes=bb)
        deepdriver.visualize(img)

        self.assertIsInstance(img.boxes, BoundingBoxes)
        img.to_json("test_key")

        # validtaion fail
        json_info['predictions']['box_data'][0]['caption'] = 3  # str to int
        with self.assertRaises(Exception):  # validation exception
            bb = BoundingBoxes(
                key=list(json_info.keys())[0],
                box_data=list(json_info.values())[0]['box_data'],
                class_labels=list(json_info.values())[0]['class_labels'])

    def test_image_with_boxes(self):
        class_labels = {
            0: "person",
            1: "car",
            2: "road",
            3: "building"
        }
        pil_data = PIL.Image.open("./cat_dog/cat/cat.png")
        class_labels = {
            0: "person",
            1: "car",
            2: "road",
            3: "building"
        }
        img = deepdriver.Image(pil_data, boxes={
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

        self.assertEqual(img.caption, "test_caption")
        self.assertIsInstance(img.boxes, BoundingBoxes)
        img.to_json("test_key")

        arti = deepdriver.Artifacts(name="result7_3", type="result")
        arti.add(img, "image_dog")
        deepdriver.upload_artifact(arti)

        img_from_server = arti.get("image_dog")
        # deepdriver.visualize(img_from_server)
        # deepdriver.log({"driving_scene": img})
