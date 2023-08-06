from typing import List, Optional
from warnings import warn

from beam.base import ResourceSet
from beam.serializer import VolumeConfiguration
from beam.types import MountType


class MountResourceSet(ResourceSet):
    def PersistentVolume(
        self, name: str, path: str = "", app_path: Optional[str] = None, **_
    ):
        if app_path is not None:
            warn(
                "'app_path' is deprecated and will be removed in the future. "
                "Please use 'path' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        self.resources.append(
            VolumeConfiguration(
                name=name,
                local_path=None,
                app_path=path or app_path,
                mount_type=MountType.Persistent,
            )
        )

    def SharedVolume(
        self, name: str, path: str = "", app_path: Optional[str] = None, **_
    ):
        if app_path is not None:
            warn(
                "'app_path' is deprecated and will be removed in the future. "
                "Please use 'path' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        self.resources.append(
            VolumeConfiguration(
                name=name,
                local_path=None,
                app_path=path or app_path,
                mount_type=MountType.Shared,
            )
        )

    def from_config(self, mounts: List[dict]):
        if mounts is None:
            return

        for m in mounts:
            if m.get("mount_type") == MountType.Persistent:
                self.PersistentVolume(**m)

            elif m.get("mount_type") == MountType.Shared:
                self.SharedVolume(**m)
