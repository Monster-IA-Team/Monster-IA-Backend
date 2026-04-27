from datetime import datetime, timezone

def mark_as_deleted(value: str) -> str:
    return f"DELETED_{value}_{datetime.now(timezone.utc).microsecond}"