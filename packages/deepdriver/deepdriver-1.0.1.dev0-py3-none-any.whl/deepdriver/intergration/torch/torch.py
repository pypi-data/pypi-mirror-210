import deepdriver
from deepdriver.sdk.lib.lazyloader import LazyLoader
torch = LazyLoader('deepdriver.lazy.torch', globals(), 'torch')

from deepdriver import logger

LOG_TRACK_COUNT, LOG_TRACK_THRESHOLD = range(2)


# 함수
def log_track_init(log_freq: int):
    """create tracking structure used by log_track_update"""
    l = [0] * 2
    l[LOG_TRACK_THRESHOLD] = log_freq
    return l


def log_track_update(log_track: int) -> bool:
    """count (log_track[0]) up to threshold (log_track[1]), reset count (log_track[0]) and return true when reached"""
    log_track[LOG_TRACK_COUNT] += 1
    if log_track[LOG_TRACK_COUNT] < log_track[LOG_TRACK_THRESHOLD]:
        return False
    log_track[LOG_TRACK_COUNT] = 0
    return True


#
class TorchLog:
    def add_log_gradients_hook(self, module, name, prefix, log_freq: int = 0):
        prefix = prefix + name

        if not hasattr(module, "_deepdriver_hook_names"):
            module._deepdriver_hook_names = []

        for name, parameter in module.named_parameters():
            print(parameter.requires_grad)
            if parameter.requires_grad:
                log_track_grad = log_track_init(log_freq)
                module._deepdriver_hook_names.append("gradients/" + prefix + name)
                self._hook_variable_gradient_stats(
                    parameter, "gradients/" + prefix + name, log_track_grad
                )

    def add_log_parameters_hook(
            self,
            module: "torch.nn.Module",
            name: str = "",
            prefix: str = "",
            log_freq: int = 0,
    ) -> None:
        """This instruments hooks into the pytorch module
        log parameters after a forward pass
        log_freq - log gradients/parameters every N batches
        """
        # if name is not None:
        prefix = prefix + name

        if not hasattr(module, "_deepdriver_hook_names"):
            module._deepdriver_hook_names = []

        def parameter_log_hook(module, input_, output, log_track):
            if not log_track_update(log_track):
                return
            for name, parameter in module.named_parameters():
                # for pytorch 0.3 Variables
                if isinstance(parameter, torch.autograd.Variable):
                    data = parameter.data
                else:
                    data = parameter
                self.log_tensor_stats(data.cpu(), "parameters/" + prefix + name)

        log_track_params = log_track_init(log_freq)
        try:
            hook = module.register_forward_hook(
                lambda mod, inp, outp: parameter_log_hook(
                    mod, inp, outp, log_track_params
                )
            )
            # self._hook_handles["parameters/" + prefix] = hook
            module._deepdriver_hook_names.append("parameters/" + prefix)
        except RuntimeError as e:
            print(
                f"Trying to register forward_hook failed ({e}) - skipping parameter tracking."
            )

    def _hook_variable_gradient_stats(self, var, name, log_track):
        """Logs a Variable's gradient's distribution statistics next time backward()
        is called on it.
        """

        def _callback(grad, log_track):
            if not log_track_update(log_track):
                return
            self.log_tensor_stats(grad.data, name)

        handle = var.register_hook(lambda grad: _callback(grad, log_track))
        # self._hook_handles[name] = handle
        return handle

    def log_tensor_stats(self, tensor, name):

        """Add distribution statistics on a tensor's elements to the current History entry"""
        # TODO Handle the case of duplicate names.

        if isinstance(tensor, tuple) or isinstance(tensor, list):
            while (isinstance(tensor, tuple) or isinstance(tensor, list)) and (
                    isinstance(tensor[0], tuple) or isinstance(tensor[0], list)
            ):
                tensor = [item for sublist in tensor for item in sublist]
            tensor = torch.cat([t.reshape(-1) for t in tensor])

        # checking for inheritance from _TensorBase didn't work for some reason
        if not hasattr(tensor, "shape"):
            cls = type(tensor)
            raise TypeError(f"Expected Tensor, not {cls.__module__}.{cls.__name__}")

        # HalfTensors on cpu do not support view(), upconvert to 32bit
        if isinstance(tensor, torch.HalfTensor):
            tensor = tensor.clone().type(torch.FloatTensor).detach()

        # Sparse tensors have a bunch of implicit zeros. In order to histo them correctly,
        # we have to count them up and add them to the histo ourselves.
        sparse_zeros = None
        if tensor.is_sparse:
            # Have to call this on a sparse tensor before most other ops.
            tensor = tensor.cpu().coalesce().clone().detach()

            backing_values = tensor._values()
            non_zero_values = backing_values.numel()
            all_values = tensor.numel()
            sparse_zeros = all_values - non_zero_values
            tensor = backing_values

        flat = tensor.reshape(-1)

        # For pytorch 0.3 we use unoptimized numpy histograms (detach is new in 0.4)
        if not hasattr(flat, "detach"):
            tensor = flat.cpu().clone().numpy()
            print("detach")
            deepdriver.log({name: deepdriver.histogram(seq=tensor)})
            return
        histogram = deepdriver.histogram(seq=tensor)
        # deepdriver.visualize(histogram)  # 코드 반영시엔 주석 처리할것!
        deepdriver.log({name: histogram})


torch_log: TorchLog = None


def set_torch_log(torch_log_: TorchLog) -> None:
    global torch_log
    torch_log = torch_log_


def get_torch_log() -> TorchLog:
    global torch_log
    if not torch_log:
        logger.info("TorchLog is Initialized")
        torch_log = TorchLog()
    return torch_log
