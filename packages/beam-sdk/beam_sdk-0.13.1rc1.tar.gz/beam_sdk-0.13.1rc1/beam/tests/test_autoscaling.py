import json
import beam

from beam.tests.utils import valid_reconstruction, generic_test_configs


class TestAutoScaling:
    # Should be removed once we fully remove autoscaling at root level of config json
    def test_old_autoscaling(self):
        for config in generic_test_configs:
            app = beam.App(
                **config,
            )

            app.Trigger.AutoScaling.MaxRequestLatency(
                desired_latency=10, max_replicas=100
            )

            assert valid_reconstruction(app)
            app_json = json.loads(app.dumps())
            assert app_json["autoscaling"]["max_replicas"] == 100
            assert (
                app_json["autoscaling"]["autoscaling_type"]
                == beam.types.AutoscalingType.MaxRequestLatency
            )
            assert app_json["autoscaling"]["desired_latency"] == 10

    # Should be removed once we fully remove autoscaling at root level of config json
    def test_old_autoscaling_matches_current_autoscaling(self):
        for config in generic_test_configs:
            app1 = beam.App(
                **config,
            )

            schema = {
                "input1": beam.Types.String(),
                "input2": beam.Types.Float(),
                "input4": beam.Types.Boolean(),
                "input5": beam.Types.Json(),
            }

            # Deprecate Webhook
            app1.Trigger.TaskQueue(
                inputs=schema,
                outputs=schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )
            app1.Trigger.AutoScaling.MaxRequestLatency(
                desired_latency=10, max_replicas=100
            )

            assert valid_reconstruction(app1)
            app_json_1 = json.loads(app1.dumps())
            assert app_json_1["autoscaling"]["max_replicas"] == 100
            assert (
                app_json_1["autoscaling"]["autoscaling_type"]
                == beam.types.AutoscalingType.MaxRequestLatency
            )
            assert app_json_1["autoscaling"]["desired_latency"] == 10

            app2 = beam.App(
                **config,
            )

            tq = app2.Trigger.TaskQueue(
                inputs=schema,
                outputs=schema,
                handler="method.py:run",
                loader="method.py:load",
                max_pending_tasks=10,
                something_else="some_other_value",
            )

            tq.AutoScaling.MaxRequestLatency(desired_latency=10, max_replicas=100)

            assert valid_reconstruction(app2)
            app_json_2 = json.loads(app2.dumps())
            assert app_json_2 == app_json_1
