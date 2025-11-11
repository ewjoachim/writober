from __future__ import annotations

import functools
import itertools
from collections.abc import Iterable


@functools.cache
def excerpt(markdown: str, max_length: int = 200) -> str:
    words = [
        word.strip()
        for line in markdown.splitlines()[1:]
        if line.strip()
        for word in line.strip().split()
    ]
    length = 0
    take_first = 0
    suffix = "…"
    for i, word in enumerate(words):
        length += len(word) + 1
        if length + len(suffix) >= max_length:
            break
        take_first = i
    else:
        suffix = ""
    return " ".join(words[:take_first]) + suffix


def color_gradient(colors: list[str]) -> list[tuple[str, float]]:
    if len(colors) == 1:
        return [(colors[0], 0)]
    colors_levels: list[tuple[str, float]] = []
    level = 0
    increment = 1 / (len(colors) - 1)
    for color in colors:
        colors_levels.append((color, level))
        level += increment

    return colors_levels


def get_prev[T](obj: T, iterable: Iterable[T]) -> T | None:
    for prev, current in itertools.pairwise(iterable):
        if current is obj:
            return prev
    return None


def get_next[T](obj: T, iterable: Iterable[T]) -> T | None:
    for current, next in itertools.pairwise(iterable):
        if current is obj:
            return next
    return None
