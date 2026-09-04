# Security Policy

## Reporting Security Vulnerabilities

**Do not** open public issues for security vulnerabilities. Instead, please report security issues responsibly through a private channel:

Please use [GitHub Security Advisories](https://github.com/Boussetta/NyquistNavigator/security/advisories/new) for private reports. If that page is unavailable, contact the repository maintainer through the GitHub profile.

Please include:

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if you have one)

We will acknowledge receipt of your report within 48 hours and provide a timeline for resolution.

## Security Considerations

### Input Validation

- All user inputs (frequency, sample rate, bit depth) are validated before use
- Numeric parameters are clamped to safe ranges
- No arbitrary code execution is possible through parameter inputs

### File Operations

- Export files are written to a designated `exports/` directory
- File paths are validated to prevent directory traversal
- Audio files are written in standard PCM16 format

### Dependencies

- We regularly review and update dependencies
- Critical security updates are prioritized
- Dependency vulnerabilities are reported through GitHub's security alerts

### Audio Processing

- Floating-point computations are bounded to prevent overflow
- Array operations use NumPy's safe defaults
- Audio output is clipped to valid ranges [-1.0, 1.0]

## Known Limitations

- **No network functionality**: This tool does not communicate over the network
- **Local-only**: All data processing occurs locally; no telemetry is sent
- **No persistent storage**: Configuration is not automatically saved between sessions (export explicitly)

## Security Best Practices for Users

1. **Keep dependencies updated**: Reinstall from the repository and review dependency updates periodically
2. **Use trusted Python environments**: Install in isolated virtual environments
3. **Verify authenticity**: Clone only from the official repository: `https://github.com/Boussetta/NyquistNavigator`
4. **Be cautious with audio**: Limit speaker volume when testing exported audio files

## Compliance

AliasingAtlas is provided as-is under the MIT License with no warranties. Users are responsible for ensuring compliance with applicable laws and regulations in their jurisdiction.

