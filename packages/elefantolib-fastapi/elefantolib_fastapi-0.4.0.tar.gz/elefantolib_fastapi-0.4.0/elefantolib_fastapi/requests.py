from elefantolib.context import AsyncPlatformContext

from fastapi import requests


class Request(requests.Request):

    @property
    def pfm(self) -> AsyncPlatformContext:
        return self.scope['pfm']
