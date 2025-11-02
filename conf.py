# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from collections.abc import Iterable
from typing import Self

import sphinx.application
import sphinx.environment

sys.path.append(".")

import dataclasses
import datetime
import pathlib

import generate_card

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Ewjoachim's Writober Journal"
copyright = "2024- Joachim Jablon - CC-BY-SA-NC"
author = "Joachim Jablon"

# Change this when inktober is moved to another month
inktober_month = 10
inktober_days = (
    datetime.date(2000, (inktober_month) % 12 + 1, 1) - datetime.timedelta(days=1)
).day

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinxfeed", "sphinxext.opengraph"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv", "CONTRIBUTING.md"]


class NotADay(Exception):
    pass


@dataclasses.dataclass
class Day:
    day: int
    year: int
    original_prompt: str

    @classmethod
    def from_path(cls, path: pathlib.Path) -> Self:
        return cls.from_docname(f"{path.parent.name}/{path.stem}")

    @classmethod
    def from_docname(cls, docname: str) -> Self:
        if "/" not in docname:
            raise NotADay
        year, day_title = docname.split("/", 1)
        if "-" not in day_title:
            raise NotADay
        day, word = day_title.split("-", 1)
        return cls(day=int(day), year=int(year), original_prompt=word)

    @classmethod
    def get_all(cls) -> Iterable[Self]:
        here = pathlib.Path.cwd()
        for path in here.glob("20*/*-*.md"):
            yield cls.from_path(path.relative_to(here))

    @property
    def docname(self) -> str:
        return f"{self.year}/{self.day:02}-{self.original_prompt}"

    @property
    def date(self) -> datetime.date:
        return datetime.date(self.year, inktober_month, self.day)

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path.cwd() / f"{self.docname}.md"


def get_excluded_days() -> Iterable[str]:
    # Assume we're in the correct timezone
    today_date = datetime.date.today()
    # Exclude all future pages
    if today_date.month == inktober_month:
        for i in range(today_date.day + 1, inktober_days + 1):
            yield f"{today_date.year}/{i:02}-*.md"

    # Exclude empty ones
    for day in Day.get_all():
        if day.path.read_text().strip().splitlines()[-1].startswith("#"):
            yield day.docname


exclude_patterns.extend(get_excluded_days())

language = "fr"

base_url = "https://writober.ewjoach.im"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


myst_enable_extensions = ["colon_fence"]


html_theme = "sphinx_book_theme"

html_title = "Ewjoachim's Writober Journal"
html_theme_options = {
    "repository_url": "https://github.com/ewjoachim/writober",
    "use_repository_button": True,
    "home_page_in_toc": True,
    "use_fullscreen_button": False,
    "use_download_button": False,
    "footer_content_items": ["copyright.html"],
}

html_sidebars = {"**": ["sbt-sidebar-nav.html"]}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Options for RSS feed -------------------------------------------------
feed_base_url = base_url
feed_author = "Joachim Jablon"
feed_description = (
    "Une nouvelle par jour d'octobre sur le thème du mot du jour d'Inktober"
)
feed_field_name = "date"

# -- Options for Opengraph -------------------------------------------------
ogp_site_url = base_url


def add_date(
    app: sphinx.application.Sphinx,
    env: sphinx.environment.BuildEnvironment,
):
    for docname in env.tocs:
        try:
            day = Day.from_docname(docname)
        except NotADay:
            continue
        metadata = env.metadata[docname]
        metadata["date"] = str(day.date)
        metadata["day"] = dataclasses.asdict(day)
        yield docname


def setup(app: sphinx.application.Sphinx):
    app.connect("generate-social-card", generate_card.generate_card)
    app.connect("env-updated", add_date)
