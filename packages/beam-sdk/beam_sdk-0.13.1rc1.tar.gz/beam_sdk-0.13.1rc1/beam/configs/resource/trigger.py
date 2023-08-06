from typing import Dict, Optional

from beam.base import Resource
from beam.serializer import RestAPITrigger, TaskQueueTrigger, CronJobTrigger
from beam.types import Types
from beam.configs.resource.autoscaling import AutoscalingResource
from beam.configs.resourceset.output import OutputResourceSet


class TriggerResourceMixin(Resource):
    @classmethod
    def from_config(cls, trigger: dict):
        inputs = {}
        outputs = {}

        if trigger.get("inputs") is not None:
            inputs = Types.load_schema(trigger.get("inputs"))

        if "inputs" in trigger:
            del trigger["inputs"]

        if trigger.get("outputs") is not None:
            outputs = Types.load_schema(trigger.get("outputs"))

        if "outputs" in trigger:
            del trigger["outputs"]

        return cls(**trigger, inputs=inputs, outputs=outputs)


class RestAPIResource(TriggerResourceMixin):
    def __init__(
        self,
        inputs: Dict[str, Types],
        handler: str,
        outputs: Optional[Dict[str, Types]] = None,
        loader: Optional[str] = None,
        keep_warm_seconds: Optional[int] = None,
        **_
    ):
        self.config = RestAPITrigger(
            inputs=inputs,
            outputs=outputs,
            handler=handler,
            loader=loader,
            keep_warm_seconds=keep_warm_seconds,
        )


class TaskQueueResource(TriggerResourceMixin):
    def __init__(
        self,
        inputs: Dict[str, Types],
        handler: str,
        loader: Optional[str] = None,
        max_pending_tasks: Optional[int] = 1000,
        callback_url: Optional[str] = None,
        **_
    ):
        self.config = TaskQueueTrigger(
            inputs=inputs,
            handler=handler,
            loader=loader,
            max_pending_tasks=max_pending_tasks,
            callback_url=callback_url,
        )

        self.AutoScaling = AutoscalingResource()
        self.Output = OutputResourceSet()


class ScheduledJobResource(TriggerResourceMixin):
    def __init__(self, when: str, handler: str, **_):
        self.config = CronJobTrigger(when=when, handler=handler)
        self.Output = OutputResourceSet()
