"""
Security utilities
Password hashing and verification
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해싱된 비밀번호
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        password: 평문 비밀번호
        hashed_password: 해싱된 비밀번호

    Returns:
        bool: 일치하면 True
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
