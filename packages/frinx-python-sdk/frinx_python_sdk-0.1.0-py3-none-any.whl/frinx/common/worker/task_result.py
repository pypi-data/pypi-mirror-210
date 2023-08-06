from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.util import snake_to_camel_case


class TaskResult(BaseModel):
    status: TaskResultStatus
    output: dict[str, Any] = Field(default={})
    logs: list[str] | str = Field(default=[])

    class Config:
        validate_assignment = True
        alias_generator = snake_to_camel_case
        allow_population_by_field_name = True

    @validator('logs', always=True)
    def validate_logs(cls, logs: str | list[str]) -> list[str]: # noqa: 805
        match logs:
            case list():
                return logs
            case str():
                return [logs]

    def add_output_data(self, key: str, value: Any) -> None:
        if self.output is None:
            self.output = {}
        self.output[key] = value

    def add_output_data_dict(self, data: dict[str, Any]) -> None:
        self.output = data
