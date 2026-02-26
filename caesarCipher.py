# caesarCipher.py
from cipher import cipher


class caesarCipher(cipher):
    """
    Caesar cipher implementation.

    Supported config keys:
        - shift (int)
        - alphabet (str)
        - preserve_nonalpha (bool, optional, default=True)
    """

    def __init__(self):
        self._conf = {
            'shift': 1,
            'alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'preserve_nonalpha': True
        }

    def setConfig(self, newConf) -> None:
        """
        Validates and sets cipher configuration.
        """
        if not isinstance(newConf, dict):
            raise ValueError("Configuration must be a dictionary.")

        if 'shift' not in newConf or 'alphabet' not in newConf:
            raise ValueError("Configuration must include 'shift' and 'alphabet'.")

        shift = newConf['shift']
        alphabet = newConf['alphabet']
        preserve_nonalpha = newConf.get('preserve_nonalpha', True)

        if not isinstance(shift, int):
            raise ValueError("Shift must be an integer.")

        if not isinstance(alphabet, str) or len(alphabet) == 0:
            raise ValueError("Alphabet must be a non-empty string.")

        if len(set(alphabet)) != len(alphabet):
            raise ValueError("Alphabet must not contain duplicate characters.")

        if not isinstance(preserve_nonalpha, bool):
            raise ValueError("'preserve_nonalpha' must be a boolean.")

        shift = shift % len(alphabet)

        self._conf = {
            'shift': shift,
            'alphabet': alphabet,
            'preserve_nonalpha': preserve_nonalpha
        }

    def encrypt(self, text: str) -> str:
        """
        Encrypts text using the configured Caesar shift.
        """
        alphabet = self._conf['alphabet']
        alphabet_size = len(alphabet)
        shift = self._conf['shift']
        preserve_nonalpha = self._conf['preserve_nonalpha']

        result = ""
        text = text.lower().strip()

        for char in text:
            if char in alphabet:
                index = alphabet.index(char)
                new_index = (index + shift) % alphabet_size
                result += alphabet[new_index]
            else:
                if preserve_nonalpha:
                    result += char
                else:
                    raise ValueError(f"Character '{char}' not in alphabet.")

        return result

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypts text using the configured Caesar shift.
        """
        alphabet = self._conf['alphabet']
        alphabet_size = len(alphabet)
        shift = self._conf['shift']
        preserve_nonalpha = self._conf['preserve_nonalpha']

        result = ""
        ciphertext = ciphertext.lower().strip()

        for char in ciphertext:
            if char in alphabet:
                index = alphabet.index(char)
                new_index = (index - shift) % alphabet_size
                result += alphabet[new_index]
            else:
                if preserve_nonalpha:
                    result += char
                else:
                    raise ValueError(f"Character '{char}' not in alphabet.")

        return result