from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class AESCrypt:
    # 固定的 salt
    salt = b"\xd0\x18\xa7QM\xd6\x9b\xebxu\xe4\xed\xa8\x83\xf6\xa3/\x01\x9c\x9e\x86n\xda;\x10EdD\xf7\x932\xcc"

    def __init__(self, password):
        """
        建立 AESCrypt 實例
        """
        self.password = password
        # 根據密碼與 salt 產生金鑰
        self.key = self.generate_key()

    def generate_key(self):
        """
        根据密码与 salt 生成 PBKDF2 金鑰
        """
        key = PBKDF2(self.password, AESCrypt.salt, 32)
        return key

    def encrypt(self, data):
        """
        使用 AES 加密資料
        """
        # 建立加密器
        cipher = AES.new(self.key, AES.MODE_CTR)

        # 將資料加密
        ciphertext = cipher.encrypt(data)

        # 回傳加密後的資料與 nonce
        return (b64encode(ciphertext), b64encode(cipher.nonce))

    def decrypt(self, data):
        """
        使用 AES 解密資料
        """
        # 將傳入的資料解析為密文與 nonce
        ciphertext, nonce = b64decode(data[0]), b64decode(data[1])

        # 建立解密器
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)

        # 解密資料並回傳
        return cipher.decrypt(ciphertext)
