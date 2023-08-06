from elefantolib.context import AsyncPlatformContext

from fastapi import requests

from redis.asyncio.client import Redis


class Request(requests.Request):

    @property
    def pfm(self) -> AsyncPlatformContext:
        pfm = self.scope['pfm']
        pfm.validate()
        return pfm

    @property
    def redis(self) -> Redis:
        return self.scope.get('redis')
