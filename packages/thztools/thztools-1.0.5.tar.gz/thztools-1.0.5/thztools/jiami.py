from Crypto.Cipher import AES as AESclass
from Crypto.Random import get_random_bytes
import rsa
class KaiSa:
    def jiami(self,plaintext, shift):
        """
        凯撒加密算法
        plaintext: 明文
        shift: 偏移量
        """
        ciphertext = ''
        for char in plaintext:
            if char.isalpha():  # 只加密字母
                # 将字母转换成数字，A为65，a为97，因此需要减去相应的值
                num = ord(char)
                if char.isupper():  # 大写字母
                    num = (num - 65 + shift) % 26 + 65
                else:  # 小写字母
                    num = (num - 97 + shift) % 26 + 97
                # 将数字转换回字母
                char = chr(num)
            ciphertext += char
        return ciphertext
    def jiemi(self,ciphertext, shift):
        """
        凯撒解密算法
        ciphertext: 密文
        shift: 偏移量(加密时的偏移量)
        """
        plaintext = ''
        for char in ciphertext:
            if char.isalpha():  # 只解密字母
                num = ord(char)
                if char.isupper():  # 大写字母
                    num = (num - 65 - shift) % 26 + 65
                else:  # 小写字母
                    num = (num - 97 - shift) % 26 + 97
                char = chr(num)
            plaintext += char
        return plaintext
class RSA:
    def newkeys(self,length : int = 1024):
        """
        生成一个rsa密钥对，默认为1024位
        :param length : int,长度，默认为1024
        :return 公钥,私钥
        """
        (gongyao,siyao) = rsa.newkeys(length)
        return gongyao,siyao
    def jiami(self,gongyao,text) -> bytes:
        """
        使用rsa算法进行加密
        Args:
            gongyao : rsa 公钥
            text : 欲加密文本
        Return:
            返回密文(bytes流)
        """
        message = text.encode()
        miwen = rsa.encrypt(message, gongyao)
        return miwen
    def jiemi(self,siyao,miwen:bytes):
        """
        使用rsa算法进行解密
        Args:
            siyao : rsa私钥
            miwen : 密文（bytes字节流）
        Return:
            明文
        """
        return rsa.decrypt(miwen, siyao).decode()
    def sign(self,siyao,text):
        """
        使用rsa算法进行数字签名
        :param siyao:rsa私钥
        :param text:欲签名文本
        :return 返回签名文本
        """
        qianminwenben = rsa.sign(text.encode(),siyao,'SHA-1')
        return qianminwenben
    def qmyz(self,text,qmwb,gongyao):
        """
        签名验证
        :param text:被验证的文本
        :param qmwb:签名文本，sign()函数的返回值
        :param gongyao:rsa公钥
        :return 成功返回True，失败返回False
        """
        res = rsa.verify(text.encode(),qmwb,gongyao)
        if res:
            return True
        else:
            return False
class AES:
    def newkey(self):
        """
        自动生成32位（256位）AES秘钥
        """
        key = get_random_bytes(32)
        return key

    def jiami(self,plaintext, key):
        """
        AES加密算法
        plaintext: 明文
        key: 秘钥
        Returns:
            密文,随机数，验证标签，均为bytes类型
        """
        # 用秘钥创建一个AES对象
        cipher = AESclass.new(key, AESclass.MODE_EAX)
        # 加密明文
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        # 返回加密后的密文和必要的参数
        return ciphertext, cipher.nonce, tag

    def jiemi(self,ciphertext, key, nonce, tag):
        """
        AES解密算法
        ciphertext: 密文
        key: 秘钥
        nonce: 加密时生成的随机数
        tag: 加密时生成的验证标签
        """
        # 用密钥和随机数创建一个AES对象
        cipher = AESclass.new(key, AESclass.MODE_EAX, nonce=nonce)
        try:
            # 解密密文
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode('utf-8')
        except:
            return None
class Weijiniya:
    def jiami(self,plaintext, key):
        """
        使用维吉尼亚密码加密明文字符串

        参数:
            plaintext (str): 明文字符串
            key (str): 加密秘钥，只能包含小写字母

        返回:
            str: 密文字符串
        """
        ciphertext = ""
        key_index = 0
        for c in plaintext:
            if c.isalpha():
                # 计算每个字符的移位量
                shift = ord(key[key_index % len(key)]) - ord('a')
                # 对字符进行移位并加入密文字符串中
                shifted_char = chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
                ciphertext += shifted_char
                key_index += 1
            else:
                # 非字母字符直接加入密文字符串中
                ciphertext += c
        return ciphertext

    def jiemi(self,ciphertext, key):
        """
        使用维吉尼亚密码解密密文字符串

        参数:
            ciphertext (str): 密文字符串
            key (str): 解密秘钥，只能包含小写字母

        返回:
            str: 明文字符串
        """
        plaintext = ""
        key_index = 0
        for c in ciphertext:
            if c.isalpha():
                # 计算每个字符的移位量
                shift = ord(key[key_index % len(key)]) - ord('a')
                # 对字符进行反向移位并加入明文字符串中
                shifted_char = chr((ord(c) - ord('a') - shift + 26) % 26 + ord('a'))
                plaintext += shifted_char
                key_index += 1
            else:
                # 非字母字符直接加入明文字符串中
                plaintext += c
        return plaintext