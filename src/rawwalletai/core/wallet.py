"""Wallet instance management."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from rawwalletai.chains.bitcoin import BitcoinAddress, BitcoinChain
from rawwalletai.core.keys import KeyManager
from rawwalletai.storage.encrypted import EncryptedStorage


@dataclass
class Wallet:
    wallet_id: str
    name: str
    network: str
    address: BitcoinAddress
    key_manager: KeyManager
    storage: EncryptedStorage


class WalletManager:
    """Manages wallet instances."""

    def __init__(
        self,
        key_manager: KeyManager,
        storage: EncryptedStorage,
        chain: BitcoinChain,
    ) -> None:
        self.key_manager = key_manager
        self.storage = storage
        self.chain = chain
        self._wallets: dict[str, Wallet] = {}

    def create_wallet(self, name: str, passphrase: str = "") -> Wallet:
        """Create a new wallet."""
        wallet_id = str(uuid.uuid4())
        mnemonic = self.key_manager.generate_mnemonic()
        self.key_manager.initialize_from_mnemonic(mnemonic, passphrase)

        master_private_key, master_chain_code = self.key_manager._master_key, self.key_manager._master_chain_code
        if master_private_key is None:
            raise RuntimeError("Master key not initialized")

        # For now derive a simple keypair from master key
        from rawwalletai.core.keys import KeyPair
        keypair = KeyPair(
            private_key_bytes=master_private_key,
            public_key_bytes=master_private_key,
            chain_code=master_chain_code or b"",
            address="",
            path="m/84'/0'/0'/0/0",
        )
        address = self.chain.generate_address(keypair.public_key_bytes, "p2wpkh")
        wallet = Wallet(
            wallet_id=wallet_id,
            name=name,
            network=self.chain.network,
            address=address,
            key_manager=self.key_manager,
            storage=self.storage,
        )
        self._wallets[wallet_id] = wallet
        self.storage.save(
            wallet_id,
            {
                "name": name,
                "network": self.chain.network,
                "mnemonic": mnemonic,
                "address": address.address,
                "script_type": address.script_type,
                "path": address.path or "",
            },
        )
        return wallet

    def load_wallet(self, wallet_id: str, passphrase: str = "") -> Wallet | None:
        """Load an existing wallet."""
        if wallet_id not in self._wallets:
            try:
                data = self.storage.load(wallet_id)
            except FileNotFoundError:
                return None
            mnemonic = data["mnemonic"]
            self.key_manager.initialize_from_mnemonic(mnemonic, passphrase)
            master_private_key, master_chain_code = self.key_manager._master_key, self.key_manager._master_chain_code
            if master_private_key is None:
                raise RuntimeError("Master key not initialized")
            from rawwalletai.core.keys import KeyPair
            keypair = KeyPair(
                private_key_bytes=master_private_key,
                public_key_bytes=master_private_key,
                chain_code=master_chain_code or b"",
                address=data["address"],
                path=data.get("path", ""),
            )
            address = BitcoinAddress(
                address=data["address"],
                script_type=data.get("script_type", "p2wpkh"),
                path=data.get("path"),
            )
            wallet = Wallet(
                wallet_id=wallet_id,
                name=data["name"],
                network=data["network"],
                address=address,
                key_manager=self.key_manager,
                storage=self.storage,
            )
            self._wallets[wallet_id] = wallet
            return wallet
        return self._wallets[wallet_id]
