import base64
import binascii
import importlib


class DES:
    @staticmethod
    def encrypt(text: str, key: str, mode=1):
        try:
            Des = importlib.import_module("Cryptodome.Cipher.DES")
        except ImportError as e:
            raise Exception(f"pycryptodomex is not exist,run:pip install pycryptodomex==3.17")
        text = str(text)
        des = Des.new(DES.pad(key), mode)
        encrypt_aes = des.encrypt(DES.pad(text))
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        return bytes.decode(binascii.b2a_hex(bytes(encrypted_text, encoding="utf8")))

    @staticmethod
    def decrypt(text: str, key: str, mode=1):
        try:
            Des = importlib.import_module("Cryptodome.Cipher.DES")
        except ImportError as e:
            raise Exception(f"pycryptodomex is not exist,run:pip install pycryptodomex==3.17")
        text = bytes.decode(binascii.a2b_hex(bytes(text, encoding="utf8")))
        des = Des.new(DES.pad(key), mode)
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        decrypted_text = des.decrypt(base64_decrypted).decode(encoding='utf-8')
        return decrypted_text.replace("\0", "")

    @staticmethod
    def pad(value):
        """
        :param value: 待处理的数据
        """
        while len(value) % 8 != 0:
            value += '\0'
        return str.encode(value)
