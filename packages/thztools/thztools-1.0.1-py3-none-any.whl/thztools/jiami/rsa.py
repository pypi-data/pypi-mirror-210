import rsa
def newkeys(length : int = 1024):
    """
    生成一个rsa密钥对，默认为1024位
    :param length : int,长度，默认为1024
    :return 公钥,私钥
    """
    (gongyao,siyao) = rsa.newkeys(length)
    return gongyao,siyao
def jiami(gongyao,text) -> bytes:
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
def jiemi(siyao,miwen:bytes):
    """
    使用rsa算法进行解密
    Args:
        siyao : rsa私钥
        miwen : 密文（bytes字节流）
    Return:
        明文
    """
    return rsa.decrypt(miwen, siyao).decode()
def sign(siyao,text):
    """
    使用rsa算法进行数字签名
    :param siyao:rsa私钥
    :param text:欲签名文本
    :return 返回签名文本
    """
    qianminwenben = rsa.sign(text.encode(),siyao,'SHA-1')
    return qianminwenben
def qmyz(text,qmwb,gongyao):
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