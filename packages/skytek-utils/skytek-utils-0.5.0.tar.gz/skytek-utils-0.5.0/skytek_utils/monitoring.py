import logging
import os
from functools import wraps
from time import time

logger = logging.getLogger(__name__)


def _to_bool(value: str) -> bool:
    return value.lower() in ("y", "yes", "true", "1")


DD_TRACE = _to_bool(os.environ.get("DD_TRACE", "true"))
DD_DOGSTATSD_DISABLE = _to_bool(os.environ.get("DD_DOGSTATSD_DISABLE", "false"))


def ddtags(obj):  # pylint: disable=unused-argument
    tags = []

    # @TODO put some project specific obj to tags conversion here

    return tags


def add_tags_to_span(span, tags):
    if isinstance(tags, (list, tuple)):
        for tag in tags:
            key, value = tag.split(":", maxsplit=2)
            span.set_tag(key, value)
    elif isinstance(tag, dict):
        for key, value in tags.items():
            span.set_tag(key, value)
    else:
        raise ValueError("Expected dict, list or tuple of tags")


if DD_TRACE:
    from ddtrace import tracer  # pylint: disable=unused-import
else:

    class _TracerContextManagerMock:
        def __init__(self, name):
            self.trace_name = name
            self.start_time = None

        def __enter__(self):
            self.start_time = time()
            logger.info("Trace: Started block %s", self.trace_name)
            return self

        def __exit__(self, type, value, traceback):  # pylint: disable=redefined-builtin
            end_time = time()
            run_time = end_time - self.start_time
            logger.info("Trace: Finished block %s after %ss", self.trace_name, run_time)

        def set_tag(self, key, value):
            logger.info("Trace: Tag %s = %s", key, value)

    class _TracerMock:
        def trace(self, name, *args, **kwargs):
            return _TracerContextManagerMock(name)

        def wrap(
            self, name=None, *dargs, **dkwargs
        ):  # pylint: disable=keyword-arg-before-vararg
            def wrap_decorator(func):
                @wraps(func)
                def wrapped(*args, **kwargs):
                    with self.trace(name, *dargs, **dkwargs):
                        return func(*args, **kwargs)

                return wrapped

            return wrap_decorator

    tracer = _TracerMock()


if not DD_DOGSTATSD_DISABLE:
    from datadog import statsd  # pylint: disable=unused-import
else:

    class _StatsdMock:
        def __getattr__(self, operation):
            def inner_fun(metric, *args, **kwargs):
                logger.info(
                    "Metric: %s at %s with args %s and kwargs %s",
                    operation,
                    metric,
                    args,
                    kwargs,
                )

            return inner_fun

    statsd = _StatsdMock()
