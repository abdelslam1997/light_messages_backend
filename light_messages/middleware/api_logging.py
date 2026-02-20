import logging
import time
from uuid import uuid4

from django.conf import settings


logger = logging.getLogger("light_messages.http")


class ApiRequestLoggingMiddleware:
    """Structured request logging for API endpoints only."""

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _client_ip(request) -> str | None:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def _is_authenticated_user(request) -> bool:
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False))

    def _should_log(self, path: str) -> bool:
        include_prefixes = getattr(settings, "API_LOG_INCLUDE_PREFIXES", ["/api/v1/"])
        exclude_prefixes = getattr(
            settings,
            "API_LOG_EXCLUDE_PREFIXES",
            ["/api/v1/docs/", "/static/", "/media/"],
        )

        return any(path.startswith(prefix) for prefix in include_prefixes) and not any(
            path.startswith(prefix) for prefix in exclude_prefixes
        )

    def __call__(self, request):
        path = request.path
        if not self._should_log(path):
            return self.get_response(request)

        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "http_request_exception",
                extra={
                    "event": "http_request_exception",
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "client_ip": self._client_ip(request),
                    "user_id": request.user.id if self._is_authenticated_user(request) else None,
                    "error": str(e),
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "http_request",
            extra={
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": self._client_ip(request),
                "user_id": request.user.id if self._is_authenticated_user(request) else None,
            },
        )

        response["X-Request-ID"] = request_id
        return response
