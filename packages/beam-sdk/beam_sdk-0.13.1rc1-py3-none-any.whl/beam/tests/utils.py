import json
import beam

from beam.types import PythonVersion

generic_test_configs = [
    {
        "name": "some_app",
        "cpu": "4000m",
        "memory": "128mi",
        "gpu": "A10G",
        "python_packages": ["pytorch"],
        "python_version": PythonVersion.Python37,
        "workspace": "./some_folder",
    },
    {
        "name": "some_app",
        "cpu": 1,
        "memory": "128mi",
        "gpu": "A10G",
    },
    {
        "name": "some_app",
        "cpu": 1,
        "memory": "1Gi",
    },
]


def valid_reconstruction(app: beam.App):
    dumped_app = app.dumps()
    dumped_json = json.dumps(dumped_app)
    app_from_dumped_config = beam.app.App.from_config(json.loads(dumped_json))
    return app_from_dumped_config.dumps() == dumped_app
