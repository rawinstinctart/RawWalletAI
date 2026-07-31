"""ECDSA signing tests with known test vectors."""

from pathlib import Path

import pytest

from rawwalletai.transactions.signer import ECKey
from rawwalletai.transactions.signer_psbt import PSBTSigner
from rawwalletai.transactions.psbt import PSBT, PSBTInput, PSBTOutput


KNOWN_TEST_VECTOR = {
    "private_key": bytes([i % 256 for i in range(32)]),
    "message": b"Bitcoin test vector for ECDSA",
}


def test_ec_key_sign_verify() -> None:
    key = ECKey(KNOWN_TEST_VECTOR["private_key"])
    signature = key.sign(KNOWN_TEST_VECTOR["message"])
    assert key.verify(key.public_key_bytes(), KNOWN_TEST_VECTOR["message"], signature)


def test_ec_key_rejects_invalid_key_length() -> None:
    with pytest.raises(ValueError):
        ECKey(b"\x00" * 31)


def test_psbt_signer_invalid_key_length() -> None:
    signer = PSBTSigner()
    inp = PSBTInput(txid=b"\xab" * 32, vout=0, amount_sats=1000, script_pubkey=b"")
    out = PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")
    psbt = PSBT(inputs=[inp], outputs=[out])
    with pytest.raises(ValueError):
        signer.sign_psbt(psbt, b"\x00" * 31)


def test_psbt_signer_produces_signature() -> None:
    signer = PSBTSigner()
    inp = PSBTInput(txid=b"\xab" * 32, vout=0, amount_sats=1000, script_pubkey=b"")
    out = PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")
    psbt = PSBT(inputs=[inp], outputs=[out])
    psbt = signer.sign_psbt(psbt, KNOWN_TEST_VECTOR["private_key"])
    assert psbt.inputs[0].signature is not None
    assert len(psbt.inputs[0].signature) > 0


def test_psbt_signer_sets_public_key() -> None:
    signer = PSBTSigner()
    inp = PSBTInput(txid=b"\xab" * 32, vout=0, amount_sats=1000, script_pubkey=b"")
    out = PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")
    psbt = PSBT(inputs=[inp], outputs=[out])
    psbt = signer.sign_psbt(psbt, KNOWN_TEST_VECTOR["private_key"])
    assert psbt.inputs[0].public_key is not None
    assert len(psbt.inputs[0].public_key) == 33


def test_psbt_signer_sets_signed_flag() -> None:
    signer = PSBTSigner()
    inp = PSBTInput(txid=b"\xab" * 32, vout=0, amount_sats=1000, script_pubkey=b"")
    out = PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")
    psbt = PSBT(inputs=[inp], outputs=[out])
    assert not psbt._signed
    psbt = signer.sign_psbt(psbt, KNOWN_TEST_VECTOR["private_key"])
    assert psbt._signed


def test_psbt_signer_invalid_inputs_raise() -> None:
    signer = PSBTSigner()
    with pytest.raises(ValueError):
        signer.sign_psbt(PSBT(inputs=[], outputs=[PSBTOutput(address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", amount_sats=500, script_pubkey=b"")]), KNOWN_TEST_VECTOR["private_key"])


def test_ec_key_verify_invalid_signature() -> None:
    key = ECKey(KNOWN_TEST_VECTOR["private_key"])
    assert not ECKey.verify(key.public_key_bytes(), KNOWN_TEST_VECTOR["message"], b"\x00" * 32)
