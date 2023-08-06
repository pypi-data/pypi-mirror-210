import sys
import crypto
sys.modules['Crypto'] = crypto
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


def md5_fp(text: str):
    return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()


class Aes:
    def __init__(self, block_size=16):
        """
        :param block_size: 填充的块大小，默认为16，有些是8
        """
        self.__block_size = block_size

        self.__modes = {
            'CBC': AES.MODE_CBC,
            'ECB': AES.MODE_ECB
        }
        self.__padding_s = {
            'pkcs7': self.__pkcs7padding,
            'pkcs5': self.__pkcs5padding,
            'zero': self.__zeropadding,
        }

    def __pkcs7padding(self, plaintext):
        """
        明文使用PKCS7填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(block_size - len_plaintext % block_size) * (block_size - len_plaintext % block_size)

    def __pkcs5padding(self, plaintext):
        """
        PKCS5Padding 的填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(block_size - len_plaintext % block_size) * (block_size - len_plaintext % block_size)

    def __zeropadding(self, plaintext):
        """
        zeropadding 的填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(0) * (block_size - len_plaintext % block_size)

    @staticmethod
    def __unpad(plaintext):
        pad_ = ord(plaintext[-1])
        return plaintext[:-pad_]

    def aes_encrypt(self, padding: str, plaintext: str, key: str, mode: str, iv=None, *args):
        """
        :param padding: 填充方式,
        :param plaintext: 明文
        :param key:
        :param mode:
        :param iv:
        :param args: 跟AES.new 的参数一样
        :return:
        """
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        if mode == 'ECB':
            aes = AES.new(key, self.__modes[mode], *args)
        else:
            aes = AES.new(key, self.__modes[mode], iv, *args)
        content_padding = self.__padding_s[padding](plaintext)  # 处理明文, 填充方式
        encrypt_bytes = aes.encrypt(content_padding.encode('utf-8'))  # 加密
        return str(base64.b64encode(encrypt_bytes), encoding='utf-8')  # 重新编码

    def aes_decrypt(self, padding: str, ciphertext: str, key: str, mode: str, iv=None, *args):
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        if mode == 'ECB':
            aes = AES.new(key, self.__modes[mode], *args)
        else:
            aes = AES.new(key, self.__modes[mode], iv, *args)
        ciphertext = base64.b64decode(ciphertext)
        plaintext = aes.decrypt(ciphertext).decode('utf-8')
        if padding == 'zero':
            return plaintext
        return self.__unpad(plaintext)


class Des:
    def __init__(self, block_size=16):
        """
        :param block_size: 填充的块大小，默认为16，有些是8
        """
        self.__block_size = block_size
        self.__modes = {
            'CBC': DES.MODE_CBC,
            'ECB': DES.MODE_ECB
        }
        self.__padding_s = {
            'pkcs7': self.__pkcs7padding,
            'pkcs5': self.__pkcs5padding,
            'zero': self.__zeropadding,
        }

    def __pkcs7padding(self, plaintext):
        """
        明文使用PKCS7填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(block_size - len_plaintext % block_size) * (block_size - len_plaintext % block_size)

    def __pkcs5padding(self, plaintext):
        """
        PKCS5Padding 的填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(block_size - len_plaintext % block_size) * (block_size - len_plaintext % block_size)

    def __zeropadding(self, plaintext):
        """
        zeropadding 的填充
        :param plaintext: 明文
        """
        block_size = self.__block_size

        text_length = len(plaintext)
        bytes_length = len(plaintext.encode('utf-8'))
        len_plaintext = text_length if (bytes_length == text_length) else bytes_length
        return plaintext + chr(0) * (block_size - len_plaintext % block_size)

    @staticmethod
    def __unpad(plaintext):
        pad_ = ord(plaintext[-1])
        return plaintext[:-pad_]

    def des_encrypt(self, padding: str, plaintext: str, key: str, mode: str, iv=None, *args):
        """
        :param padding: 填充方式,
        :param plaintext: 明文
        :param key:
        :param mode:
        :param iv:
        :param args: 跟DES.new 的参数一样
        :return:
        """
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        if mode == 'ECB':
            des = DES.new(key, self.__modes[mode], *args)
        else:
            des = DES.new(key, self.__modes[mode], iv, *args)
        content_padding = self.__padding_s[padding](plaintext)  # 处理明文, 填充方式
        encrypt_bytes = des.encrypt(content_padding.encode('utf-8'))  # 加密
        return str(base64.b64encode(encrypt_bytes), encoding='utf-8')  # 重新编码

    def des_decrypt(self, padding: str, ciphertext: str, key: str, mode: str, iv=None, *args):
        key = key.encode('utf-8')
        #iv = iv.encode('utf-8')
        if mode == 'ECB':
            des = DES.new(key, self.__modes[mode], *args)
        else:
            des = DES.new(key, self.__modes[mode], iv, *args)
        ciphertext = base64.b64decode(ciphertext)
        plaintext = des.decrypt(ciphertext).decode('utf-8')
        if padding == 'zero':
            return plaintext
        return self.__unpad(plaintext)


if __name__ == '__main__':
    def aes():
        key_ = 'v4dj1g1lfekof8sz'
        #iv_ = 'hs2s8eop6pn6cf89'

        plaintext_ = 'captchaSn=Cgp6dC5jYXB0Y2hhEq0CHiCn1lzbV1vue2VbxZIkkKn'
        a = Aes(block_size=16)
        ciphertext_ = a.aes_encrypt('pkcs5', plaintext_, key_, 'CBC', iv_)
        plaintext_ = a.aes_decrypt('pkcs5', ciphertext_, key_, 'CBC', iv_)
        print("加密:", ciphertext_)
        print("解密:", plaintext_)

        ciphertext_ = a.aes_encrypt('pkcs5', plaintext_, key_, 'ECB', iv_)
        plaintext_ = a.aes_decrypt('pkcs5', ciphertext_, key_, 'ECB', iv_)
        print("加密:", ciphertext_)
        print("解密:", plaintext_)

    aes()