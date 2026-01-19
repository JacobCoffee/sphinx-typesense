"""Search backend implementations for sphinx-typesense.

This package provides pluggable search backends:
    - TypesenseBackend: Server-based search with Typesense
    - PagefindBackend: Static search with Pagefind (no server needed)

The backend is selected via the ``typesense_backend`` config option:
    - 'auto': Use Typesense if API key present, otherwise Pagefind
    - 'typesense': Force Typesense backend
    - 'pagefind': Force Pagefind backend

Example:
    In conf.py::

        typesense_backend = "auto"  # Default
        # OR
        typesense_backend = "pagefind"  # Static search only

"""

from sphinx_typesense.backends.base import SearchBackend
from sphinx_typesense.backends.pagefind import PagefindBackend
from sphinx_typesense.backends.typesense import TypesenseBackend

__all__ = ["PagefindBackend", "SearchBackend", "TypesenseBackend"]
