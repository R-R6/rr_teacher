"""Helpers for admin console access checks and payload shaping."""


def mask_db_host(host: str | None) -> str:
    value = (host or "").strip()
    if not value:
        return ""
    if value in {"127.0.0.1", "localhost", "mysql"}:
        return value
    if len(value) <= 8:
        return value[:2] + "***"
    return f"{value[:6]}...{value[-8:]}"


def parse_admin_csv(value: str | None) -> set[str]:
    return {item.strip() for item in (value or "").split(",") if item.strip()}


def is_admin_user(user, admin_user_ids: set[str], admin_usernames: set[str]) -> bool:
    return bool(
        user
        and (
            getattr(user, "id", None) in admin_user_ids
            or getattr(user, "username", None) in admin_usernames
        )
    )


def build_system_status_payload(settings, health_status: str, question_count: int, user_count: int) -> dict:
    cos_enabled = bool(settings.COS_SECRET_ID and settings.COS_BUCKET)
    return {
        "health": health_status,
        "database": {
            "type": settings.DB_TYPE,
            "name": getattr(settings, "DB_NAME", "") or "",
            "host_masked": mask_db_host(getattr(settings, "DB_HOST", "")),
        },
        "storage": {
            "mode": "cos" if cos_enabled else "local",
            "bucket": settings.COS_BUCKET if cos_enabled else "",
        },
        "ocr": {
            "default_engine": settings.OCR_DEFAULT_ENGINE,
        },
        "runtime": {
            "debug": settings.DEBUG,
            "swagger_enabled": settings.SWAGGER_ENABLED,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "login_rate_limit": settings.LOGIN_RATE_LIMIT,
            "question_count": question_count,
            "user_count": user_count,
        },
    }
