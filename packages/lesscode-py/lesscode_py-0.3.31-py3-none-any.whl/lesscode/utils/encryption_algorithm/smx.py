import importlib


class SMX:
    @staticmethod
    def generate_sm2_key():
        try:
            smx_sm2 = importlib.import_module("pysmx.SM2")
        except ImportError as e:
            raise Exception(f"snowland-smx is not exist,run:pip install snowland-smx==0.3.1")
        pk, sk = smx_sm2.generate_keypair()
        return {"pk": pk, "sk": sk}

    @staticmethod
    def generate_sm2_sign(string: str, DA, k, len_para, Hexstr=0, encoding="utf-8"):
        try:
            smx_sm2 = importlib.import_module("pysmx.SM2")
        except ImportError as e:
            raise Exception(f"snowland-smx is not exist,run:pip install snowland-smx==0.3.1")
        return smx_sm2.Sign(string, DA, k, len_para, Hexstr=Hexstr, encoding=encoding)

    @staticmethod
    def verify_sm2_sign(sign, string: str, PA, len_para, Hexstr=0, encoding="utf-8"):
        try:
            smx_sm2 = importlib.import_module("pysmx.SM2")
        except ImportError as e:
            raise Exception(f"snowland-smx is not exist,run:pip install snowland-smx==0.3.1")
        return smx_sm2.Verify(sign, string, PA, len_para, Hexstr=Hexstr, encoding=encoding)

    @staticmethod
    def encrypt(string: str, **kwargs):
        try:
            smx_sm2 = importlib.import_module("pysmx.SM2")
            smx_sm3 = importlib.import_module("pysmx.SM3")
            smx_sm4 = importlib.import_module("pysmx.SM4")
        except ImportError as e:
            raise Exception(f"snowland-smx is not exist,run:pip install snowland-smx==0.3.1")
        encrypt_type = kwargs.get("encrypt_type")
        encryption_algorithm = ["SM2", "SM3", "SM4"]
        encrypt_string = ""
        if encrypt_type in ["SM2", "SM3", "SM4"]:
            if encrypt_type == "SM2":
                encrypt_string = smx_sm2.Encrypt(string.encode(kwargs.get("encoding", "utf-8")), kwargs.get("pk"),
                                                 kwargs.get("len_para"),
                                                 kwargs.get("Hexstr", 0), kwargs.get("encoding", "utf-8"),
                                                 kwargs.get("hash_algorithm", "sm3"))
            elif encrypt_type == "SM3":
                sm3 = smx_sm3.SM3()
                sm3.update(string)
                encrypt_string = sm3.hexdigest()
            elif encrypt_type == "SM4":
                sm4 = smx_sm4.Sm4()
                sm4.sm4_set_key(kwargs.get("key_data"), kwargs.get("mode"))
                encrypt_string = sm4.sm4_crypt_ecb()
        else:
            raise Exception(
                f"{encrypt_type} is unsupported SMX algorithm,supported algorithm have {encryption_algorithm}")
        return encrypt_string

    @staticmethod
    def decrypt(string: str, **kwargs):
        try:
            smx_sm2 = importlib.import_module("pysmx.SM2")
            smx_sm4 = importlib.import_module("pysmx.SM4")
        except ImportError as e:
            raise Exception(f"snowland-smx is not exist,run:pip install snowland-smx==0.3.1")
        decrypt_type = kwargs.get("encrypt_type")
        decrypt_algorithm = ["SM2", "SM3", "SM4"]
        decrypt_string = ""
        if decrypt_type in ["SM2", "SM3", "SM4"]:
            if decrypt_type == "SM2":
                decrypt_string = smx_sm2.Decrypt(string, kwargs.get("sk"), kwargs.get("len_para"),
                                                 kwargs.get("Hexstr", 0),
                                                 kwargs.get("encoding", "utf-8"), kwargs.get("hash_algorithm", "sm3"))
            elif decrypt_type == "SM4":
                sm4 = smx_sm4.Sm4()
                sm4.sm4_set_key(kwargs.get("key_data"), kwargs.get("mode"))
                decrypt_string = sm4.sm4_crypt_ecb(string)

        else:
            raise Exception(f"{decrypt_type} is unsupported SMX algorithm,supported algorithm have {decrypt_algorithm}")
        return decrypt_string
