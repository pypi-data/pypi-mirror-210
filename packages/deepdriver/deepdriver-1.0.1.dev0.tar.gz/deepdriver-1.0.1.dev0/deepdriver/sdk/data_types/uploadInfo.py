class UploadInfo():
    def __init__(self, upload_type: str, local_path: str, root_path: str, path: str, run_id: int,teamName: str, expName: str, run_name: str, entry_digest: str, file_index: int):
        self.upload_type =upload_type
        self.local_path =local_path
        self.root_path = root_path
        self.path = path
        self.run_id = run_id
        self.teamName = teamName
        self.expName = expName
        self.run_name = run_name
        self.entry_digest =entry_digest
        self.file_index =file_index


