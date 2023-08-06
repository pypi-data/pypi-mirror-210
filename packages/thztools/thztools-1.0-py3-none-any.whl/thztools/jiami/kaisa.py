def jiami(plaintext, shift):
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
def jiemi(ciphertext, shift):
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