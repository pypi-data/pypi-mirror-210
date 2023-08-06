from pathlib import Path
from typing import Iterator

def bytes_to_temp_file(data: bytes) -> Iterator[Path]: ...
