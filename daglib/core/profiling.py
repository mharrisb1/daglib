import time
from pathlib import Path
from typing import Any, TypeVar, Callable

from fastavro import writer, parse_schema

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])

_PROFILING_SCHEMA = parse_schema(
    {
        "doc": "daglib profiling stats",
        "name": "tprofile",
        "namespace": "daglib.profiling",
        "type": "record",
        "fields": [
            {"name": "dag_name", "type": "string"},
            {"name": "dag_description", "type": "string"},
            {"name": "run_id", "type": "string"},
            {"name": "task_name", "type": "string"},
            {"name": "task_description", "type": "string"},
            {"name": "task_runtime", "type": "float"},
        ],
    }
)


def profiling_wrapper(
    dag_name: str,
    dag_description: str,
    run_id: str,
    task_name: str,
    task_description: str,
    profile_dir: str,
    fn: WrappedFn,
    *args: Any,
    **kwargs: Any,
) -> Any:
    # noinspection PyShadowingNames
    def profiled_task(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        run_time = end - start
        record = {
            "dag_name": dag_name,
            "dag_description": dag_description,
            "run_id": run_id,
            "task_name": task_name,
            "task_description": task_description,
            "task_runtime": run_time,
        }
        out_dir = Path(profile_dir) / Path(dag_name)
        if not out_dir.parent.parent.exists():  # create meta/ if not exists
            out_dir.parent.parent.mkdir()
        if not out_dir.parent.exists():  # create meta/profiling if not exists
            out_dir.parent.mkdir()
        if not out_dir.exists():
            out_dir.mkdir()
        out_path = out_dir / Path(f"{run_id}.avro")
        if not out_path.exists():
            with open(out_path, "wb") as fp:
                writer(fp, _PROFILING_SCHEMA, records=[record])
        else:
            with open(out_path, "a+b") as fp:
                writer(fp, _PROFILING_SCHEMA, records=[record])
        return result

    return profiled_task
