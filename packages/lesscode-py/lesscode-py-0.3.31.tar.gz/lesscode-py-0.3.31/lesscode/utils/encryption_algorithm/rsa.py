import base64
import importlib


class RSA:
    @staticmethod
    def generate_key():
        try:
            Rsa = importlib.import_module("Cryptodome.PublicKey.RSA")
            Random = importlib.import_module("Cryptodome.Random")
        except ImportError as e:
            raise Exception(f"pycryptodomex is not exist,run:pip install pycryptodomex==3.17")
        _random_generator = Random.new().read
        # rsa算法生成实例
        _rsa = Rsa.generate(1024, _random_generator)
        # 私钥的生成
        _private_key = _rsa.exportKey()
        # 公钥的生成
        _public_key = _rsa.publickey().exportKey()
        key = {
            "private_key": _private_key,
            "public_key": _public_key
        }
        return key

    @staticmethod
    def encrypt(text: str, public_key: str, encoding='utf-8'):
        try:
            Rsa = importlib.import_module("Cryptodome.PublicKey.RSA")
            Cipher_pkcs1_v1_5 = importlib.import_module("Cryptodome.Cipher.PKCS1_v1_5")
        except ImportError as e:
            raise Exception(f"pycryptodomex is not exist,run:pip install pycryptodomex==3.17")
        rsa_key = Rsa.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        encrypt_string = base64.b64encode(cipher.encrypt(text.encode(encoding))).decode(encoding)
        return encrypt_string

    @staticmethod
    def decrypt(text: str, private_key: str, encoding='utf-8'):
        try:
            Rsa = importlib.import_module("Cryptodome.PublicKey.RSA")
            Cipher_pkcs1_v1_5 = importlib.import_module("Cryptodome.Cipher.PKCS1_v1_5")
        except ImportError as e:
            raise Exception(f"pycryptodomex is not exist,run:pip install pycryptodomex==3.17")
        rsa_key = Rsa.importKey(private_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        decrypt_string = cipher.decrypt(base64.b64decode(text.encode(encoding)), "解密失败").decode(encoding)
        return decrypt_string
