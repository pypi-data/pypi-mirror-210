import json
import beam
import pytest

from beam.tests.utils import valid_reconstruction, generic_test_configs
from beam.exceptions import BeamSerializationError


class TestMounts:
    def test_persistent_volume(self):
        for config in generic_test_configs:
            app = beam.App(
                **config,
            )

            app.Mount.PersistentVolume(
                path="/some/path",
                name="some_name",
            )

            assert valid_reconstruction(app)

            app_json = json.loads(app.dumps())
            assert app_json.get("mounts") is not None
            assert app_json.get("mounts")[0].get("app_path") == "/some/path"
            assert app_json.get("mounts")[0].get("name") == "some_name"
            assert (
                app_json.get("mounts")[0].get("mount_type")
                == beam.types.MountType.Persistent
            )

    def test_persistent_volume_missing_values(self):
        for config in generic_test_configs:
            app = beam.App(
                **config,
            )

            app.Mount.PersistentVolume(
                name="some_name",
            )

            with pytest.raises(BeamSerializationError):
                app.dumps()

            app = beam.App(
                **config,
            )

            with pytest.raises(TypeError):
                app.Mount.PersistentVolume(
                    path="/some/path",
                )

    def test_shared_volume_missing_values(self):
        for config in generic_test_configs:
            app = beam.App(
                **config,
            )

            app.Mount.SharedVolume(
                name="some_name",
            )

            with pytest.raises(BeamSerializationError):
                app.dumps()

            app = beam.App(
                **config,
            )

            with pytest.raises(TypeError):
                app.Mount.SharedVolume(
                    path="/some/path",
                )

    def test_shared_volume(self):
        for config in generic_test_configs:
            app = beam.App(
                **config,
            )

            app.Mount.SharedVolume(
                path="/some/path",
                name="some_name",
            )

            assert valid_reconstruction(app)

            app_json = json.loads(app.dumps())
            assert app_json.get("mounts") is not None
            assert app_json.get("mounts")[0].get("app_path") == "/some/path"
            assert app_json.get("mounts")[0].get("name") == "some_name"
            assert (
                app_json.get("mounts")[0].get("mount_type")
                == beam.types.MountType.Shared
            )
