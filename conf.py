# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Ewjoachim's Writober Journal"
copyright = "CC-BY-SA-NC © Copyright 2024- Joachim Jablon"
author = "Joachim Jablon"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]

language = "fr"

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
