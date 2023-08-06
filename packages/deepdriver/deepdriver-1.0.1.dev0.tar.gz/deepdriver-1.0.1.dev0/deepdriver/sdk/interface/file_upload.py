import base64
import json
import os
import sys
from typing import IO, TYPE_CHECKING, Optional
import requests
import math
import logging
import contextlib

from deepdriver.sdk.data_types.artifactInfo import ArtifactInfo
from deepdriver.sdk.data_types.uploadInfo import UploadInfo

try:
    from http.client import HTTPConnection # py3
except ImportError:
    from httplib import HTTPConnection # py2

class Progress:
    """A helper class for displaying progress."""



    def __init__(
        self, file: IO[bytes], iter_bytes: int ,upload_info: UploadInfo, arti_info: ArtifactInfo, callback: Optional["ProgressFn"] = None
    ) -> None:
        self.file = file
        self.file_name =file.name
        self.upload_info = upload_info
        self.arti_info = arti_info
        if callback is None:

            def callback_(new_bytes: int, total_bytes: int) -> None:
                pass

            callback = callback_

        self.callback: "ProgressFn" = callback
        self.bytes_read = 0
        self.chunk_num =0
        self.len = os.fstat(file.fileno()).st_size
        self.iter_bytes = iter_bytes
        self.total_chunk = math.ceil(self.len / self.iter_bytes)
        artifactEntries =[{"path":entry.path,"digest" : entry.digest, "size": entry.size, "status":entry.status, "key":entry.key ,"type":entry.type,"metadata" :entry.metadata} for entry in self.arti_info.entry_list]
        self.artifact ={
            "artifactType" : self.arti_info.artifact_type,
            "artifactName" : self.arti_info.artifact_name,
            "artifactId": self.arti_info.artifact_id,
            "firstFileYN": "Y" if self.upload_info.file_index==0 else "N",
            "lastFileYN": 'Y' if self.arti_info.last_file_yn =="Y" else "N",
            "digest" : self.arti_info.artifact_digest,
            "artifactEntryEntries": artifactEntries
        }
        self.upload_data ={
            "teamName": self.upload_info.teamName,
            "expName": self.upload_info.expName,
            "runName": self.upload_info.run_name,
            "runId": self.upload_info.run_id,
            "uploadType": self.upload_info.upload_type,
            "fileName": self.upload_info.path,
            "chunk": "",
            "chunkNum": 0,
            "chunkSize": 0,
            "totalSize": self.len,
            "totalChunk": self.total_chunk,
            "digest": self.upload_info.entry_digest,
            "artifact": self.artifact
        }

    def read(self, size=-1):
        """Read bytes and call the callback."""
        bites = self.file.read(size)
        self.bytes_read += len(bites)
        if not bites and self.bytes_read < self.len:
            # Files shrinking during uploads causes request timeouts. Maybe
            # we could avoid those by updating the self.len in real-time, but
            # files getting truncated while uploading seems like something
            # that shouldn't really be happening anyway.
            print(
                "File {} size shrank from {} to {} while it was being uploaded.".format(
                    self.file.name, self.len, self.bytes_read
                )
            )
        # Growing files are also likely to be bad, but our code didn't break
        # on those in the past so it's riskier to make that an error now.
        #upload_callback(uploaded_size,total_size,local_path,entry_list,chunk_bytes, file_index)
        self.callback(self.bytes_read, self.len, self.file_name, self.arti_info.entry_list,bites,self.upload_info.file_index)
        base64_str =str( base64.b64encode(bites), encoding='utf-8')
        self.upload_data["chunk"] = base64_str
        self.upload_data["chunkNum"] = self.chunk_num
        self.upload_data["chunkSize"] = len(bites)


        self.chunk_num = self.chunk_num + 1
        if len(bites)>0:
            return self.upload_data
        return ""

    def rewind(self) -> None:
        self.callback(-self.bytes_read, 0)
        self.bytes_read = 0
        self.file.seek(0)

    def __getattr__(self, name):
        """Fallback to the file object for attrs not defined here."""
        if hasattr(self.file, name):
            return getattr(self.file, name)
        else:
            raise AttributeError

    def __iter__(self):
        return self

    def __next__(self):
        bites = self.read(self.iter_bytes)
        if len(bites) == 0:
            raise StopIteration
        return bites

    def __len__(self):
        return self.len

    next = __next__