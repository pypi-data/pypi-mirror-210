import logging

import backoff
import requests as r

logger = logging.getLogger(__name__)


class RequestManager:
    BASE_URL = "https://api.notion.com/v1/"

    @backoff.on_exception(
        backoff.expo,
        (
            r.ReadTimeout,
            r.ConnectTimeout,
            r.Timeout,
            r.JSONDecodeError,
            r.ConnectionError,
        ),
        max_tries=8,
    )
    def make_request(self, path, *, method, params=None):
        _path = f"{self.BASE_URL}{path}"
        _params = (
            dict(params=params) or {}
            if method.upper() == "GET"
            else dict(json=params) or {}
        )

        _r = r.request(
            method,
            _path,
            headers=self.get_headers(),
            timeout=10.0,
            **_params,
        )
        if not _r.ok:
            logger.warning(_r.json())
            if _r.status_code == 404:
                raise NotFoundException
            assert (
                False
            ), f"Запрос {method.upper()} {_path} прошел с ошибкой {_r.status_code}/n"
        return _r.json()

    def pagination(self, url, *, params=None, **kwargs):
        _params = params or {}
        response = None
        result = []
        while True:
            response = self.make_request(url, params=_params, **kwargs)
            result.extend(response["results"])

            if not response.get("has_more"):
                return result
            _params["start_cursor"] = response["next_cursor"]

    def pagination_iterator(self, url, *, params=None, **kwargs):
        _params = params or {}
        while True:
            response = self.make_request(url, params=_params, **kwargs)
            result = response["results"]
            yield from result

            if not response.get("has_more"):
                return
            _params["start_cursor"] = response["next_cursor"]


class NotFoundException(Exception):
    ...
