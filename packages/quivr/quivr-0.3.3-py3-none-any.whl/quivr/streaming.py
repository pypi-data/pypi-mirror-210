import pathlib
from typing import Iterator, TypeVar

from quivr import Table

T = TypeVar("T", bound=Table)


def chunked_read(path: pathlib.path, table_class: T, chunk_size: int) -> Iterator[T]:
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield table_class(chunk)
