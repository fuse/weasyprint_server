import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from flask import current_app, has_app_context
from weasyprint.urls import FatalURLFetchingError, URLFetcher
from .logger import ERROR_LOGGER


class ForbiddenURL(Exception):
    pass


def _origin(url):
    parts = urlsplit(url)
    return (parts.scheme.lower(), (parts.hostname or "").lower(), parts.port)


def _base_url():
    if has_app_context():
        return current_app.config.get("BASE_URL")
    return os.environ.get("BASE_URL")


def is_allowed_url(url, base_url):
    """Only inline data and assets served by BASE_URL can be fetched."""
    if url.startswith("data:"):
        return True
    if not base_url:
        return False

    scheme, host, port = _origin(url)
    return scheme in ("http", "https") and (scheme, host, port) == _origin(base_url)


class SafeURLFetcher(URLFetcher):
    """Fetcher that only follows inline data and assets served by BASE_URL.

    Redirects are disabled: a redirect from an allowed asset to another origin
    would otherwise bypass the origin check.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("timeout", 10)
        kwargs["allow_redirects"] = False
        super().__init__(**kwargs)

    def fetch(self, url, headers=None):
        if not is_allowed_url(url, _base_url()):
            ERROR_LOGGER.warning("asset refused", extra={"context": {"url": url}})
            # WeasyPrint logs and skips the resource: the PDF is generated without it.
            raise ForbiddenURL(url)
        try:
            return super().fetch(url, headers)
        except HTTPError as e:
            if 300 <= e.code < 400:
                # Redirects are not followed: treated like a refused origin.
                ERROR_LOGGER.warning(
                    "asset redirect refused", extra={"context": {"url": url}}
                )
                raise ForbiddenURL(url) from e
            ERROR_LOGGER.warning(
                "asset missing", exc_info=e, extra={"context": {"url": url}}
            )
            raise FatalURLFetchingError(url) from e
        except URLError as e:
            ERROR_LOGGER.warning(
                "asset missing", exc_info=e, extra={"context": {"url": url}}
            )
            # A missing asset of the allowed origin stops the rendering:
            # the caller gets an error instead of an incomplete PDF.
            raise FatalURLFetchingError(url) from e


def custom_url_fetcher():
    """A new fetcher per rendering (URLFetcher keeps per-request state)."""
    return SafeURLFetcher()
