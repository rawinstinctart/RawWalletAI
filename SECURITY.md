# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities to rawinstinctai@mail.de.  
Do not open public issues for security problems.

## Security Model

- No registration, no KYC, no central providers
- Self-custody only
- Local key management
- Seed phrases encrypted at rest
- Automated transactions supported

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | No        |
| main    | Yes       |

## Known Limitations

- PSBT finalization is currently a stub pending an audited external library
- Secret zeroization is limited in CPython; use process isolation for high-security deployments
- Electrum backend requires `electrumx` package and is marked experimental
