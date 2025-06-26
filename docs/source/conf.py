# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath("../../src"))

# Mock external modules that might not be available during documentation build
autodoc_mock_imports = [
    "cv2",
    "numpy",
    "pandas",
    "scikit-learn",
    "sklearn",
    "freenect",
    "pythonosc",
    "python_osc",
    "websockets",
    "asyncio_mqtt",
    "fastapi",
    "uvicorn",
    "click",
    "rich",
    "pydantic",
    "stream_pose_ml",
]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Eddi"
copyright = "2025, Nate Green"
author = "Nate Green"

# Read version from pyproject.toml
try:
    import tomli

    with open("../../pyproject.toml", "rb") as f:
        data = tomli.load(f)
    version = data["project"]["version"] if "version" in data["project"] else "0.1.0"
except (ImportError, FileNotFoundError, KeyError):
    version = "0.1.0"

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx_multiversion",
    "sphinxext.opengraph",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# Alabaster theme options
html_theme_options = {
    "description": "Emergent Dynamic Design Interface - Interactive environmental systems through movement",
    "github_user": "mrilikecoding",
    "github_repo": "eddi",
    "github_button": True,
    "github_banner": True,
    "show_powered_by": False,
    "sidebar_includehidden": True,
    "sidebar_collapse": False,
    "fixed_sidebar": True,
    "page_width": "1200px",
    "sidebar_width": "300px",
    "body_max_width": "800px",
    "show_related": True,
}

# Sidebar configuration
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "versions.html",
    ]
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "opencv": ("https://docs.opencv.org/4.x/", None),
}

# OpenGraph metadata
ogp_site_url = "https://eddi.readthedocs.io/"
ogp_site_name = "Eddi Documentation"
ogp_description = "Interactive environmental systems through movement - Emergent Dynamic Design Interface"

# Mermaid settings
mermaid_version = "10.6.0"
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    themeVariables: {
        primaryColor: '#ffffff',
        primaryTextColor: '#000000',
        primaryBorderColor: '#000000',
        lineColor: '#000000',
        sectionBkgColor: '#f8f8f8',
        altSectionBkgColor: '#ffffff',
        gridColor: '#cccccc',
        secondaryColor: '#f0f0f0',
        tertiaryColor: '#ffffff'
    }
});
"""