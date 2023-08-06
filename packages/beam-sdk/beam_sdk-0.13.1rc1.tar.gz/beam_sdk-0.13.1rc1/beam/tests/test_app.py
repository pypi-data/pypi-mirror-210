import beam
import json
import pytest

from beam.exceptions import BeamSerializationError
from beam.tests.utils import valid_reconstruction, generic_test_configs
from beam.types import Types


REQUIREMENTS_FILE_CONTENT = """

torch
numpy==1.19.5

scikit-learn

"""


class TestApp:
    def test_basic_app_reconstruction(self):
        for config in generic_test_configs:
            app = beam.App(**config)
            assert valid_reconstruction(app)

    def test_python_packages_from_requirements_file(self, tmp_path):
        for config in generic_test_configs:
            requirements_path = tmp_path / "requirements.txt"
            requirements_path.write_text(REQUIREMENTS_FILE_CONTENT)
            assert requirements_path.read_text() == REQUIREMENTS_FILE_CONTENT

            config["python_packages"] = str(requirements_path)

            app = beam.App(
                **config,
            )

            assert len(app.Spec.python_packages) == 3
            assert [
                "torch",
                "numpy==1.19.5",
                "scikit-learn",
            ] == app.Spec.python_packages

        assert valid_reconstruction(app)

    def test_valid_schedule_expressions(self):
        for config in generic_test_configs:
            app1 = beam.App(**config)

            app1.Trigger.Schedule(
                when="* * * * *",
                handler="method.py:run",
            )

            assert valid_reconstruction(app1)

            app1 = beam.App(**config)

            app1.Trigger.Schedule(
                when="every 5m",
                handler="method.py:run",
            )

            assert valid_reconstruction(app1)

            app2 = beam.App(**config)

            app2.Trigger.Schedule(
                when="every",
                handler="method.py:run",
            )

            with pytest.raises(BeamSerializationError):
                valid_reconstruction(app2)

    def test_multiple_triggers_should_fail_build(self):
        for config in generic_test_configs:
            app = beam.App(**config)

            app.Trigger.Schedule(
                when="* * * * *",
                handler="test.py:app",
            )

            with pytest.raises(ValueError):
                app.Trigger.TaskQueue(
                    inputs={
                        "some_input": beam.Types.String(),
                    },
                    handler="test.py:app",
                )

    def test_cpu_in_app_config(self):
        for config in generic_test_configs:
            config["cpu"] = 4
            app1 = beam.App(**config)

            config["cpu"] = "4000m"
            app2 = beam.App(**config)

            assert valid_reconstruction(app1)
            assert valid_reconstruction(app2)
            assert app1.dumps() == app2.dumps()

            config["cpu"] = 1
            app3 = beam.App(**config)

            config["cpu"] = "1000m"
            app4 = beam.App(**config)

            assert valid_reconstruction(app3)
            assert valid_reconstruction(app4)
            assert app3.dumps() == app4.dumps()

    def test_valid_rest_api(self):
        for config in generic_test_configs:
            app = beam.App(**config)

            schema = {
                "input1": beam.Types.String(),
                "input2": beam.Types.Float(),
                "input4": beam.Types.Boolean(),
                "input5": beam.Types.Json(),
            }

            app.Trigger.RestAPI(
                inputs=schema,
                outputs=schema,
                handler="method.py:run",
                loader="method.py:load",
                keep_warm_seconds=60,
                some_other_field="some_other_value",
            )

            assert valid_reconstruction(app)
            app_json = json.loads(app.dumps())
            assert app_json["triggers"][0]["inputs"] == Types.dump_schema(schema)
            assert app_json["triggers"][0]["outputs"] == Types.dump_schema(schema)
            assert app_json["triggers"][0]["handler"] == "method.py:run"
            assert app_json["triggers"][0]["loader"] == "method.py:load"
            assert app_json["triggers"][0]["keep_warm_seconds"] == 60
            assert "some_other_field" not in app_json["triggers"][0]

    def test_valid_webhook(self):
        for config in generic_test_configs:
            app_1 = beam.App(**config)
            app_2 = beam.App(**config)

            schema = {
                "input1": beam.Types.String(),
                "input2": beam.Types.Float(),
                "input4": beam.Types.Boolean(),
                "input5": beam.Types.Json(),
            }

            # Deprecate Webhook
            app_1.Trigger.Webhook(
                inputs=schema,
                outputs=schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            assert valid_reconstruction(app_1)
            app_json = json.loads(app_1.dumps())
            assert app_json["triggers"][0]["inputs"] == Types.dump_schema(schema)
            assert "outputs" not in app_json["triggers"][0]
            assert app_json["triggers"][0]["handler"] == "method.py:run"
            assert app_json["triggers"][0]["loader"] == "method.py:load"
            assert app_json["triggers"][0]["max_pending_tasks"] == 10
            assert "something_else" not in app_json["triggers"][0]

            # Use TaskQueue
            app_2.Trigger.TaskQueue(
                inputs=schema,
                outputs=schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            assert valid_reconstruction(app_2)
            app_json = json.loads(app_2.dumps())
            assert app_json["triggers"][0]["inputs"] == Types.dump_schema(schema)
            assert "outputs" not in app_json["triggers"][0]
            assert app_json["triggers"][0]["handler"] == "method.py:run"
            assert app_json["triggers"][0]["loader"] == "method.py:load"
            assert app_json["triggers"][0]["max_pending_tasks"] == 10
            assert "something_else" not in app_json["triggers"][0]

            assert app_1.dumps() == app_2.dumps()

    def test_valid_schedule(self):
        for config in generic_test_configs:
            app = beam.App(**config)

            app.Trigger.Schedule(
                when="* * * * *",
                handler="method.py:run",
                loader="method.py:load",
                something_else="some_other_value",
            )

            assert valid_reconstruction(app)
            app_json = json.loads(app.dumps())
            assert app_json["triggers"][0]["when"] == "* * * * *"
            assert app_json["triggers"][0]["handler"] == "method.py:run"
            assert "loader" not in app_json["triggers"][0]
            assert "something_else" not in app_json["triggers"][0]
