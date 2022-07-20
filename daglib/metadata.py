import warnings
from pathlib import Path

import duckdb
import pandas as pd
from fastavro import reader


def _delete_folder(p: Path) -> None:
    for sub in p.iterdir():
        if sub.is_dir():
            _delete_folder(sub)
        else:
            sub.unlink()
    p.rmdir()


class MetaDB:
    def __init__(self) -> None:
        self._meta_dir = Path("meta/")
        if not self._meta_dir.exists():
            self._meta_dir.mkdir()

        self._profiling_dir = self._meta_dir / Path("profiling")
        if not self._profiling_dir.exists():
            self._profiling_dir.mkdir()

        profiling_record_paths = list(self._profiling_dir.rglob("*.avro"))

        profiling_records = []
        for p in profiling_record_paths:
            with open(p, "rb") as fp:
                for record in reader(fp):
                    profiling_records.append(record)

        self.profiling = pd.DataFrame(profiling_records)

    def query(self, query: str) -> pd.DataFrame | None:
        profiling = self.profiling  # noqa: F841
        con = duckdb.connect()
        try:
            df = con.execute(query).df()
            return df
        except RuntimeError:
            warnings.warn("No profiling records found")
            return pd.DataFrame()
        finally:
            con.close()

    def drop(self) -> None:
        try:
            _delete_folder(self._meta_dir)
        except FileNotFoundError:
            pass
        self.profiling = self.profiling.head(0)
