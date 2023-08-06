from typing import Any

from fastapi import HTTPException, status


class Unauthorized(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'Unauthorized',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
