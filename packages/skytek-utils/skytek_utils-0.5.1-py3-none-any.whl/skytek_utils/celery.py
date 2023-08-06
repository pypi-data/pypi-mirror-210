import importlib
from inspect import getmembers
from typing import Generator, Iterable

import kombu


def autodiscover_celery_queues(
    installed_apps: Iterable[str],
) -> Generator[kombu.Queue, None, None]:
    for app in installed_apps:
        queues_module_path = f"{app}.queues"

        try:
            queues_module = importlib.import_module(queues_module_path)
        except ImportError:
            continue

        for name, queue in getmembers(queues_module):
            if name.startswith("_"):
                continue
            if isinstance(queue, kombu.Queue):
                yield queue
            elif isinstance(queue, str):
                yield kombu.Queue(queue, routing_key=queue, exchange=queue)
