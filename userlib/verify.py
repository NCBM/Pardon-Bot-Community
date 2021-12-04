import os
import time
from random import choice
from typing import Optional
from .paths import VERIFY_DIR

# 声明验证码取字范围
chars = "ABDEFGHJKLMNPQRTUYabdefghjkmnpqrty123456789"

EXPIRE_LIMIT_MINUTE = 5


def gen_code(length: int = 4) -> str:
    code = ""
    for _ in range(length):
        code += choice(chars)
    return code


def uid2fp(gid: int, uid: int) -> str:
    return f"{VERIFY_DIR}/{gid}/{uid}"


def save_vcode(gid: int, uid: int, code: str) -> None:
    os.makedirs(f"{VERIFY_DIR}/{gid}", exist_ok=True)
    with open(uid2fp(gid, uid), "w") as f:
        f.write(code)


def read_vcode(cfp: str) -> Optional[str]:
    if os.path.exists(cfp):
        with open(cfp, "r") as f:
            return f.read()
    else:
        return None


def check_code_expired(cfp: str) -> int:
    T = time.time() - os.path.getmtime(cfp)
    return T > EXPIRE_LIMIT_MINUTE * 60


def verifiable(gid: int) -> bool:
    with open(f"{VERIFY_DIR}/in_verify", "r") as f:
        data = f.read().split("\n")
    return str(gid) in data
