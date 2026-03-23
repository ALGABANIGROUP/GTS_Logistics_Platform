from fastapi import HTTPException, status


def ai_forbidden(error: str, bot: str, **details) -> HTTPException:
    payload = {"error": error, "bot": bot, **details}
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=payload)
