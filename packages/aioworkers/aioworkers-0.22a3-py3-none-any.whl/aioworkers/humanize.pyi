from _typeshed import Incomplete
from typing import Sequence, Union

def size(value: int, suffixes: Sequence[str] = ...) -> str: ...

pattern_valid: Incomplete
pattern: Incomplete
size_levels: Incomplete

def parse_size(value: Union[int, float, str]) -> Union[int, float]: ...

durations: Incomplete

def parse_duration(value: Union[int, float, str]) -> Union[int, float]: ...
