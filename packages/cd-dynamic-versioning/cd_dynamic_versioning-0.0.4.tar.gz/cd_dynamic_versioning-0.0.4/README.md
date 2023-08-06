# Template for Statnett Python packages on GitHub

This is a template for Python packages made with Poetry at Statnett.
The CI pipelines (workflows) are defined in `.github/workflows`, and there are currently two of them:

 * `deploy.yml`
    - Runs for tags matching the pattern `"*.*.*"`
    - Runs tests and linting checks and if they succeed, the package is pushed to Test-PyPI and PyPI
 * `tests.yml`
    - Runs for all pushes and all PRs
    - Runs tests and linting checks

We hope to create a workflow for hosting documentation with Sphinx also.
