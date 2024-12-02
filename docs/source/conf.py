# Add your project directory to sys.path
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'PIScO development'
copyright = '2024, GEOMAR'
author = 'vdausmann'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    #"sphinxcontrib.programoutput",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx.ext.coverage",
    "sphinx.ext.autosummary",
]

# Mock modules so that they don't need to be available
# just to generate the documentstion.
autodoc_mock_imports = ["matplotlib"]

napoleon_use_param = False
napoleon_use_keyword = False
napoleon_use_rtype = False
typehints_document_rtype = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # TODO: Always link to the latest stable
    "pims": ("https://soft-matter.github.io/pims/v0.4.1/", None),
    "skimage": ("https://scikit-image.org/docs/stable/", None),
    "PIL": ("https://pillow.readthedocs.io/en/stable/", None),
    "h5py": ("https://docs.h5py.org/en/stable/", None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'


