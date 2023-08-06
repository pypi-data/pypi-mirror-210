from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def newkey():
    """
    自动生成32位（256位）AES秘钥
    """
    key = get_random_bytes(32)
    return key

def jiami(plaintext, key):
    """
    AES加密算法
    plaintext: 明文
    key: 秘钥
    Returns:
        密文,随机数，验证标签，均为bytes类型
    """
    # 用秘钥创建一个AES对象
    cipher = AES.new(key, AES.MODE_EAX)
    # 加密明文
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    # 返回加密后的密文和必要的参数
    return ciphertext, cipher.nonce, tag

def jiemi(ciphertext, key, nonce, tag):
    """
    AES解密算法
    ciphertext: 密文
    key: 秘钥
    nonce: 加密时生成的随机数
    tag: 加密时生成的验证标签
    """
    # 用密钥和随机数创建一个AES对象
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        # 解密密文
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')
    except:
        return None