# Releasing AliasingAtlas

This project publishes releases from version tags through GitHub Actions.

## One-Time PyPI Setup

The release workflow uses PyPI Trusted Publishing, so no long-lived PyPI token is stored in GitHub.

1. Create the `aliasing-atlas` project on PyPI, or request the project name if it is already reserved.
2. In PyPI, add a pending trusted publisher with:
   - Owner: `Boussetta`
   - Repository: `NyquistNavigator`
   - Workflow: `release.yml`
   - Environment: `pypi`
3. Ensure the GitHub repository has an environment named `pypi`.
4. Restrict the environment deployment rule to protected version tags where practical.

Until this setup is complete, the release workflow will build and validate distributions but publishing will fail at the publish step.

## Release Checklist

1. Update `project.version` in `pyproject.toml`.
2. Add release notes to `CHANGELOG.md`.
3. Run the local verification commands:

   ```bash
   .venv/bin/python -m pytest -q --cov=aliasing_atlas --cov-report=term-missing
   .venv/bin/python -m ruff check src tests
   .venv/bin/python -m mypy src/aliasing_atlas --ignore-missing-imports
   .venv/bin/python -m pip wheel . --no-deps --no-build-isolation -w /tmp/aliasing-atlas-dist
   ```

4. Confirm the version and release notes are committed to `main`.
5. Create an annotated version tag matching `pyproject.toml` exactly:

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

6. Monitor the `Release` workflow.
7. Verify the package page, GitHub release, and attached distributions.
8. Update the Colab notebook guidance after the first successful PyPI publication.

## Versioning Policy

Use Semantic Versioning:

- Patch: backwards-compatible bug fixes.
- Minor: backwards-compatible features.
- Major: breaking API or behavior changes.

The workflow rejects a tag when its version does not exactly match `pyproject.toml`.

## Recovery

If a release fails before publishing, fix the issue and push a new commit to `main`, then delete and recreate the tag only if it has not been published. Never overwrite a package version already published to PyPI; increment the version instead.
