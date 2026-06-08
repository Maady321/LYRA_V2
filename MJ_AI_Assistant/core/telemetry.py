import os
import asyncio
import logging
import functools
import time
from typing import Callable, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

logger = logging.getLogger("Telemetry")

_tracer = None
_meter = None
_agent_latency_histogram = None
_llm_latency_histogram = None

def init_telemetry(service_name: str = "lyra-aios"):
    global _tracer, _meter, _agent_latency_histogram, _llm_latency_histogram
    
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    resource = Resource.create({"service.name": service_name})
    
    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    otlp_trace_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    _tracer = trace.get_tracer(service_name)
    
    # Metrics
    otlp_metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(otlp_metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(service_name)
    
    _agent_latency_histogram = _meter.create_histogram(
        "agent_task_duration_seconds",
        description="Duration of agent task execution",
        unit="s"
    )
    
    _llm_latency_histogram = _meter.create_histogram(
        "llm_inference_duration_seconds",
        description="Duration of LLM generation",
        unit="s"
    )
    
    logger.info(f"OpenTelemetry initialized with OTLP endpoint: {endpoint}")

def trace_agent_execution(agent_name: str):
    """Decorator to trace agent execution time."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _tracer:
                return await func(*args, **kwargs)
                
            start_time = time.time()
            with _tracer.start_as_current_span(f"{agent_name}.execute") as span:
                span.set_attribute("agent.name", agent_name)
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("agent.status", "SUCCESS")
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("agent.status", "FAILED")
                    raise
                finally:
                    duration = time.time() - start_time
                    if _agent_latency_histogram:
                        _agent_latency_histogram.record(duration, {"agent": agent_name})
                        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _tracer:
                return func(*args, **kwargs)
                
            start_time = time.time()
            with _tracer.start_as_current_span(f"{agent_name}.execute") as span:
                span.set_attribute("agent.name", agent_name)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("agent.status", "SUCCESS")
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("agent.status", "FAILED")
                    raise
                finally:
                    duration = time.time() - start_time
                    if _agent_latency_histogram:
                        _agent_latency_histogram.record(duration, {"agent": agent_name})

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
