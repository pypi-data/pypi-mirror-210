from typing import Any

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field

from frinx.common.conductor_enums import RetryLogic
from frinx.common.conductor_enums import TimeoutPolicy
from frinx.common.frinx_rest import X_FROM
from frinx.common.util import snake_to_camel_case


class TaskInput(BaseModel):
    class Config:
        allow_mutation = False
        extra = Extra.forbid
        validate_all = True
        arbitrary_types_allowed = False
        allow_population_by_field_name = False


class TaskOutput(BaseModel):
    class Config:
        allow_mutation = False
        extra = Extra.allow


class BaseTaskdef(BaseModel):
    name: str | None
    description: str | None
    owner_app: str | None = Field(default=None)
    create_time: int | None = Field(default=None)
    update_time: int | None = Field(default=None)
    created_by: str | None = Field(default=None)
    updated_by: str | None = Field(default=None)
    retry_count: int | None = Field(default=None)
    timeout_seconds: int | None = Field(default=None)
    input_keys: list[str] | None = Field(default=None)
    output_keys: list[str] | None = Field(default=None)
    timeout_policy: TimeoutPolicy | None = Field(default=None)
    retry_logic: RetryLogic | None = Field(default=None)
    retry_delay_seconds: int | None = Field(default=None)
    response_timeout_seconds: int | None = Field(default=None)
    concurrent_exec_limit: int | None = Field(default=None)
    input_template: dict[str, Any] | None = Field(default=None)
    rate_limit_per_frequency: int | None = Field(default=None)
    rate_limit_frequency_in_seconds: int | None = Field(default=None)
    isolation_group_id: str | None = Field(default=None)
    execution_name_space: str | None = Field(default=None)
    owner_email: str | None = Field(default=None)
    poll_timeout_seconds: int | None = Field(default=None)
    backoff_scale_factor: int | None = Field(default=None)
    limit_to_thread_count: int | None = Field(default=None)

    class Config:
        allow_mutation = False
        extra = Extra.forbid
        validate_assignment = True
        alias_generator = snake_to_camel_case
        allow_population_by_field_name = True
        # TODO  add validators


class TaskDefinition(BaseTaskdef):
    name: str
    description: str
    labels: list[object] | None = Field(default=None)
    rbac: list[object] | None = Field(default=None)

    class Config:
        allow_mutation = True
        extra = Extra.forbid


class DefaultTaskDefinition(BaseTaskdef):
    retry_count: int = 0
    timeout_policy: TimeoutPolicy = TimeoutPolicy.ALERT_ONLY
    timeout_seconds: int = 60
    retry_logic: RetryLogic = RetryLogic.FIXED
    retry_delay_seconds: int = 0
    response_timeout_seconds: int = 59
    rate_limit_per_frequency: int = 0
    rate_limit_frequency_in_seconds: int = 5
    owner_email: str = X_FROM


class ConductorWorkerError(Exception):
    """Base error of Conductor worker."""


class InvalidTaskInputError(ConductorWorkerError):
    """Error due to invalid input of (simple) task."""


class FailedTaskError(ConductorWorkerError):
    """Exception causing task to fail with provided message instead of full traceback."""

    def __init__(self, error_msg: str) -> None:
        self.error_msg = error_msg
