"""
Compression and Optimization Middleware
Gzip/Brotli response compression for FastAPI
"""

import gzip
import zlib
from io import BytesIO
from typing import Callable, Optional, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send
import re


class CompressionMiddleware:
    """
    ASGI middleware for response compression.
    Supports Gzip and Deflate encoding.
    """
    
    MINIMUM_SIZE = 500  # Don't compress small responses
    COMPRESSIBLE_TYPES = {
        'text/plain',
        'text/html',
        'text/css',
        'text/javascript',
        'text/xml',
        'application/json',
        'application/javascript',
        'application/xml',
        'application/xhtml+xml',
        'image/svg+xml',
    }
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        compression_level: int = 6,
        exclude_paths: Optional[Set[str]] = None
    ):
        self.app = app
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.exclude_paths = exclude_paths or set()
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path should be excluded
        path = scope.get("path", "")
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            await self.app(scope, receive, send)
            return
        
        # Get accepted encodings
        accept_encoding = self._get_accept_encoding(scope)
        
        if not accept_encoding:
            await self.app(scope, receive, send)
            return
        
        # Determine encoding to use
        encoding = self._select_encoding(accept_encoding)
        
        if not encoding:
            await self.app(scope, receive, send)
            return
        
        # Wrap send to compress response
        response_started = False
        initial_headers = []
        body_parts = []
        content_type = ""
        
        async def compressed_send(message: Message):
            nonlocal response_started, initial_headers, body_parts, content_type
            
            if message["type"] == "http.response.start":
                response_started = True
                initial_headers = list(message.get("headers", []))
                
                # Extract content type
                for name, value in initial_headers:
                    if name == b"content-type":
                        content_type = value.decode()
                        break
                
                return  # Don't send yet, wait for body
            
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                
                body_parts.append(body)
                
                if not more_body:
                    # All body received, compress if applicable
                    full_body = b"".join(body_parts)
                    
                    should_compress = (
                        len(full_body) >= self.minimum_size and
                        self._is_compressible(content_type)
                    )
                    
                    if should_compress:
                        compressed_body = self._compress(full_body, encoding)
                        
                        # Update headers
                        new_headers = []
                        for name, value in initial_headers:
                            if name.lower() not in (b"content-length", b"content-encoding"):
                                new_headers.append((name, value))
                        
                        new_headers.append((b"content-encoding", encoding.encode()))
                        new_headers.append((b"content-length", str(len(compressed_body)).encode()))
                        new_headers.append((b"vary", b"Accept-Encoding"))
                        
                        # Send compressed response
                        await send({
                            "type": "http.response.start",
                            "status": message.get("status", 200),
                            "headers": new_headers
                        })
                        await send({
                            "type": "http.response.body",
                            "body": compressed_body
                        })
                    else:
                        # Send uncompressed
                        await send({
                            "type": "http.response.start",
                            "status": 200,
                            "headers": initial_headers
                        })
                        await send({
                            "type": "http.response.body",
                            "body": full_body
                        })
        
        await self.app(scope, receive, compressed_send)
    
    def _get_accept_encoding(self, scope: Scope) -> str:
        headers = dict(scope.get("headers", []))
        return headers.get(b"accept-encoding", b"").decode()
    
    def _select_encoding(self, accept_encoding: str) -> Optional[str]:
        """Select best encoding from accepted encodings."""
        accept_encoding = accept_encoding.lower()
        
        if "gzip" in accept_encoding:
            return "gzip"
        elif "deflate" in accept_encoding:
            return "deflate"
        
        return None
    
    def _is_compressible(self, content_type: str) -> bool:
        """Check if content type should be compressed."""
        if not content_type:
            return False
        
        # Extract base type without parameters
        base_type = content_type.split(";")[0].strip().lower()
        return base_type in self.COMPRESSIBLE_TYPES
    
    def _compress(self, data: bytes, encoding: str) -> bytes:
        """Compress data with specified encoding."""
        if encoding == "gzip":
            buf = BytesIO()
            with gzip.GzipFile(
                fileobj=buf,
                mode="wb",
                compresslevel=self.compression_level
            ) as f:
                f.write(data)
            return buf.getvalue()
        
        elif encoding == "deflate":
            return zlib.compress(data, self.compression_level)
        
        return data


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add cache control headers based on path patterns.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        static_max_age: int = 31536000,  # 1 year
        api_max_age: int = 0,
        default_max_age: int = 3600
    ):
        super().__init__(app)
        self.static_max_age = static_max_age
        self.api_max_age = api_max_age
        self.default_max_age = default_max_age
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        path = request.url.path
        
        # Static assets (immutable)
        if self._is_static_asset(path):
            response.headers["Cache-Control"] = f"public, max-age={self.static_max_age}, immutable"
        
        # API routes (no cache by default)
        elif path.startswith("/api/"):
            if "Cache-Control" not in response.headers:
                response.headers["Cache-Control"] = "no-store"
        
        # HTML pages
        elif path.endswith(".html") or not "." in path.split("/")[-1]:
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        
        return response
    
    def _is_static_asset(self, path: str) -> bool:
        """Check if path is a static asset."""
        static_extensions = {
            ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg",
            ".woff", ".woff2", ".ttf", ".eot", ".ico", ".webp"
        }
        return any(path.endswith(ext) for ext in static_extensions)


class ETaggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add ETag headers for response validation.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Only for successful GET requests
        if request.method != "GET" or response.status_code != 200:
            return response
        
        # Skip if already has ETag
        if "ETag" in response.headers:
            return response
        
        # Generate ETag from response body (for small responses)
        # Note: This is a simplified implementation
        if hasattr(response, "body"):
            etag = self._generate_etag(response.body)
            response.headers["ETag"] = etag
            
            # Check If-None-Match
            if_none_match = request.headers.get("If-None-Match")
            if if_none_match and if_none_match == etag:
                return Response(status_code=304)
        
        return response
    
    def _generate_etag(self, content: bytes) -> str:
        """Generate ETag from content."""
        import hashlib
        hash_value = hashlib.md5(content).hexdigest()
        return f'"{hash_value}"'


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'self'"
        )
        
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(self), "
            "gyroscope=(), magnetometer=(), microphone=(), "
            "payment=(), usb=()"
        )
        
        # HSTS (only for production)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


def setup_optimization_middleware(app):
    """
    Configure all optimization middlewares for the application.
    """
    # Add middlewares in reverse order (first added = last executed)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ETaggerMiddleware)
    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(
        CompressionMiddleware,
        minimum_size=500,
        compression_level=6,
        exclude_paths={"/api/v1/monitoring/ws", "/health"}
    )
    
    return app
