import hashlib
import json
import os
import random
import string
from pathlib import Path
from typing import Union, Dict, Tuple

from PIL import Image as PIL_IMAGE
from assertpy import assert_that

from deepdriver import logger
from deepdriver.sdk.data_types.artifactInfo import ArtifactInfo
from deepdriver.sdk.data_types.boundingBoxes import BoundingBoxes
from deepdriver.sdk.data_types.media import LOG_TYPE_IMAGE, Media
from deepdriver.sdk.data_types.run import Run
from deepdriver.sdk.interface import interface


class Image(Media):

    def __init__(self, data: Union[str, PIL_IMAGE.Image], caption: str = None,
                 boxes: Union[Dict[str, BoundingBoxes], Dict[str, dict]] = None) -> None:
        super().__init__(log_type=LOG_TYPE_IMAGE)

        assert_that(data).is_not_none()
        if isinstance(data, str):
            # str인 경우 local_path로 지정하고 data 에는 해당 경로 파일을 로드한 PIL.Image 객체를 지정함
            self.local_path = data
            self.data = PIL_IMAGE.open(self.local_path)
            self.height = self.data.size[1]
            self.width = self.data.size[0]
            self.format = self.data.format
        elif isinstance(data, PIL_IMAGE.Image):
            self.data = data
            # data가 PIL.Image 객체인 경우 7자리의 random id값을 생성한후 {random_id}.{file_format}으로 저장
            random_id = "".join(random.choice(string.digits) for _ in range(7))
            self.local_path = f"{random_id}.{data.format}"
            logger.debug(f"PIL Image save to local:local_path:{self.local_path}")
            data.save(self.local_path)
            self.height = self.data.size[1]
            self.width = self.data.size[0]
            self.format = self.data.format
        else:
            raise Exception(f"unknown data type {type(data)}")

        # caption, boxes 처리
        self.caption: str = caption
        self.boxes: BoundingBoxes = None

        if boxes:
            if isinstance(boxes, BoundingBoxes):
                self.boxes = boxes
            elif isinstance(boxes, dict):
                bb = BoundingBoxes(
                    key=list(boxes.keys())[0],
                    box_data=list(boxes.values())[0]['box_data'],
                    class_labels=list(boxes.values())[0]['class_labels'])
                self.boxes = bb

    def to_json(self, key_name: str, is_list: bool = False, index: int = 0, log_step: int = None) -> str:
        assert_that(key_name).is_not_none()

        return json.dumps(self.to_dict(key_name, is_list, index, log_step))

    def meta_json(self, key_name: str, is_list=False, index=0) -> str:
        return json.dumps({
            "log_type": self.log_type,
            "path": self.get_path_json(key_name, is_list, index),
        })

    def to_dict(self, key_name: str, is_list=False, index=0, log_step: int = None) -> Dict:
        return {
            "log_type": self.log_type,
            "hash": self.get_digest(),
            "size": self.get_size(),
            "path": self.get_path(key_name, is_list, index, log_step),
            "height": self.height,
            "width": self.width,
            "format": self.format,
            "caption": self.caption if self.caption else "",
            "boxes": self.boxes.to_dict() if self.boxes else "",
        }

    def get_size(self) -> int:
        return os.stat(self.local_path).st_size

    def get_digest(self) -> str:
        with open(self.local_path, "rb") as f:
            digest = hashlib.md5(f.read()).hexdigest()
        return digest

    # json으로 구성된 메타데이터 전송
    def upload_file(self, run: Run, key_name: str, is_list: bool = False, index: int = 0, log_step: int = None) -> None:
        # 저장한 파일을 Interface.py의 upoad_file을 호출하여 전송
        digest = self.get_digest()
        root_path = self.get_root_path(run.run_id)
        path = self.get_path(key_name, is_list, index, log_step)
        logger.debug(f"file upload[image] : local_path=[{self.local_path}], root_path=[{root_path}], path=[{path}]")
        arti_info = ArtifactInfo(artifact_id=0, last_file_yn="Y", artifact_name="", artifact_type="",
                                 artifact_digest="", entry_list=[])
        interface.upload_file(upload_type="RUN", local_path=self.local_path, root_path=root_path, path=path,
                              run_id=run.run_id, teamName=run.team_name,
                              expName=run.exp_name,
                              run_name=run.run_name,
                              entry_digest=digest,
                              arti_info=arti_info,
                              file_index=0)

    def get_path(self, key_name: str, is_list: bool = False, index: int = 0,
                 log_step: int = None) -> str:

        if is_list:
            # format : {key}.IMAGE.{step}.{Index}.JPEG
            return f"{key_name}.IMAGE.{str(log_step) + '.' if log_step or log_step == 0 else ''}{index}.{self.format}"
        else:
            # format : {key}.IMAGE.{step}.JPEG
            return f"{key_name}.IMAGE.{str(log_step) + '.' if log_step or log_step == 0 else ''}{self.format}"

    def get_path_json(self, key_name: str, is_list=False, index=0) -> str:
        if is_list:
            return f"{key_name}.IMAGE.{index}.json"
        else:
            # server 패스
            return f"{key_name}.IMAGE.json"

    def get_root_path(self, run_id: int) -> str:
        return os.path.join(str(run_id), "media")

    def file_dump(self, path: str, key_name: str, is_list=False, index=0) -> Tuple[str, str]:
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.to_dict(key_name, is_list, index), f)

        with open(path, "rb") as f:
            digest = hashlib.md5(f.read()).hexdigest()
            f.seek(0, os.SEEK_END)
            size = f.tell()
        return digest, size
