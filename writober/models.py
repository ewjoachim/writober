from __future__ import annotations

import calendar
import dataclasses
import datetime
import functools
import hashlib
import pathlib
import tomllib
import zoneinfo
from collections.abc import Iterable, Mapping, Sequence
from typing import Self, override

import bs4
import pydantic
import pydantic_extra_types.color
from pydantic import dataclasses as pdataclasses

from . import utils


@pdataclasses.dataclass(kw_only=True)
class Prompt:
    day_number: int
    color_index: int
    title: str
    original_prompt: str


@pdataclasses.dataclass(kw_only=True)
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


@pdataclasses.dataclass
class ColorCycle:
    colors: list[pydantic_extra_types.color.Color]

    def __getitem__(self, i: int) -> str:
        return self.colors[i % len(self.colors)].as_hex()


@pdataclasses.dataclass(kw_only=True)
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
    def get_all(cls, settings: Settings) -> Writings:
        result: dict[int, list[Self]] = {}
        for year in settings.years:
            year_folder = settings.args.source_dir / f"{year}"
            for path in sorted(year_folder.glob("[0-9][0-9]-*.md")):
                writing = cls.from_path(path, month=settings.month)
                if writing.date > settings.until:
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
                color_index=(day_number + first - 1),
                original_prompt=original_prompt.title(),
                title=title,
            )

    def social_preview_filename(self, signature: str) -> str:
        return str(self.path(f"{signature}.png")).replace("/", "-")


type Writings = Mapping[int, Sequence[Writing]]


@pdataclasses.dataclass(kw_only=True)
class Args:
    source_dir: pathlib.Path
    build_dir: pathlib.Path
    provided_until: datetime.date | None


class IconLink(pydantic.BaseModel):
    rel: str
    type: str | None = None
    sizes: str | None = None
    href: str


class Settings(pydantic.BaseModel):
    args: Args
    site_name: str
    description: str
    copyright: str
    author: str
    month: int
    month_name: str
    years: list[int]
    language: str
    base_url: str
    repository_url: str
    timezone: str
    colors: list[pydantic_extra_types.color.Color]
    index_colors: list[str]
    inject_hot_reload_js: bool = False
    social_preview_width: int = 1200
    social_preview_height: int = 630
    social_preview_path: pathlib.Path = pathlib.Path("social_previews")
    logo: pathlib.Path
    atom_path: pathlib.Path = pathlib.Path("feed.atom")
    icon_links: list[IconLink]
    body_font_family: str
    body_font_file_woff2: pathlib.Path
    title_font_family: str
    title_font_file_woff2: pathlib.Path
    source_static_dir: pathlib.Path = pathlib.Path("static")
    build_static_dir: pathlib.Path = pathlib.Path("static")
    extra_css: list[pathlib.Path] = []

    @property
    def until(self) -> datetime.date:
        return (
            self.args.provided_until
            or datetime.datetime.now(tz=zoneinfo.ZoneInfo(self.timezone)).date()
        )

    @property
    def color_cycle(self) -> ColorCycle:
        return ColorCycle(self.colors)

    @classmethod
    def from_pyproject(cls, args: Args) -> Self:
        pyproject = args.source_dir / "pyproject.toml"
        pyprojects_settings = tomllib.loads(pyproject.read_text())["tool"]["writober"]
        settings = cls(**pyprojects_settings, args=args)
        return settings


@pdataclasses.dataclass(kw_only=True)
class PageMetadata:
    title: str | None
    url_path: str | None
    description: str
    social_preview_path: pathlib.Path
    repository_url_path: pathlib.Path


@pdataclasses.dataclass(kw_only=True)
class TextArtifact:
    path: pathlib.Path
    contents: str

    def write(self, dir: pathlib.Path):
        if self.path.is_absolute():
            raise ValueError("Only relative paths are accepted")

        (dir / self.path).parent.mkdir(exist_ok=True, parents=True)
        (dir / self.path).write_text(self.contents)


@pdataclasses.dataclass(kw_only=True)
class HTMLArtifact(TextArtifact):
    @override
    def write(self, dir: pathlib.Path):
        self.contents: str = bs4.BeautifulSoup(self.contents, "html.parser").prettify()
        super().write(dir=dir)


@pdataclasses.dataclass(kw_only=True)
class BytesArtifact:
    path: pathlib.Path
    contents: bytes

    def write(self, dir: pathlib.Path):
        if self.path.is_absolute():
            raise ValueError("Only relative paths are accepted")

        (dir / self.path).parent.mkdir(exist_ok=True, parents=True)
        (dir / self.path).write_bytes(self.contents)


@pdataclasses.dataclass(kw_only=True)
class FeedEntryArtifact:
    id: str
    title: str
    link: str
    date: datetime.date


type Artifact = (
    TextArtifact | HTMLArtifact | BytesArtifact | FeedEntryArtifact | FileArtifact
)


@pdataclasses.dataclass(kw_only=True)
class FileArtifact:
    path: pathlib.Path
    source: pathlib.Path
    destination: pathlib.Path

    def write(self, dir: pathlib.Path):
        rel = self.path.relative_to(self.source)
        destination = dir / self.destination / rel
        destination.parent.mkdir(exist_ok=True, parents=True)
        self.path.copy(destination)


@pdataclasses.dataclass(kw_only=True)
class SocialPreviewContents:
    """
    Parameters for generating a social preview PNG.
    """

    top_line: str
    title: str
    description: str
    logo: pathlib.Path
    date: str | None  # this might not strictly be a date
    colors: list[str]
    body_font_file_woff2: pathlib.Path
    title_font_file_woff2: pathlib.Path

    @property
    def signature(self) -> str:
        return hashlib.md5(str(dataclasses.asdict(self)).encode()).hexdigest()[:8]
