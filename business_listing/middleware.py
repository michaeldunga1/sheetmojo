from django.core.cache import cache
from django.http import HttpResponse


class RequestSafetyMiddleware:
    """Add a light safety layer for security headers and abuse throttling.

    This middleware intentionally stays conservative so it can be used on a
    small Django deployment without external services. It focuses on:
    1. Adding browser security headers.
    2. Rate-limiting repeated POST requests on sensitive endpoints.
    """

    AUTH_PATH_PREFIXES = ('/login/', '/register/')
    WRITE_PATH_PREFIXES = ('/add-business/', '/business/', '/user/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        throttle_response = self._throttle_if_needed(request)
        if throttle_response is not None:
            return throttle_response

        response = self.get_response(request)
        self._apply_security_headers(response)
        return response

    def _throttle_if_needed(self, request):
        if request.method != 'POST':
            return None

        bucket, limit, window = self._rate_limit_profile(request.path)
        if bucket is None:
            return None

        client_ip = self._client_ip(request)
        cache_key = f'rate-limit:{bucket}:{client_ip}'
        attempts = cache.get(cache_key, 0)
        if attempts >= limit:
            return HttpResponse(
                'Too many requests. Please wait a moment and try again.',
                status=429,
            )

        cache.set(cache_key, attempts + 1, timeout=window)
        return None

    def _rate_limit_profile(self, path):
        if path.startswith(self.AUTH_PATH_PREFIXES):
            return 'auth', 10, 60

        if path == '/logout/':
            return None, None, None

        if path.startswith(self.WRITE_PATH_PREFIXES) and any(
            marker in path for marker in ('/edit/', '/delete/', '/add-business/', '/user/')
        ):
            return 'writes', 30, 60

        return None, None, None

    def _client_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def _apply_security_headers(self, response):
        # The CSP keeps third-party assets constrained to the libraries already
        # used by the project. Inline allowances remain because current templates
        # still include a small amount of inline JS/CSS.
        response.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://unpkg.com https://platform-api.sharethis.com; "
            "connect-src 'self';"
        )
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.setdefault('Cross-Origin-Resource-Policy', 'same-origin')
