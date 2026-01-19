============
Contributing
============

Thank you for your interest in contributing to sphinx-typesense! This guide will help you
get set up and ready to contribute.

.. contents:: Table of Contents
   :local:
   :depth: 2

Development Environment Setup
=============================

Prerequisites
-------------

Before you begin, ensure you have the following installed:

- **Python 3.9+** - The project supports Python 3.9 through 3.13
- **uv** - Modern Python package manager (`installation guide <https://docs.astral.sh/uv/getting-started/installation/>`_)
- **Docker** - Required for running integration tests with Typesense
- **Git** - For version control

Quick Setup
-----------

1. **Fork and clone the repository**:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/sphinx-typesense.git
      cd sphinx-typesense

2. **Run the setup command**:

   .. code-block:: bash

      make setup

   This single command will:

   - Install all development dependencies (docs, lint, test groups)
   - Install pre-commit hooks for automatic code quality checks

3. **Verify your setup**:

   .. code-block:: bash

      make test-smoke

   If all tests pass, you're ready to contribute!

Development Workflow
====================

Code Formatting
---------------

The project uses `Ruff <https://docs.astral.sh/ruff/>`_ for both formatting and linting.
Before committing, format your code:

.. code-block:: bash

   make fmt

This will:

- Format all Python code in ``src/`` and ``tests/``
- Auto-fix any fixable linting issues

To check formatting without making changes:

.. code-block:: bash

   make fmt-check

Linting
-------

Run the full linting suite (Ruff + mypy type checking):

.. code-block:: bash

   make lint

For just type checking:

.. code-block:: bash

   make typecheck

Testing
-------

**Run the full test suite with coverage**:

.. code-block:: bash

   make test

**Quick smoke test** (fast, excludes slow and integration tests):

.. code-block:: bash

   make test-smoke

**Run tests without coverage** (faster iteration):

.. code-block:: bash

   make test-fast

**Run tests in parallel**:

.. code-block:: bash

   make test-parallel

**Run with verbose output**:

.. code-block:: bash

   make test-verbose

Documentation
-------------

**Build the documentation**:

.. code-block:: bash

   make docs

**Live preview with auto-rebuild** (recommended for writing docs):

.. code-block:: bash

   make docs-serve

This starts a local server that automatically rebuilds when you save changes
and opens your browser.

**Clean documentation build artifacts**:

.. code-block:: bash

   make docs-clean

Running Integration Tests
=========================

Integration tests require a running Typesense instance. The project includes a Docker
Compose configuration to make this easy.

**Run integration tests** (automatically manages Typesense):

.. code-block:: bash

   make test-integration

This command will:

1. Start a Typesense container
2. Wait for it to be healthy
3. Run the integration test suite
4. Stop the container when done

**Manual Typesense management**:

.. code-block:: bash

   # Start Typesense
   make typesense-up

   # Stop Typesense
   make typesense-down

   # Stop and remove all data
   make typesense-clean

The Typesense instance will be available at ``http://localhost:8108`` with the
API key configured in ``tests/docker-compose.yml``.

Pull Request Guidelines
=======================

Workflow
--------

1. **Fork the repository** on GitHub

2. **Create a feature branch** from ``main``:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

3. **Make your changes** and ensure they follow the code style guidelines

4. **Run the CI checks locally**:

   .. code-block:: bash

      make ci

   This runs the same checks as the CI pipeline:

   - Format checking
   - Linting (Ruff + mypy)
   - Full test suite with coverage

5. **Commit your changes** with clear, descriptive commit messages:

   .. code-block:: text

      feat: add support for custom document schemas

      - Add schema configuration option to extension config
      - Update indexer to use custom fields
      - Add tests for schema validation

6. **Push your branch** and open a pull request

PR Checklist
------------

Before submitting your PR, ensure:

- [ ] ``make ci`` passes without errors
- [ ] New features include appropriate tests
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and follow conventional format

Commit Message Format
---------------------

We follow a conventional commit format:

- ``feat:`` - New features
- ``fix:`` - Bug fixes
- ``docs:`` - Documentation changes
- ``test:`` - Test additions or modifications
- ``refactor:`` - Code refactoring
- ``chore:`` - Maintenance tasks

Code Style
==========

Formatting and Linting
----------------------

- **Ruff** handles both formatting and linting
- Line length is set to **120 characters**
- Target Python version is **3.9** for compatibility
- Run ``make fmt`` before committing to auto-format

The full Ruff configuration is in ``pyproject.toml`` under ``[tool.ruff]``.

Type Hints
----------

Type hints are strongly encouraged and checked with mypy in strict mode:

.. code-block:: python

   def process_document(
       content: str,
       metadata: dict[str, Any] | None = None,
   ) -> ProcessedDocument:
       """Process a document for indexing.

       Args:
           content: The raw document content.
           metadata: Optional metadata to include.

       Returns:
           A processed document ready for indexing.
       """
       ...

Docstrings
----------

All public APIs should have docstrings. We use **Google style** docstrings:

.. code-block:: python

   def create_collection(
       name: str,
       fields: list[FieldDefinition],
   ) -> Collection:
       """Create a new Typesense collection.

       Creates a collection with the specified name and field definitions.
       If a collection with the same name already exists, it will be updated.

       Args:
           name: The name of the collection to create.
           fields: List of field definitions for the collection schema.

       Returns:
           The created or updated Collection object.

       Raises:
           TypesenseError: If the collection cannot be created.

       Example:
           >>> fields = [FieldDefinition(name="title", type="string")]
           >>> collection = create_collection("docs", fields)
       """
       ...

Pre-commit Hooks
================

The project uses pre-commit hooks to maintain code quality. They're installed
automatically during ``make setup``, but you can also manage them manually:

**Install hooks**:

.. code-block:: bash

   make pre-commit-install

**Run hooks on all files**:

.. code-block:: bash

   make pre-commit

The hooks include:

- Trailing whitespace removal
- End-of-file fixing
- YAML/TOML validation
- Ruff linting and formatting
- Codespell for typo checking
- mypy type checking
- sphinx-lint for RST files
- GitHub Actions workflow validation
- Secret detection

Useful Make Targets
===================

Here's a quick reference of all available make targets:

.. code-block:: text

   Installation:
     make install          - Install production dependencies only
     make dev              - Install development dependencies
     make dev-all          - Install all dependency groups explicitly
     make setup            - Complete development setup (recommended)

   Code Quality:
     make fmt              - Format code with Ruff
     make fmt-check        - Check formatting without changes
     make lint             - Run Ruff check and mypy
     make lint-fix         - Run Ruff with auto-fix
     make typecheck        - Run mypy only

   Testing:
     make test             - Run tests with coverage
     make test-smoke       - Quick smoke test
     make test-fast        - Run tests without coverage
     make test-verbose     - Run tests with verbose output
     make test-parallel    - Run tests in parallel
     make test-integration - Run integration tests (requires Docker)

   Documentation:
     make docs             - Build documentation
     make docs-serve       - Live preview server
     make docs-clean       - Clean build artifacts

   CI/CD:
     make check            - Run lint + test
     make ci               - Full CI pipeline (fmt-check, lint, test)
     make pre-commit       - Run pre-commit on all files

   Cleanup:
     make clean            - Remove all build artifacts
     make refresh          - Clean and reinstall dependencies

   Build:
     make build            - Build wheel and sdist
     make build-check      - Build and verify with twine

Getting Help
============

If you have questions or need help:

- Open an issue on `GitHub <https://github.com/JacobCoffee/sphinx-typesense/issues>`_
- Check existing issues and discussions for similar questions

Thank you for contributing!
