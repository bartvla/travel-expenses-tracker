from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)


def setup_metrics(app: FastAPI) -> None:
    """Wpina middleware zbierajace metryki HTTP i wystawia /metrics.
    """
    instrumentator = Instrumentator(
        excluded_handlers=["/metrics"],
        should_group_status_codes=False,
    )
    instrumentator.instrument(app, latency_lowr_buckets=LATENCY_BUCKETS)
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
