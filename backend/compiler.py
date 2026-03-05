import os
import re
import subprocess
from triton.backends.compiler import BaseBackend, GPUTarget

class TritonLinalgBackend(BaseBackend):
    def __init__(self, target: tuple) -> None:
        super().__init__(target)

    @staticmethod
    def supports_target(target: GPUTarget):
        return target.backend == "triton_linalg"

    def parse_options(self, options: dict) -> object:
        return object()

    def pack_metadata(self, metadata):
        return metadata

    def get_codegen_implementation(self):
        return None

    def load_dialects(self, context):
        return

    def add_stages(self, stages, options):
        return

    def hash(self):
        return "triton_linalg"
