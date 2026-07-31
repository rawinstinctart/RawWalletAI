"""Configuration management."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class WalletSettings(BaseModel):
    """Wallet configuration settings."""

    name: str = Field(default="default")
    network: str = Field(default="bitcoin")
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".rawwalletai")
    passphrase: str | None = Field(default=None)
    fee_rate: int = Field(default=2, ge=1, description="satoshis per byte")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def model_post_init(self, __context: object) -> None:
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "wallets").mkdir(exist_ok=True)
