from typing import Literal, Optional
from deepdriver.sdk.lib.lazyloader import LazyLoader
torch = LazyLoader('deepdriver.lazy.torch', globals(), 'torch')

from deepdriver.intergration.torch.torch import get_torch_log

_global_watch_idx = 0


def watch(models, log: Optional[Literal["gradients", "parameters", "all"]] = "gradients", log_freq: int = 1000,
          log_graph: bool = False):
    if log != "gradients" and log != "parameters" and log != "all":
        raise ValueError("log must be one of 'gradients', 'parameters', 'all'")

    if not isinstance(models, (tuple, list)):
        models = (models,)

    global _global_watch_idx
    idx = _global_watch_idx

    prefix = ""
    for local_idx, model in enumerate(models):
        global_idx = idx + local_idx
        _global_watch_idx += 1

        if global_idx > 0:
            prefix = "graph_%i" % global_idx

        if not isinstance(model, torch.nn.Module):
            raise ValueError(
                "Expected a pytorch model (torch.nn.Module). Received "
                + str(type(model))
            )

        if log == "gradients" or log == "all":
            get_torch_log().add_log_gradients_hook(model, name="", prefix=prefix, log_freq=log_freq)

        if log == "parameters" or log == "all":
            get_torch_log().add_log_parameters_hook(model, name="", prefix=prefix, log_freq=log_freq)

