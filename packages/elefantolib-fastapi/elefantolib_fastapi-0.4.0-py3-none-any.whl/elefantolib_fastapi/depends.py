from typing import Annotated, NamedTuple

from elefantolib_fastapi import exceptions
from elefantolib_fastapi.requests import Request

from fastapi import HTTPException, Header, status


class CommonHeaders(NamedTuple):
    auth_token: Annotated[str, Header(alias='Authorization')]
    correlation_id: Annotated[str, Header(alias='X-Correlation-Id')]
    locale: Annotated[str, Header(alias='Accept-Language')]


def request_depend(request: Request):
    try:
        request.pfm.validate()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def is_authenticated(request: Request):
    if not request.pfm.user.is_authenticated():
        raise exceptions.Unauthorized
