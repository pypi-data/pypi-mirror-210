import bentoml
import importlib
import sys
import subprocess
def save_model(framework, model_name,  model):
    #(sys.modules[__package__])
    #print(globals())
    module = __import__("bentoml.sklearn")

    import importlib
    module =importlib.import_module("bentoml."+framework)
    save_model = getattr(module, 'save_model')
    print(save_model)
    save_model(model_name,model)

def serving_model(file):
    result = subprocess.check_output('bentoml serve service.py:svc --reload', shell=True)
    return result