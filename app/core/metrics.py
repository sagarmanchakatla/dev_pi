from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app):
    """Add Prometheus metrics endpoint to the FastAPI app."""
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        inprogress_name="platform_api_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")
    return instrumentator
