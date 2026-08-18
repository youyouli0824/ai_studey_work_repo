"""
安全工具模块:密码哈希 + 登录 token(签名)。
使用标准库 hashlib/hmac 实现,不依赖第三方包。
"""
import hashlib
import hmac
import base64
import os
import json
import time

# ---------- 密码哈希(PBKDF2) ----------

_PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """生成密码哈希,格式: pbkdf2$迭代次数$盐hex$哈希hex"""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2${_PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码是否与存储的哈希匹配"""
    try:
        _, iters, salt_hex, hash_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# ---------- 登录 token(HMAC 签名,无状态) ----------

_SECRET = os.environ.get("APP_TOKEN_SECRET") or "staff-chat-dev-secret-2026"
_TOKEN_TTL = 7 * 24 * 3600  # 7 天有效期


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def create_token(employee_id) -> str:
    """生成签名 token: base64(payload).签名"""
    payload = {"uid": int(employee_id), "exp": int(time.time()) + _TOKEN_TTL}
    raw = _b64url(json.dumps(payload).encode("utf-8"))
    sig = hmac.new(_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def verify_token(token: str):
    """校验 token,有效返回员工ID,否则返回 None"""
    try:
        raw, sig = token.split(".")
        expect = hmac.new(_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expect):
            return None
        payload = json.loads(_b64url_decode(raw))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("uid")
    except Exception:
        return None
