import logging

from elefantolib import logger_config
from elefantolib.http_client import BaseClient

import httpx


logger = logger_config.configure_logger(__name__)


class HttpxClient(BaseClient):

    def get(self, *args, **kwargs):
        return self._request(*args, method='get', **kwargs)

    def post(self, *args, **kwargs):
        return self._request(*args, method='post', **kwargs)

    def put(self, *args, **kwargs):
        return self._request(*args, method='put', **kwargs)

    def patch(self, *args, **kwargs):
        return self._request(*args, method='patch', **kwargs)

    def delete(self, *args, **kwargs):
        return self._request(*args, method='delete', **kwargs)

    def options(self, *args, **kwargs):
        return self._request(*args, method='options', **kwargs)

    def _request(self,
                 path: str,
                 raises: bool = False,
                 success_log_level: str = 'INFO',
                 error_log_level: str = 'ERROR',
                 **kwargs):
        method = kwargs.pop('method', 'get')

        logger.setLevel(getattr(logging, success_log_level))
        log = getattr(logger, success_log_level.lower())

        with httpx.Client(headers=self.headers) as client:
            kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}

            log(f'\nREQUEST: {method.upper()}\nURL: {self.api_url}/{path}'
                f'\nHEADERS: {kwargs["headers"]}\nBODY: {kwargs.get("data")}')

            try:
                resp = getattr(client, method)(f'{self.api_url}/{path}', **kwargs)

                if resp.is_error:
                    logger.setLevel(getattr(logging, error_log_level))
                    log = getattr(logger, error_log_level.lower())

                log(f'\nRESPONSE: {resp.status_code}'
                    f'\nHEADERS: {resp.headers}\nBODY: {resp.content.decode("utf-8")}')

                return (resp, None) if not raises else resp
            except Exception as e:
                logger.setLevel(getattr(logging, error_log_level))
                log = getattr(logger, error_log_level.lower())
                log(e)
                return (None, e) if not raises else None


class AsyncHttpxClient(BaseClient):

    async def get(self, *args, **kwargs):
        return await self._request(*args, method='get', **kwargs)

    async def post(self, *args, **kwargs):
        return await self._request(*args, method='post', **kwargs)

    async def put(self, *args, **kwargs):
        return await self._request(*args, method='put', **kwargs)

    async def patch(self, *args, **kwargs):
        return await self._request(*args, method='patch', **kwargs)

    async def delete(self, *args, **kwargs):
        return await self._request(*args, method='delete', **kwargs)

    async def options(self, *args, **kwargs):
        return await self._request(*args, method='options', **kwargs)

    async def _request(self,
                       path: str,
                       raises: bool = False,
                       success_log_level: str = 'INFO',
                       error_log_level: str = 'ERROR',
                       **kwargs):
        method = kwargs.pop('method', 'get')

        logger.setLevel(getattr(logging, success_log_level))
        log = getattr(logger, success_log_level.lower())

        async with httpx.AsyncClient(headers=self.headers) as client:
            kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}

            log(f'\nREQUEST: {method.upper()}\nURL: {self.api_url}/{path}'
                f'\nHEADERS: {kwargs["headers"]}\nBODY: {kwargs.get("data")}')

            try:
                resp = await getattr(client, method)(f'{self.api_url}/{path}', **kwargs)

                if resp.is_error:
                    logger.setLevel(getattr(logging, error_log_level))
                    log = getattr(logger, error_log_level.lower())

                log(f'\nRESPONSE: {resp.status_code}'
                    f'\nHEADERS: {resp.headers}\nBODY: {resp.content.decode("utf-8")}')

                return (resp, None) if not raises else resp
            except Exception as e:
                logger.setLevel(getattr(logging, error_log_level))
                log = getattr(logger, error_log_level.lower())
                log(e)
                return (None, e) if not raises else None
