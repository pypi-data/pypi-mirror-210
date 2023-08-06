from threading import Lock
from typing import Any

from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import start_wsgi_server
from prometheus_client.registry import CollectorRegistry
from pydantic import BaseModel
from pydantic import Field

from frinx.common.telemetry.enums import MetricDocumentation
from frinx.common.telemetry.enums import MetricLabel
from frinx.common.telemetry.enums import MetricName


class MetricsSettings(BaseModel):
    metrics_enabled: bool = True
    port: int = Field(default=8000)


class MetricsSingletonMeta(type):

    _instances: dict[Any, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Metrics(metaclass=MetricsSingletonMeta):
    counters: dict[str, Counter] = {}
    gauges: dict[str, Gauge] = {}
    registry: CollectorRegistry
    settings: MetricsSettings

    def __init__(self, settings: MetricsSettings | None = None):
        if settings is not None:
            self.settings = settings
            self.__init_collector()
        else:
            self.settings = MetricsSettings(metrics_enabled=False)

    def __init_collector(self) -> None:
        if self.settings.metrics_enabled:
            self.registry = CollectorRegistry()
            start_wsgi_server(self.settings.port, registry=self.registry)

    def increment_counter(
            self, name: MetricName, documentation: MetricDocumentation, labels: dict[MetricLabel, str]
    ) -> None:

        if self.settings.metrics_enabled:
            counter = self.__get_counter(
                name=name, documentation=documentation, label_names=list(labels.keys())
            )
            counter.labels(*labels.values()).inc()

    def record_gauge(
            self,
            name: MetricName,
            documentation: MetricDocumentation,
            labels: dict[MetricLabel, str],
            value: Any,
    ) -> None:
        if self.settings.metrics_enabled:
            gauge = self.__get_gauge(
                name=name, documentation=documentation, label_names=list(labels.keys())
            )
            gauge.labels(*labels.values()).set(value)

    def __get_counter(
            self, name: MetricName, documentation: MetricDocumentation, label_names: list[MetricLabel]
    ) -> Counter:
        if name not in self.counters:
            self.counters[name] = self.__generate_counter(name, documentation, label_names)
        return self.counters[name]

    def __get_gauge(
            self, name: MetricName, documentation: MetricDocumentation, label_names: list[MetricLabel]
    ) -> Gauge:
        if name not in self.gauges:
            self.gauges[name] = self.__generate_gauge(name, documentation, label_names)
        return self.gauges[name]

    def __generate_counter(
            self, name: MetricName, documentation: MetricDocumentation, label_names: list[MetricLabel]
    ) -> Counter:
        return Counter(
            name=name, documentation=documentation, labelnames=label_names, registry=self.registry
        )

    def __generate_gauge(
            self, name: MetricName, documentation: MetricDocumentation, label_names: list[MetricLabel]
    ) -> Gauge:
        return Gauge(
            name=name, documentation=documentation, labelnames=label_names, registry=self.registry
        )
