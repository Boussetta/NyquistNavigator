# Contributing to AliasingAtlas

Thank you for your interest in contributing to AliasingAtlas! This document provides guidelines for contributing code, documentation, and feedback to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- Be respectful and constructive in all interactions
- Provide credit and attribution where due
- Respect differing opinions and experiences
- Report unacceptable behavior to the maintainers

## How to Contribute

### Reporting Issues

If you discover a bug or have a feature request:

1. **Search existing issues** to avoid duplicates
2. **Create a detailed issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Your environment (Python version, OS, dependencies)
3. **Attach screenshots or examples** if applicable

### Submitting Code Changes

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Boussetta/NyquistNavigator.git
cd sinewave-sampling

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
pip install pytest pytest-cov black flake8 mypy
```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write code** adhering to project standards:
   - Follow PEP 8 style guidelines
   - Add docstrings to all functions and classes (Google style)
   - Include type hints for function signatures
   - Keep functions small and focused (single responsibility)

3. **Write tests** for new functionality:
   - Maintain or improve test coverage
   - Tests should be in `tests/` directory
   - Use pytest conventions (test files start with `test_`)
   - Run tests before committing: `pytest`

4. **Format and lint your code**
   ```bash
   black src/ tests/
   flake8 src/ tests/ --max-line-length=100
   mypy src/ --strict
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new feature
   
   Detailed explanation of changes and motivation.
   References issue #123 if applicable."
   ```
   Use conventional commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

6. **Push and open a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Pull Request Guidelines

- **Reference related issues** in the PR description
- **Provide clear description** of changes and motivation
- **Keep PRs focused** on a single feature or fix
- **Be responsive** to code review feedback
- **Ensure CI passes** (tests, linting, type checking)

### Code Standards

#### Docstring Format

Use Google-style docstrings with the following structure:

```python
def sample_signal(t_cont: np.ndarray, y_cont: np.ndarray, f_samp: float, duration: float) -> Tuple[np.ndarray, np.ndarray]:
    """Sample a continuous-time proxy signal at a target sample rate.
    
    Args:
        t_cont: Time vector of the continuous proxy signal.
        y_cont: Amplitude values of the continuous proxy signal.
        f_samp: Target sampling frequency in Hz.
        duration: Total duration of the signal to sample in seconds.
    
    Returns:
        A tuple of (t_samp, y_samp) where:
            - t_samp: Time vector of sampled points
            - y_samp: Interpolated amplitude values at sampled times
    
    Raises:
        ValueError: If duration or f_samp is non-positive.
    """
```

#### Type Hints

Always include type hints for function arguments and return types:

```python
def compute_duration(f_sig: float, cycles: float = 3.0) -> float:
    """Return visualization duration that shows a fixed number of cycles."""
    return cycles / f_sig if f_sig > 0 else 1.0
```

#### Commenting

- Add comments explaining **why**, not **what** (code shows what)
- Use inline comments sparingly for complex logic
- Use section headers for major logical blocks

### Testing Guidelines

- **Unit tests** for all DSP functions and signal models
- **Integration tests** for UI workflows
- **Edge cases**: test boundary conditions, empty inputs, extreme values
- **Maintainability**: tests should be easy to understand and modify

Example test structure:

```python
def test_quantize_signal_16bit():
    """Test 16-bit quantization produces correct number of levels."""
    y = np.linspace(-1, 1, 1000)
    quantized = quantize_signal(y, 16)
    
    unique_levels = len(np.unique(quantized))
    assert unique_levels == 2**16
```

### Documentation

- Update `README.md` for user-facing changes
- Update docstrings when modifying functions
- Add comments to complex algorithms
- Keep `CHANGELOG.md` updated with notable changes

## Project Structure

```
sinewave-sampling/
├── src/aliasing_atlas/        # Main package
│   ├── __init__.py            # Version and exports
│   ├── __main__.py            # CLI entry point
│   ├── app.py                 # Main interactive UI
│   ├── dsp.py                 # Pure DSP functions
│   ├── signals.py             # Signal generation models
│   ├── presets.py             # Pedagogical presets
│   ├── learning.py            # Learning hints
│   └── exporting.py           # Export utilities
├── tests/                     # Test suite
├── AliasingAtlas.ipynb        # Interactive notebook
├── pyproject.toml             # Project metadata
├── README.md                  # User guide
├── CONTRIBUTING.md            # This file
├── GOVERNANCE.md              # Project governance
├── SECURITY.md                # Security policy
└── LICENSE                    # MIT License
```

## Release Process

Maintainers follow this process for releases:

1. Update version in `src/aliasing_atlas/__init__.py`
2. Update `CHANGELOG.md` with release notes
3. Create annotated git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions automatically builds and publishes to PyPI

## Questions?

- Open a **discussion** for questions and ideas
- Check **existing documentation** before asking
- Be patient and respectful when seeking help

Thank you for contributing! 🙏

