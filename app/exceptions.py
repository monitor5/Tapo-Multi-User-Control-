from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class PlugNotFoundException(BaseAPIException):
    def __init__(self, plug_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plug '{plug_name}' not found"
        )

class PlugAlreadyInUseException(BaseAPIException):
    def __init__(self, plug_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Plug '{plug_name}' is already in use"
        )

class PlugNotInUseException(BaseAPIException):
    def __init__(self, plug_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plug '{plug_name}' is not in use"
        )

class TapoConnectionException(BaseAPIException):
    def __init__(self, plug_name: str, error: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to plug '{plug_name}': {error}"
        ) 