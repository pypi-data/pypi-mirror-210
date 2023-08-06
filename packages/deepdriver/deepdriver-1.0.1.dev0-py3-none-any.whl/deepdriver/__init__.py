import logging
import sys
from deepdriver.sdk import util
import os

# Google introduced an incompatibility into protobuf-4.21.x
# that is not backwards compatible with many libraries.
# Once those libraries have updated to rebuild their _pb2.py files,
# this can be removed.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# os.environ["GRPC_VERBOSITY"] = "debug"
# os.environ["GRPC_TRACE"] = "all"
# os.environ["TSI_OPENSSL_ALPN_SUPPORT"] = "1"
# print(os.environ)
try:
  from google.protobuf.internal import builder as _builder
except ImportError:
  pass
#   # tensorflow와 protobuf 버젼 호환 문제로 protovuf 4.2.x 버젼을 사용하게 함
#   raise ImportError("A higher protobuf package version is requried. Upgrade protobuf using 'pip install --upgrade protobuf==4.21.12'" )

logger = logging.getLogger("deepdriver")
logger.propagate = False
if logger.handlers == []:
  console_handler = logging.StreamHandler(sys.stdout)
  if not util.is_notebook():
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s')
    console_handler.setFormatter(formatter)
  else:
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
  logger.setLevel(logging.INFO)
  logger.addHandler(console_handler)


from deepdriver.sdk.artifact import *
from deepdriver.sdk.config import *
from deepdriver.sdk.experiment import *
from deepdriver.sdk.login import *
from deepdriver.sdk.setting import *
from deepdriver.sdk.run import *
from deepdriver.sdk.watch import watch

from deepdriver.sdk.visualization import visualize
from deepdriver.sdk.chart.histogram import histogram
from deepdriver.sdk.chart.line import line
from deepdriver.sdk.chart.bar import bar
from deepdriver.sdk.chart.scatter import scatter
from deepdriver.sdk.chart.confusion_matrix import confusion_matrix
from deepdriver.sdk.chart.roc_curve import roc_curve
from deepdriver.sdk.data_types.dataFrame import DataFrame
from deepdriver.sdk.data_types.image import Image
from deepdriver.sdk.data_types.table import Table
from deepdriver.sdk.model import *

#layzyload
from deepdriver.sdk.lib.lazyloader import LazyLoader
keras = LazyLoader('deepdriver.intergration.keras', globals(), 'deepdriver.intergration.keras.keras')
torch = LazyLoader('deepdriver.intergration.torch', globals(), 'deepdriver.intergration.torch.torch')



config = Config()

