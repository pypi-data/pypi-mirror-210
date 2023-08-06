# import deepdriver
# import shutil
# deepdriver.setting(http_host="127.0.0.1:9011", grpc_host="127.0.0.1:19051")
# deepdriver.login(key="ZjRlYWNmZjc0NGE1MTc5MGI5OGYxYTQ3YmFkM2U0MjcyNzg4ZmFhMzNhNzIxZTk0YzIwZDY2NThjNmNiZWE5Zg==")
# exp_name ="test_artifact_multiple9"
# _artifact_name ="arti9"
# _artifact_type ="dataset"
#
# run = deepdriver.init(exp_name=exp_name,
#                       config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
#
#
# arti = deepdriver.Artifacts(name=_artifact_name, type=_artifact_type)
# arti.add("cat_dog")
# print([ (ent.path, ent.digest ) for ent  in arti.entry_list])
# deepdriver.upload_artifact(arti)
#
# run.finish()
#
# run = deepdriver.init(exp_name=exp_name,
#                       config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})
#
#
# arti = deepdriver.get_artifact(name=_artifact_name, type=_artifact_type)
# arti.add("cat_dog2")
# print([ (ent.path, ent.digest ) for ent  in arti.entry_list])
# deepdriver.upload_artifact(arti)
#
# arti = deepdriver.get_artifact(name=_artifact_name, type=_artifact_type)
# print(f"artfact info : {arti.__dict__}")
# for idx, entry in enumerate(arti.entry_list):
#     print(f"artfact entry [{idx}]: {entry.path}")
# arti.download()
# print(arti.get_download_dir())
#
# run.finish()

import deepdriver
import shutil
deepdriver.setting(http_host="54.180.86.146:9011", grpc_host="54.180.86.146:19051")
deepdriver.login(key="ZjRlYWNmZjc0NGE1MTc5MGI5OGYxYTQ3YmFkM2U0MjcyNzg4ZmFhMzNhNzIxZTk0YzIwZDY2NThjNmNiZWE5Zg==")
_artifact_name ="arti9"
_artifact_type ="dataset"
_exp_name ="test_hpo_2"
run = deepdriver.creat_hpo(exp_name=_exp_name,
                      config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})







run = deepdriver.init(exp_name=_exp_name,
                      config={'epoch': 10, 'batch_size': 64, 'hidden_layer': 128})

arti = deepdriver.get_artifact(name=_artifact_name, type=_artifact_type)


arti = deepdriver.Artifacts(name=_artifact_name, type=_artifact_type)
arti.add("cat_dog2")
print([ (ent.path, ent.digest ) for ent  in arti.entry_list])
deepdriver.upload_artifact(arti)

arti = deepdriver.get_artifact(name=_artifact_name, type=_artifact_type)
print(f"artfact info : {arti.__dict__}")
for idx, entry in enumerate(arti.entry_list):
    print(f"artfact entry [{idx}]: {entry.path}")
arti.download()
print(arti.get_download_dir())

run.finish()