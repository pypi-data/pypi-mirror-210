
from typing import  List

class ArtifactEntryInfo():
    def __init__(self,  path, digest, size, status, key, type, metadata):
        self.path = path
        self.digest = digest
        self.size = size
        self.status = status
        self.key = key
        self.type = type
        self.metadata =metadata
