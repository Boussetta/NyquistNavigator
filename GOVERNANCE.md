# Project Governance

## Vision

AliasingAtlas is an open-source educational tool designed to make digital signal processing (DSP) concepts accessible to students and practitioners. We are committed to maintaining a high-quality, well-documented, and pedagogically sound project.

## Project Roles

### Maintainers

**Current Maintainer**: Wissem Boussetta (@Boussetta)

Maintainers are responsible for:

- Reviewing and merging pull requests
- Releasing new versions
- Maintaining project infrastructure
- Setting direction on major features
- Ensuring code quality and documentation standards

### Contributors

Contributors submit code, documentation, bug reports, and feature requests. All contributions are valued and help improve the project.

### Users

Users download, use, and provide feedback on AliasingAtlas. Your use cases and suggestions drive project improvements.

## Decision Making

### Minor Changes

**Definition**: Bug fixes, documentation updates, small refactorings that don't alter user-facing behavior.

**Process**: Direct merge by maintainer after code review.

### Feature Additions

**Definition**: New signal models, UI enhancements, pedagogical features.

**Process**:
1. Open a discussion or issue describing the feature
2. Gather feedback from maintainers and community
3. Submit a pull request with implementation
4. Maintainer reviews and merges with feedback

### Major Changes

**Definition**: Architectural changes, API redesign, significant performance improvements.

**Process**:
1. Open a detailed issue with motivation and design proposal
2. Maintainer and interested contributors discuss trade-offs
3. Consensus reached before implementation begins
4. Detailed pull request with documentation and tests required

### Breaking Changes

Breaking changes require:
- Clear justification in the issue
- Communication plan (changelog, deprecation warning if applicable)
- Increment major version number (semantic versioning)
- Update all affected documentation and examples

## Maintenance Priorities

Listed in order of importance:

1. **Educational Value**: Does this improve student understanding of DSP concepts?
2. **Code Quality**: Is the code well-tested, documented, and maintainable?
3. **Usability**: Is the tool easy to use and understand?
4. **Performance**: Does the tool respond quickly and efficiently?
5. **Features**: Does the feature align with project goals?

## Release Policy

### Versioning

AliasingAtlas follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- Increment MAJOR for breaking changes
- Increment MINOR for new features (backwards compatible)
- Increment PATCH for bug fixes

### Release Frequency

- Patch releases: As-needed for bug fixes
- Minor releases: Quarterly or when significant features accumulate
- Major releases: When needed for architectural improvements

### Release Process

1. Identify commits since last release
2. Update version in `src/aliasing_atlas/__init__.py`
3. Update `CHANGELOG.md` with changes and author credits
4. Create git tag: `git tag -a v{VERSION} -m "Release v{VERSION}"`
5. Push to GitHub
6. CI/CD automatically builds and publishes to PyPI

## Deprecation Policy

When features are removed or changed significantly:

1. Add a **deprecation warning** at least one minor version before removal
2. Document the **migration path** clearly
3. Provide a **removal timeline** (e.g., will be removed in v2.0)
4. Update documentation with examples of the new approach

Example:

```python
import warnings

def old_function():
    """Old function (deprecated, use new_function instead)."""
    warnings.warn(
        "old_function is deprecated and will be removed in v2.0. Use new_function instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... implementation
```

## Code of Conduct

All participants (contributors, maintainers, users) are expected to:

- Be respectful and professional
- Welcome diverse perspectives and backgrounds
- Report violations privately to maintainers
- Assume good intentions while addressing impacts

Unacceptable behavior includes harassment, discrimination, or deliberate disruption.

## Attribution

We value all contributions. Contributors will be recognized through:

- Git commit history
- Release notes
- Project contributors list (if established)

## Dispute Resolution

If disagreements arise:

1. **Direct discussion**: Respectfully discuss the issue on GitHub
2. **Seek consensus**: Maintainers work to find a mutually acceptable solution
3. **Maintainer decision**: If consensus cannot be reached, the maintainer makes a final decision
4. **Appeal**: Disputed decisions can be reviewed if substantial new information emerges

## Community

We encourage community involvement through:

- **Issues**: Report bugs, request features, discuss design
- **Discussions**: Ask questions, share ideas, brainstorm features
- **Pull Requests**: Contribute code and documentation
- **Teaching**: Use AliasingAtlas in classrooms and share feedback

## Amendments

This governance policy can be updated as the project evolves. Significant changes will be discussed with contributors and documented in release notes.

