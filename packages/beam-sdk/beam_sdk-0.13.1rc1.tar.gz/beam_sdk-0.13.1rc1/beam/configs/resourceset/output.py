from typing import List

from beam.base import ResourceSet
from beam.serializer import FileConfiguration
from beam.types import OutputType


class OutputResourceSet(ResourceSet):
    def File(self, path: str, name: str, **_):
        self.resources.append(
            FileConfiguration(path=path, name=name, output_type=OutputType.File)
        )

    def Dir(self, path: str, name: str, **_):
        self.resources.append(
            FileConfiguration(path=path, name=name, output_type=OutputType.Directory)
        )

    def from_config(self, outputs: List[dict]):
        if outputs is None:
            return

        for f in outputs:
            if f.get("output_type") == OutputType.Directory:
                self.Dir(**f)
            else:
                self.File(**f)
