import dataclasses
import os

from typing import List
from abc import abstractmethod
from copy import deepcopy
from marshmallow_dataclass import dataclass
from typing import ClassVar, Type as TypingType
from marshmallow import Schema as MarshmallowSchema
from beam.exceptions import BeamSerializationError
from beam.types import Types


@dataclass
class BaseSerializer:
    Schema: ClassVar[TypingType[Schema]] = MarshmallowSchema

    def validate_and_dump(self):
        validation_errors = self.validate()

        if len(validation_errors) > 0:
            raise BeamSerializationError(
                f"{self.__class__.__name__}\n{validation_errors}"
            )
        return self.dump()

    def validate(self):
        if os.getenv("SKIP_VALIDATION") is not None:
            return []

        data_to_val = {}

        for key, val in self.__dataclass_fields__.items():
            if isinstance(val, dataclasses.Field) and key != "Schema":
                data_to_val[key] = self.__getattribute__(key)

        validation_errors = []
        validation_errors = self.Schema().validate(data_to_val)

        if len(validation_errors) > 0:
            raise BeamSerializationError(
                f"{self.__class__.__name__}\n{validation_errors}"
            )

        return validation_errors

    def dump(self, data=None):
        if data:
            return self.Schema().dump(data)

        return self.Schema().dump(self)

    class Meta:
        ordered = True


class BaseTriggerSerializer(BaseSerializer):
    def dump(self):
        config = deepcopy(self)

        if hasattr(config, "inputs") and config.inputs is not None:
            config.inputs = Types.dump_schema(config.inputs)

        if hasattr(config, "outputs") and config.outputs is not None:
            config.outputs = Types.dump_schema(config.outputs)

        return super().dump(data=config)


class AbstractDataLoader:
    @abstractmethod
    def dumps(self):
        pass

    @abstractmethod
    def from_config(self):
        pass


class ResourceSet(AbstractDataLoader):
    def __init__(self, **kwargs) -> None:
        self.resources: List[AbstractDataLoader] = []

    def dumps(self):
        dump_data = []

        for r in self.resources:
            data = None
            if hasattr(r, "dumps"):
                data = r.dumps()
            elif hasattr(r, "validate_and_dump"):
                data = r.validate_and_dump()

            if data is None:
                raise BeamSerializationError(
                    f"{self.__class__.__name__} does not support {r.__class__.__name__}"
                )

            dump_data.append(data)

        return dump_data


class Resource(AbstractDataLoader):
    managers: List[ResourceSet] = []
    config: BaseSerializer = None

    def dumps(self):
        return self.config.validate_and_dump()
