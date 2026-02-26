from abc import ABC, abstractmethod
from typing import Any


class cipher(ABC):
    """
    Abstract base class for ciphers.
    """

    @abstractmethod
    def encrypt(self, plaintext: str) -> Any:
        """
        Encrypts the given plaintext.
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str) -> Any:
        """
        Decrypts the given ciphertext.
        """
        pass

    @abstractmethod
    def setConfig(self, newConf: dict) -> None:
        """
        Sets the configuration for the cipher.
        """
        pass