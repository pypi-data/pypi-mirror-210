#
# voice-skill-sdk
#
# (C) 2022, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#


import base64
import json
import logging
from typing import Any, Dict

from skill_sdk.intents import r
from skill_sdk.config import settings
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)


class ServiceTokenDecryption:
    """
    Utility class responsible for decrypting the cv service-token.

    NOTE :: Please do not store the user related token claims
            in any permanent persistence storage due to GDR compliance issues.
            Currently there is not any existing mechanism for cleaning up any user related data.
    """

    def __init__(self, service_token: str = "", service_token_secret: str = "") -> None:
        self.service_token = service_token
        self.service_token_secret = service_token_secret

    def decrypt(self) -> Dict:
        """
        Verifies and decrypts the cvi service-token.
        Returns the claims of the token

        :param service_token: 
            The token that should be decrypted

        :param service_token_secret: 
            The secret to decrypt the service token

        :return:
            the claims of the token

        :Raises ValueError:
            if the MAC does not match. The message has been tampered with
            or the key is incorrect.
        """

        if len(self.service_token) == 0:
            e = ValueError("Service Token is empty")
            logger.error(e)
            raise e

        if len(self.service_token_secret) == 0:
            e = ValueError("Service Token Secret is empty")
            logger.error(e)
            raise e

        decoded_cvi_token: bytes = base64.b64decode(self.service_token)
        decoded_str = str(decoded_cvi_token, "utf-8")
        decoded_dict: dict = json.loads(decoded_str)
        decoded_nonce = base64.b64decode(str(decoded_dict.get("nonce")))
        decoded_encrypted_plain_token = base64.b64decode(
            str(decoded_dict.get("encryptedPlainToken"))
        )
        decoded_secret: bytes = base64.b64decode(self.service_token_secret)

        cipher: Any = AES.new(key=decoded_secret, mode=AES.MODE_GCM, nonce=decoded_nonce)   # Setup cipher
        # https://docs.python.org/3/library/typing.html#the-any-type
        # Prevent mypy to miss judge the return value of the AES.new method by making sure the object will be marked as Any

        # Raw data structure for encryptedPlainToken crypttext[:-16] + auth_tag[-16:] aka default cipher.block_size
        decoded_cipher_text = decoded_encrypted_plain_token[: -cipher.block_size]
        decoded_auth_tag = decoded_encrypted_plain_token[-cipher.block_size :]
        try:
            plaintext = cipher.decrypt_and_verify(
                decoded_cipher_text,
                decoded_auth_tag,
            )
            logger.debug(str(plaintext, "utf-8"))
        except ValueError as e:
            logger.error(e)
            raise e
        token_data = json.loads(str(plaintext, "utf-8"))
        
        return token_data
