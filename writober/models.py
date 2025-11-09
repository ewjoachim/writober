from __future__ import annotations

import calendar
import dataclasses
import datetime
import functools
import hashlib
import pathlib
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol, Self

from . import utils


@dataclasses.dataclass
class Prompt:
    day_number: int
    color: str
    title: str
    original_prompt: str


COLORS = [
    "#dd3300",
    "#f46101",
    "#f9980d",
    "#f4ca26",
    "#c0de48",
    "#77e173",
    "#31c8a7",
    "#de3e02",
    "#f47504",
    "#fdad16",
    "#fddc41",
    "#dbf172",
    "#9df1a3",
    "#4bcac3",
    "#da340c",
    "#f36710",
    "#fba921",
    "#f9df4c",
    "#c4f383",
    "#82f1af",
    "#3ac5c8",
    "#ce2619",
    "#f24d17",
    "#f88220",
    "#f9be4a",
    "#b4be9b",
    "#62ccc0",
    "#29abcd",
    "#bf1424",
    "#e22014",
    "#e84a31",
    "#e47178",
    "#9d69bb",
    "#4b73d5",
    "#156bce",
    "#901653",
    "#ae183e",
    "#b02b56",
    "#ad4084",
    "#773fae",
    "#3d40c1",
    "#153db7",
]


@dataclasses.dataclass
class MarkdownFile:
    md_path: pathlib.Path

    @functools.cached_property
    def markdown(self) -> str:
        return self.md_path.read_text()

    def excerpt(self, max_length: int = 200) -> str:
        return utils.excerpt(markdown=self.markdown, max_length=max_length)

    @property
    def full_title(self) -> str:
        for line in self.markdown.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ")

        return ""

    @property
    def title_elements(self) -> tuple[str, str]:
        num, title = tuple(self.full_title.split(" - ", maxsplit=1))
        return num, title

    @property
    def title(self) -> str:
        return self.title_elements[-1]


@dataclasses.dataclass
class Writing:
    date: datetime.date
    original_prompt: str

    @classmethod
    def from_path(cls, path: pathlib.Path, month: int) -> Self:
        year = path.parent.name
        day_title = path.stem
        day, word = day_title.split("-", 1)
        return cls(date=datetime.date(int(year), month, int(day)), original_prompt=word)

    @classmethod
    def get_all(cls, month: int, until: datetime.date) -> Writings:
        here = pathlib.Path.cwd()
        result: dict[int, list[Self]] = {}
        for year_folder in sorted(here.glob("20[0-9][0-9]")):
            year = int(f"{year_folder.name}")
            for path in sorted(year_folder.glob("[0-9][0-9]-*.md")):
                writing = cls.from_path(path, month=month)
                print(writing.date, until, writing.date > until)
                if writing.date > until:
                    return result
                result.setdefault(year, []).append(writing)

        return result

    @property
    def md_path(self) -> pathlib.Path:
        return self.path("md")

    @property
    def html_path(self) -> pathlib.Path:
        return self.path("html")

    def path(self, ext: str) -> pathlib.Path:
        return (
            pathlib.Path(f"{self.year}")
            / f"{self.day_number:02}-{self.original_prompt}.{ext}"
        )

    @property
    def day_number(self):
        return self.date.day

    @property
    def year(self):
        return self.date.year

    @classmethod
    @functools.cache
    def days_count_for_month(cls, year: int, month: int) -> int:
        return calendar.monthrange(year, month)[-1]

    @classmethod
    @functools.cache
    def first_weekday(cls, year: int, month: int) -> int:
        return calendar.monthrange(year, month)[0]

    @functools.cached_property
    def markdown_file(self) -> MarkdownFile:
        return MarkdownFile(md_path=self.md_path)

    def excerpt(self, max_length: int = 200) -> str:
        return utils.excerpt(markdown=self.markdown, max_length=max_length)

    @property
    def markdown(self) -> str:
        return self.markdown_file.markdown

    @property
    def full_title(self) -> str:
        return self.markdown_file.full_title

    @property
    def title_elements(self) -> tuple[str, str]:
        return self.markdown_file.title_elements

    @property
    def title(self) -> str:
        return self.markdown_file.title

    @property
    def prompts(self) -> Iterable[Prompt]:
        first = self.first_weekday(year=self.year, month=self.date.month)
        numbers, titles_str = self.title_elements
        day_numbers = (int(e) for e in numbers.split("&"))
        original_prompts = self.original_prompt.split("-")
        titles = titles_str.split(", ")
        for original_prompt, title, day_number in zip(
            original_prompts, titles, day_numbers
        ):
            yield Prompt(
                day_number=day_number,
                color=COLORS[day_number + first - 1],
                original_prompt=original_prompt.title(),
                title=title,
            )

    def get_repository_url_path(self):
        return f"blob/HEAD/{self.md_path}"

    def social_preview_filename(self, signature: str) -> str:
        return str(self.path(f"{signature}.png")).replace("/", "-")


type Writings = Mapping[int, Sequence[Writing]]


@dataclasses.dataclass
class Args:
    build_dir: pathlib.Path
    until: datetime.date


@dataclasses.dataclass(kw_only=True)
class Settings:
    site_name: str
    description: str
    copyright: str
    author: str
    month: int
    month_name: str
    language: str
    base_url: str
    repository_url: str
    build_dir: pathlib.Path
    until: datetime.date
    inject_hot_reload_js: bool = False
    social_preview_width: int = 1200
    social_preview_height: int = 630
    social_preview_path: pathlib.Path = pathlib.Path("social_previews")
    html_logo: pathlib.Path = pathlib.Path(
        "writober/static/_static/android-chrome-512x512.png"
    )

    @classmethod
    def from_pyproject(cls, args: Args) -> Self:
        pyproject = pathlib.Path("pyproject.toml")
        return cls(
            **tomllib.loads(pyproject.read_text())["tool"]["writober"],
            **dataclasses.asdict(args),
        )


@dataclasses.dataclass
class PageMetadata:
    title: str | None
    url_path: str | None
    description: str
    social_preview_path: pathlib.Path
    repository_url_path: str


class Artifact(Protocol):
    path: pathlib.Path

    def write(self, dir: pathlib.Path): ...


@dataclasses.dataclass
class TextArtifact:
    path: pathlib.Path
    contents: str

    def write(self, dir: pathlib.Path):
        if self.path.is_absolute():
            raise ValueError("Only relative paths are accepted")

        (dir / self.path).parent.mkdir(exist_ok=True, parents=True)
        (dir / self.path).write_text(self.contents)


@dataclasses.dataclass
class BytesArtifact:
    path: pathlib.Path
    contents: bytes

    def write(self, dir: pathlib.Path):
        if self.path.is_absolute():
            raise ValueError("Only relative paths are accepted")

        (dir / self.path).parent.mkdir(exist_ok=True, parents=True)
        (dir / self.path).write_bytes(self.contents)


@dataclasses.dataclass
class FileArtifact:
    path: pathlib.Path
    source: pathlib.Path

    def write(self, dir: pathlib.Path):
        rel = self.path.relative_to(self.source)
        destination = dir / rel
        destination.parent.mkdir(exist_ok=True, parents=True)
        self.path.copy(destination)


@dataclasses.dataclass
class SocialPreviewContents:
    """
    Parameters for generating a social preview PNG.
    """

    top_line: str
    title: str
    description: str
    html_logo: pathlib.Path
    date: str | None  # this might not strictly be a date
    colors: list[str]

    @property
    def signature(self) -> str:
        return hashlib.md5(str(dataclasses.asdict(self)).encode()).hexdigest()[:8]
