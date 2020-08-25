# serializing and deserializing
# source: https://repl.it/@KevinLu2/ArcticUnsightlyTaskscheduling#main.py
from string import ascii_letters, digits


# non-translating characters
ALPHANUMERIC_SET = set(ascii_letters + digits)
# mapping all bytes to themselves, except '_' maps to '\' and '.' maps to '/'
ESCAPE_CHAR_DECODE_TABLE = bytes(bytearray(range(256)).replace(b"_", b"\\")).replace(
    b".", b"/"
)
# reverse mapping -- maps `\` back to `_`
ESCAPE_CHAR_ENCODE_TABLE = bytes(bytearray(range(256)).replace(b"\\", b"_")).replace(
    b"/", b"."
)
# encoding table for ASCII characters not in ALPHANUMERIC_SET
ASCII_ENCODE_TABLE = {
    i: u"_x{:x}".format(i) for i in set(range(128)) ^ set(map(ord, ALPHANUMERIC_SET))
}
ASCII_ENCODE_TABLE[47] = "."  # '/'='.'


def encode(s):
    s = s.translate(ASCII_ENCODE_TABLE)
    bytes_ = s.encode("unicode-escape")
    bytes_ = bytes_.decode("ascii")
    bytes_ = bytes_.translate(ESCAPE_CHAR_ENCODE_TABLE)
    return bytes_


def decode(s):
    s = s.encode("ascii")
    s = s.translate(ESCAPE_CHAR_DECODE_TABLE)
    return s.decode("unicode-escape")


if __name__ == "__main__":
    # s = u"Random UTF-8/ String ☑⚠⚡"
    s = "/"
    # s = "北亰/"
    print(s)
    b = encode(s)
    print(b)
    new_s = decode(b)
    print(new_s)
