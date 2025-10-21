"""
ID Generator Utilities
Generate unique IDs for various resources
"""
import uuid


def generate_id(prefix: str = "", length: int = 12) -> str:
    """
    고유 ID 생성

    Args:
        prefix: ID 접두사 (예: "U_", "WS_")
        length: UUID 부분의 길이 (기본: 12)

    Returns:
        str: 생성된 ID

    Examples:
        >>> generate_id("U_", 8)
        'U_a1b2c3d4'
        >>> generate_id("WS_", 12)
        'WS_a1b2c3d4e5f6'
    """
    uuid_hex = uuid.uuid4().hex[:length]
    return f"{prefix}{uuid_hex}"


def generate_user_id() -> str:
    """User ID 생성 (U_ + 10자리)"""
    return generate_id("U_", 10)


def generate_workspace_id() -> str:
    """Workspace ID 생성 (WS_ + 10자리)"""
    return generate_id("WS_", 10)


def generate_workspace_member_id() -> str:
    """WorkspaceMember ID 생성 (WM_ + 10자리)"""
    return generate_id("WM_", 10)


def generate_template_id() -> str:
    """CrewTemplate ID 생성 (TPL_ + 9자리)"""
    return generate_id("TPL_", 9)


def generate_favorite_id() -> str:
    """TemplateFavorite ID 생성 (FAV_ + 9자리)"""
    return generate_id("FAV_", 9)
