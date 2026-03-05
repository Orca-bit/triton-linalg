from triton.backends.driver import DriverBase
import os

class TritonLinalgDriver(DriverBase):
    def __init__(self):
        super().__init__()
        self.utils = None
        self.binary_name = "triton_linalg"

    def is_active(self):
        return True

    def get_current_target(self):
        from triton.backends.compiler import GPUTarget
        return GPUTarget("triton_linalg", 0, 32)

    def get_current_device(self):
        return 0

    def get_current_stream(self, device):
        return 0
    
    def get_device_capability(self, device=None):
        return (0, 0)

    def get_benchmarker(self):
        return None
