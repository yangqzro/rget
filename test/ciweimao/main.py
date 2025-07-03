import json
from typing import List
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad  # 导入位置


class Base64:
    __PADCHAR = "="
    __ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    @classmethod
    def __from_char_code(cls, *codes: int) -> str:
        return "".join([chr(code) for code in codes])

    @classmethod
    def __get_byte64(cls, s: str, i: int) -> int:
        idx = cls.__ALPHA.find(s[i])
        if idx == -1:
            raise ValueError("cannot decode base64")
        return idx

    @classmethod
    def __get_byte(cls, s: str, i: int) -> int:
        x = ord(s[i])
        if x > 255:
            raise ValueError("invalid character")
        return x

    @classmethod
    def encode(cls, s: str) -> str:
        x, imax = [], len(s) - (len(s) % 3)

        if len(s) == 0:
            return s

        for i in range(0, imax, 3):
            b10 = (cls.__get_byte(s, i) << 16) | (cls.__get_byte(s, i + 1) << 8) | cls.__get_byte(s, i + 2)
            x.append(cls.__ALPHA[(b10 >> 18)])
            x.append(cls.__ALPHA[(b10 >> 12) & 63])
            x.append(cls.__ALPHA[(b10 >> 6) & 63])
            x.append(cls.__ALPHA[b10 & 63])

        if len(s) - imax == 1:
            b10 = cls.__get_byte(s, i) << 16
            x.append(cls.__ALPHA[b10 >> 18] + cls.__ALPHA[(b10 >> 12) & 63] + cls.__PADCHAR + cls.__PADCHAR)
        elif len(s) - imax == 2:
            b10 = cls.__get_byte(s, i) << 16 | cls.__get_byte(s, i + 1) << 8
            x.append(cls.__ALPHA[b10 >> 18] + cls.__ALPHA[(b10 >> 12) & 63] + cls.__ALPHA[(b10 >> 6) & 63] +cls.__PADCHAR)

        return "".join(x)

    @classmethod
    def decode(cls, s: str) -> str:
        pads, imax, x = 0, len(s), []

        if imax == 0:
            return s
        if imax % 4 != 0:
            raise ValueError("cannot decode base64")
        if s[imax - 1] == cls.__PADCHAR:
            pads = 1
            if s[imax - 2] == cls.__PADCHAR:
                pads = 2
            imax -= 4

        for i in range(0, imax, 4):
            b10 = (
                cls.__get_byte64(s, i) << 18
                | cls.__get_byte64(s, i + 1) << 12
                | cls.__get_byte64(s, i + 2) << 6
                | cls.__get_byte64(s, i + 3)
            )
            x.append(cls.__from_char_code(b10 >> 16, (b10 >> 8) & 0xFF, b10 & 0xFF))

        if pads == 1:
            b10 = cls.__get_byte64(s, i) << 18 | cls.__get_byte64(s, i + 1) << 12 | cls.__get_byte64(s, i + 2) << 6
            x.append(cls.__from_char_code(b10 >> 16, (b10 >> 8) & 0xFF))
        elif pads == 2:
            b10 = cls.__get_byte64(s, i) << 18 | cls.__get_byte64(s, i + 1) << 12
            x.append(cls.__from_char_code(b10 >> 16))

        return "".join(x)


def decrypt(content: str = "", keys: List[str] = [], access_key: str = ""):
    t = len(keys)
    k = [keys[ord(access_key[-1]) % t], keys[ord(access_key[0]) % t]]
    for i in range(len(k)):
        n = Base64.decode(content)
        p = k[i]
        j = Base64.encode(n[0:16])
        f = Base64.encode(n[16:])
    return "hello world"


if __name__ == "__main__":
    with open("test/ciweimao/testdata.json", "r", encoding="utf-8") as file:
        data: dict = json.load(file)
        print(decrypt(data.get("content"), data.get("keys"), data.get("accessKey")))
