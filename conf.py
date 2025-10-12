# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys

sys.path.append(".")

import datetime
import pathlib

import generate_card

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Ewjoachim's Writober Journal"
copyright = "2024- Joachim Jablon - CC-BY-SA-NC"
author = "Joachim Jablon"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinxfeed", "sphinxext.opengraph"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv", "CONTRIBUTING.md"]

# Assume we're in the correct timezone
today_date = datetime.date.today()
# Exclude all future pages
if today_date.month == 10:
    exclude_patterns.extend(
        f"{today_date.year}/{i:02}-*.md" for i in range(today_date.day + 1, 32)
    )

# Exclude empty ones
exclude_patterns.extend(
    str(p.relative_to(pathlib.Path.cwd()))
    for p in pathlib.Path.cwd().glob("20*/*-*.md")
    if p.read_text().strip().endswith("]")
)

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


def setup(app):
    app.connect("generate-social-card", generate_card.generate_card)
