import json
import beam

from beam.tests.utils import valid_reconstruction, generic_test_configs


test_schema = {
    "input1": beam.Types.String(),
    "input2": beam.Types.Float(),
    "input4": beam.Types.Boolean(),
    "input5": beam.Types.Json(),
}


class TestOutputs:
    def _verify_output(self, app, name, path, output_type):
        assert valid_reconstruction(app)

        app_json = json.loads(app.dumps())
        assert app_json.get("outputs") is not None
        assert app_json.get("outputs")[0].get("path") == path
        assert app_json.get("outputs")[0].get("name") == name
        assert app_json.get("outputs")[0].get("output_type") == output_type

        return app_json

    def test_add_files_webhook(self):
        for config in generic_test_configs:
            # Old way of adding outputs
            app1 = beam.App(
                **config,
            )

            app1.Trigger.TaskQueue(
                inputs=test_schema,
                outputs=test_schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            app1.Output.File(
                path="/some/path",
                name="some_name",
            )

            assert valid_reconstruction(app1)

            app_json_1 = self._verify_output(
                app1, "some_name", "/some/path", beam.types.OutputType.File
            )

            # New way of adding outputs
            app2 = beam.App(
                **config,
            )

            trigger = app2.Trigger.TaskQueue(
                inputs=test_schema,
                outputs=test_schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            trigger.Output.File(
                path="/some/path",
                name="some_name",
            )

            app_json_2 = self._verify_output(
                app2, "some_name", "/some/path", beam.types.OutputType.File
            )

            assert app_json_1 == app_json_2

    def test_add_directory_webhook(self):
        for config in generic_test_configs:
            app1 = beam.App(
                **config,
            )

            app1.Trigger.TaskQueue(
                inputs=test_schema,
                outputs=test_schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            app1.Output.Dir(
                path="/some/path",
                name="some_name",
            )

            app_json_1 = self._verify_output(
                app1, "some_name", "/some/path", beam.types.OutputType.Directory
            )

            # New way of adding outputs
            app2 = beam.App(
                **config,
            )

            trigger = app2.Trigger.TaskQueue(
                inputs=test_schema,
                outputs=test_schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            trigger.Output.Dir(
                path="/some/path",
                name="some_name",
            )

            app_json_2 = self._verify_output(
                app2, "some_name", "/some/path", beam.types.OutputType.Directory
            )

            assert app_json_1 == app_json_2

    def test_add_file_scheduled_job(self):
        for config in generic_test_configs:
            app1 = beam.App(
                **config,
            )

            app1.Trigger.Schedule(
                when="every 5m",
                handler="method.py:run",
            )

            app1.Output.File(
                path="/some/path",
                name="some_name",
            )

            app_json_1 = self._verify_output(
                app1, "some_name", "/some/path", beam.types.OutputType.File
            )

            # New way of adding outputs
            app2 = beam.App(
                **config,
            )

            trigger = app2.Trigger.Schedule(
                when="every 5m",
                handler="method.py:run",
            )

            trigger.Output.File(
                path="/some/path",
                name="some_name",
            )

            app_json_2 = self._verify_output(
                app2, "some_name", "/some/path", beam.types.OutputType.File
            )

            assert app_json_1 == app_json_2

    def test_add_directory_scheduled_job(self):
        for config in generic_test_configs:
            app1 = beam.App(
                **config,
            )

            app1.Trigger.Schedule(
                when="every 5m",
                handler="method.py:run",
            )

            app1.Output.Dir(
                path="/some/path",
                name="some_name",
            )

            app_json_1 = self._verify_output(
                app1, "some_name", "/some/path", beam.types.OutputType.Directory
            )

            # New way of adding outputs
            app2 = beam.App(
                **config,
            )

            trigger = app2.Trigger.Schedule(
                when="every 5m",
                handler="method.py:run",
            )

            trigger.Output.Dir(
                path="/some/path",
                name="some_name",
            )

            app_json_2 = self._verify_output(
                app2, "some_name", "/some/path", beam.types.OutputType.Directory
            )

            assert app_json_1 == app_json_2
