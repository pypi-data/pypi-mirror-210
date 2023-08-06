import os.path
import sys
from typing import Any, Final

# Add the project's root directory to the sys.path:
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Project Information
# -------------------

# The documented project's name:
project: Final[str] = "jsonrpc-py"

# General Configuration
# ---------------------

# A list of strings that are module names of extensions:
extensions: Final[tuple[str, ...]] = (
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
)

# Highlighting of the code blocks:
pygments_style: Final[str] = "stata-light"

# This variable is Furo-specific at this time:
pygments_dark_style: Final[str] = "stata-dark"

# Options for HTML Output
# -----------------------

# The "theme" that the HTML output should use:
html_theme: Final[str] = "furo"

# The "title" for HTML documentation:
html_title: Final[str] = project

# The base URL which points to the root of the HTML documentation:
html_baseurl: Final[str] = "https://docs.jsonrpc.ru"

# If true, the reST sources are included in the HTML build as _sources/name:
html_copy_source: Final[bool] = False

# If true, "(c) Copyright ..." is shown in the HTML footer:
html_show_copyright: Final[bool] = False

# Automatically documented members are sorted by source order:
autodoc_member_order: Final[str] = "bysource"

# Don't show typehints in docstrings:
autodoc_typehints: Final[str] = "none"

# The locations and names of other projects
# that should be linked to in this documentation:
intersphinx_mapping: Final[dict[str, Any]] = {
    "python": ("https://docs.python.org/3.11/", None),
}
