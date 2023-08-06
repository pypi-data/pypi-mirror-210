from __future__ import annotations

from typing import TYPE_CHECKING

from frinx.common.telemetry.enums import MetricDocumentation
from frinx.common.telemetry.enums import MetricLabel
from frinx.common.telemetry.enums import MetricName

if TYPE_CHECKING:
    from frinx.common.telemetry.metrics import Metrics


def increment_task_poll(metrics: Metrics, task_type: str) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_POLL,
        documentation=MetricDocumentation.TASK_POLL,
        labels={MetricLabel.TASK_TYPE: task_type}
    )


def increment_task_execution_queue_full(metrics: Metrics, task_type: str) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_EXECUTION_QUEUE_FULL,
        documentation=MetricDocumentation.TASK_EXECUTION_QUEUE_FULL,
        labels={MetricLabel.TASK_TYPE: task_type},
    )


def increment_uncaught_exception(metrics: Metrics) -> None:
    metrics.increment_counter(
        name=MetricName.THREAD_UNCAUGHT_EXCEPTION,
        documentation=MetricDocumentation.THREAD_UNCAUGHT_EXCEPTION,
        labels={},
    )


def increment_task_poll_error(metrics: Metrics, task_type: str, exception: Exception) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_POLL_ERROR,
        documentation=MetricDocumentation.TASK_POLL_ERROR,
        labels={MetricLabel.TASK_TYPE: task_type, MetricLabel.EXCEPTION: str(exception)},
    )


def increment_task_paused(metrics: Metrics, task_type: str) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_PAUSED,
        documentation=MetricDocumentation.TASK_PAUSED,
        labels={
            MetricLabel.TASK_TYPE: task_type
        }
    )


def increment_task_execution_error(metrics: Metrics, task_type: str, exception: Exception) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_EXECUTE_ERROR,
        documentation=MetricDocumentation.TASK_EXECUTE_ERROR,
        labels={MetricLabel.TASK_TYPE: task_type, MetricLabel.EXCEPTION: str(exception)},
    )


def increment_task_ack_failed(metrics: Metrics, task_type: str) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_ACK_FAILED,
        documentation=MetricDocumentation.TASK_ACK_FAILED,
        labels={
            MetricLabel.TASK_TYPE: task_type
        }
    )


def increment_task_ack_error(metrics: Metrics, task_type: str, exception: Exception) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_ACK_ERROR,
        documentation=MetricDocumentation.TASK_ACK_ERROR,
        labels={
            MetricLabel.TASK_TYPE: task_type,
            MetricLabel.EXCEPTION: str(exception)
        }
    )


def increment_task_update_error(metrics: Metrics, task_type: str, exception: Exception) -> None:
    metrics.increment_counter(
        name=MetricName.TASK_UPDATE_ERROR,
        documentation=MetricDocumentation.TASK_UPDATE_ERROR,
        labels={
            MetricLabel.TASK_TYPE: task_type,
            MetricLabel.EXCEPTION: str(exception)
        }
    )


def increment_external_payload_used(metrics: Metrics, entity_name: str, operation: str, payload_type: str) -> None:
    metrics.increment_counter(
        name=MetricName.EXTERNAL_PAYLOAD_USED,
        documentation=MetricDocumentation.EXTERNAL_PAYLOAD_USED,
        labels={
            MetricLabel.ENTITY_NAME: entity_name,
            MetricLabel.OPERATION: operation,
            MetricLabel.PAYLOAD_TYPE: payload_type
        }
    )


def increment_workflow_start_error(metrics: Metrics, workflow_type: str, exception: Exception) -> None:
    metrics.increment_counter(
        name=MetricName.WORKFLOW_START_ERROR,
        documentation=MetricDocumentation.WORKFLOW_START_ERROR,
        labels={
            MetricLabel.WORKFLOW_TYPE: workflow_type,
            MetricLabel.EXCEPTION: str(exception)
        }
    )


def record_workflow_input_payload_size(metrics: Metrics, workflow_type: str, version: str, payload_size: int) -> None:
    metrics.record_gauge(
        name=MetricName.WORKFLOW_INPUT_SIZE,
        documentation=MetricDocumentation.WORKFLOW_INPUT_SIZE,
        labels={
            MetricLabel.WORKFLOW_TYPE: workflow_type,
            MetricLabel.WORKFLOW_VERSION: version
        },
        value=payload_size
    )


def record_task_result_payload_size(metrics: Metrics, task_type: str, payload_size: int) -> None:
    metrics.record_gauge(
        name=MetricName.TASK_RESULT_SIZE,
        documentation=MetricDocumentation.TASK_RESULT_SIZE,
        labels={MetricLabel.TASK_TYPE: task_type},
        value=payload_size,
    )


def record_task_poll_time(metrics: Metrics, task_type: str, time_spent: float) -> None:
    metrics.record_gauge(
        name=MetricName.TASK_POLL_TIME,
        documentation=MetricDocumentation.TASK_POLL_TIME,
        labels={
            MetricLabel.TASK_TYPE: task_type
        },
        value=time_spent
    )


def record_task_execute_time(metrics: Metrics, task_type: str, time_spent: float) -> None:
    metrics.record_gauge(
        name=MetricName.TASK_EXECUTE_TIME,
        documentation=MetricDocumentation.TASK_EXECUTE_TIME,
        labels={MetricLabel.TASK_TYPE: task_type},
        value=time_spent,
    )
