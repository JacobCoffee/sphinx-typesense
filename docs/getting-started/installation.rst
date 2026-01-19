Installation
============

sphinx-typesense can be installed using your preferred Python package manager.

.. tab-set::

   .. tab-item:: uv
      :sync: uv

      .. code-block:: bash

         uv add sphinx-typesense

   .. tab-item:: pip
      :sync: pip

      .. code-block:: bash

         pip install sphinx-typesense

   .. tab-item:: Poetry
      :sync: poetry

      .. code-block:: bash

         poetry add sphinx-typesense

   .. tab-item:: PDM
      :sync: pdm

      .. code-block:: bash

         pdm add sphinx-typesense

Development Installation
------------------------

To install from source for development:

.. code-block:: bash

   git clone https://github.com/JacobCoffee/sphinx-typesense.git
   cd sphinx-typesense
   uv sync --group dev

Dependencies
------------

sphinx-typesense has the following dependencies, which are automatically installed:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Package
     - Version
     - Purpose
   * - sphinx
     - >=7.0.0
     - Sphinx documentation framework
   * - typesense
     - >=0.21.0
     - Typesense Python client
   * - beautifulsoup4
     - >=4.12.0
     - HTML parsing for content extraction

Optional Dependencies
---------------------

Pagefind Backend
~~~~~~~~~~~~~~~~

To use the Pagefind backend (static search, no server required), install with the
``pagefind`` extra:

.. tab-set::

   .. tab-item:: uv
      :sync: uv

      .. code-block:: bash

         uv add "sphinx-typesense[pagefind]"

   .. tab-item:: pip
      :sync: pip

      .. code-block:: bash

         pip install "sphinx-typesense[pagefind]"

   .. tab-item:: Poetry
      :sync: poetry

      .. code-block:: bash

         poetry add "sphinx-typesense[pagefind]"

   .. tab-item:: PDM
      :sync: pdm

      .. code-block:: bash

         pdm add "sphinx-typesense[pagefind]"

This installs the Python ``pagefind`` package which bundles the Pagefind binary.
No Node.js or npm is required.

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

For building documentation:

.. code-block:: bash

   uv sync --group docs

This installs additional packages needed for building the sphinx-typesense
documentation itself, including the Shibuya theme and sphinx-design.

Verifying Installation
----------------------

After installation, verify that sphinx-typesense is available:

.. code-block:: python

   >>> import sphinx_typesense
   >>> sphinx_typesense.__version__
   '0.1.0'

Next Steps
----------

Continue to :doc:`quickstart` to configure sphinx-typesense in your project.
