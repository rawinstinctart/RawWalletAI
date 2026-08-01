# ADR-0006 — PSBT Finalization Wrapper API Design

**Status:** Proposed  
**Date:** 2026-08-01  
**Decision Owner:** Pascal Haux / RawInstinctAI  
**Context:** rust-bitcoin integration, wrapper design before implementation

---

## Context

We have accepted rust-bitcoin via PyO3 for PSBT finalization. This ADR defines the wrapper API surface before any implementation begins.

## Current State

- `src/rawwalletai/transactions/psbt.py` — PSBT parsing and signing
- `src/rawwalletai/transactions/pipeline.py` — E2E transaction pipeline
- `src/rawwalletai/transactions/builder.py` — Transaction building with fee validation

## Problem

We need a clean boundary between Python wallet logic and Rust Bitcoin protocol code. The wrapper must:

1. Expose minimal, focused API
2. Handle type conversions safely
3. Provide clear error messages
4. Support fallback when Rust unavailable
5. Enable future Taproot support

## Proposed API

### Core Functions

```python
# Finalize a signed PSBT into a raw transaction
def finalize_psbt(psbt_hex: str) -> str:
    """
    Finalize a signed PSBT and return the raw transaction hex.
    
    Args:
        psbt_hex: Hex-encoded signed PSBT
        
    Returns:
        Hex-encoded raw transaction ready for broadcast
        
    Raises:
        ImportError: If Rust extension is unavailable
        ValueError: If PSBT is invalid or missing signatures
        RuntimeError: If finalization fails
    """
```

```python
# Validate that a PSBT can be finalized
def validate_psbt(psbt_hex: str) -> bool:
    """
    Validate that a PSBT has all required signatures.
    
    Args:
        psbt_hex: Hex-encoded PSBT
        
    Returns:
        True if PSBT can be finalized
        
    Raises:
        ImportError: If Rust extension is unavailable
        ValueError: If PSBT is malformed
    """
```

```python
# Extract transaction data without finalizing
def extract_psbt_data(psbt_hex: str) -> dict:
    """
    Extract transaction data from PSBT for display/audit.
    
    Returns:
        Dict with inputs, outputs, fee, and metadata
    """
```

### Error Hierarchy

```python
class PSBTError(Exception):
    """Base PSBT error."""

class PSBTImportError(PSBTError):
    """Rust extension unavailable."""

class PSBTValidationError(PSBTError):
    """PSBT is malformed or missing data."""

class PSBTFinalizationError(PSBTError):
    """Finalization failed."""
```

### Fallback Behavior

When Rust is unavailable:
- `validate_psbt()` raises `PSBTImportError`
- `finalize_psbt()` raises `PSBTImportError`
- `extract_psbt_data()` returns empty dict or raises
- Other wallet functionality remains operational

## Integration Points

### Pipeline Integration

```python
# In transactions/pipeline.py
def _finalize_transaction(self, psbt: PSBT) -> RawTransaction:
    if not _rust_available:
        raise RuntimeError("PSBT finalization requires rust-bitcoin wrapper")
    raw_hex = finalize_psbt(psbt.serialize())
    return RawTransaction(hex=raw_hex)
```

### API Integration

```python
# In api/server.py
@app.post("/wallets/{wallet_id}/transactions/finalize")
async def finalize_transaction(wallet_id: str, psbt_hex: str):
    try:
        raw_tx = finalize_psbt(psbt_hex)
        return {"raw_transaction": raw_tx}
    except PSBTImportError:
        raise HTTPException(503, "PSBT finalization unavailable")
    except PSBTValidationError as e:
        raise HTTPException(400, str(e))
```

## Future Taproot Support

The wrapper API will be extended with:

```python
# Taproot-specific finalization
def finalize_taproot_psbt(psbt_hex: str) -> str:
    """Finalize Taproot PSBT with Schnorr signatures."""

# Taproot validation
def validate_taproot_psbt(psbt_hex: str) -> bool:
    """Validate Taproot PSBT structure."""
```

## Type Safety

All functions will use:
- `str` for hex-encoded data
- `dict` for structured data
- Explicit error types
- Full type annotations

No raw bytes in public API.

## Security Considerations

1. No key material in wrapper
2. PSBT validation before finalization
3. Clear error messages (no stack traces to callers)
4. No logging of sensitive data
5. Timeout protection for large PSBTs

## Consequences

- Clean separation of concerns
- Easy testing with mock wrapper
- Clear upgrade path for Taproot
- Graceful degradation without Rust

## Decision

**Status:** Proposed  
**Next Step:** Review and accept API design before implementation
