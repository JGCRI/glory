# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Initial Setup -----------------------------------------------------

import os
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GLORY'
copyright = '2022, Battelle Memorial Institute'
author = 'Mengqi Zhao'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.imgmath',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
    'sphinx_design',
    'sphinx-mathjax-offline'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The suffix of source filenames.
source_suffix = [".rst"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# replace "view page source" with "edit on github" in Read The Docs theme
#  * https://github.com/readthedocs/sphinx_rtd_theme/issues/529
html_context = {
    'display_github': True,
    'github_user': 'jgcri',
    'github_repo': 'glory',
    'github_version': 'main/docs/source/',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
# html_css_files = [
#     "css/glory.css",
#     "css/getting_started.css",
# ]

# If true, links to the reST sources are added to the pages.
#
html_show_sourcelink = False


import glory
version = str(glory.__version__)


# -- Extension configuration -------------------------------------------------
# panels_add_bootstrap_css = False


# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True