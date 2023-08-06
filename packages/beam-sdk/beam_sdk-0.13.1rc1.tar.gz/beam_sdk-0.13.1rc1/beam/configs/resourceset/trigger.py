from typing import Dict, Optional, Union
from warnings import warn

from beam.base import ResourceSet
from beam.configs.resource import (
    TaskQueueResource,
    RestAPIResource,
    ScheduledJobResource,
    AutoscalingResource,
)
from beam.types import Types


class TriggerType:
    Webhook = "webhook"
    RestAPI = "rest_api"
    CronJob = "cron_job"


class TriggerResourceSet(ResourceSet):
    def __init__(self) -> None:
        super().__init__()

        # @Deprecate AutoScaling in TriggerResourceSet
        # Opt into using Autoscaling through TaskQueueResource instead
        self.AutoScaling = AutoscalingResource()

    def _validate_trigger_groupings(self):
        """
        NOTE: For the time being, the Beam APP can only accept one trigger during the alpha
        stages. Later we will allow multiple trigger types for webhooks (Slack, Twitter, etc)
        """
        if len(self.resources) > 1:
            raise ValueError("App can only have 1 trigger at a time")

    def Webhook(
        self,
        inputs: Dict[str, Types],
        handler: str,
        loader: Optional[str] = None,
        max_pending_tasks: Optional[int] = 1000,
        callback_url: Optional[str] = None,
        **_,
    ):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            loader: specify the method that will load the data into the handler (optional)
            inputs: dictionary specifying how to serialize/deserialize input arguments
            max_pending_tasks (optional): maximum number of pending tasks in the queue, if exceeded, the webhook will prevent further items from being enqueued

        """
        warn(
            "The 'Webhook' trigger is deprecated and is replaced by 'TaskQueue'. Please use 'TaskQueue' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.TaskQueue(
            inputs=inputs,
            handler=handler,
            loader=loader,
            max_pending_tasks=max_pending_tasks,
            callback_url=callback_url,
        )

    def TaskQueue(
        self,
        inputs: Dict[str, Types],
        handler: str,
        loader: Optional[str] = None,
        max_pending_tasks: Optional[int] = 1000,
        callback_url: Optional[str] = None,
        **_,
    ):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            inputs: dictionary specifying how to serialize/deserialize input arguments
            max_pending_tasks (optional): maximum number of pending tasks in the queue, if exceeded, the webhook will prevent further items from being enqueued

        """
        resource = TaskQueueResource(
            inputs=inputs,
            handler=handler,
            loader=loader,
            max_pending_tasks=max_pending_tasks,
            callback_url=callback_url,
        )

        self.resources.append(resource)
        self._validate_trigger_groupings()

        return resource

    def Schedule(self, when: str, handler: str, **_):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            when: CRON string to indicate the schedule in which the job is to run
                - https://en.wikipedia.org/wiki/Cron \
        """
        resource = ScheduledJobResource(when=when, handler=handler)
        self.resources.append(resource)
        self._validate_trigger_groupings()

        return resource

    def RestAPI(
        self,
        inputs: Dict[str, Types],
        handler: str,
        outputs: Optional[Dict[str, Types]] = None,
        loader: Optional[str] = None,
        keep_warm_seconds: Optional[int] = None,
        **_,
    ):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            loader: specify the method that will load the data into the handler (optional)
            inputs: dictionary specifying how to serialize/deserialize input arguments
            outputs: dictionary specifying how to serialize/deserialize return values
            keep_warm_seconds: how long the app should stay warm after the last request
        """
        resource = RestAPIResource(
            inputs=inputs,
            handler=handler,
            outputs=outputs,
            loader=loader,
            keep_warm_seconds=keep_warm_seconds,
        )

        self.resources.append(resource)
        self._validate_trigger_groupings()

        return resource

    def get_trigger(
        self,
    ) -> Union[ScheduledJobResource, TaskQueueResource, RestAPIResource]:
        self._validate_trigger_groupings()

        if len(self.resources) == 0:
            return None

        return self.resources[0]

    def dumps(self):
        # To make this backwards compatible in the future after switching back to
        # multiple triggers, we will make this a list that currently will only have 1 trigger
        self._validate_trigger_groupings()
        triggers = []

        for r in self.resources:
            triggers.append(r.dumps())

        return triggers

    def from_config(self, triggers):
        if triggers is None:
            return

        for t in triggers:
            trigger_type = t.get("trigger_type")

            if trigger_type == TriggerType.Webhook:
                self.resources.append(TaskQueueResource.from_config(t))
            elif trigger_type == TriggerType.CronJob:
                self.resources.append(ScheduledJobResource.from_config(t))
            elif trigger_type == TriggerType.RestAPI:
                self.resources.append(RestAPIResource.from_config(t))
            else:
                raise ValueError(
                    f"Found an unknown trigger type in config: {trigger_type}"
                )
