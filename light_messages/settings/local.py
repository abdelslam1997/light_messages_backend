from .base import *  # noqa: F401, F403
from .base import env
import os


# Development specific settings should be added here

ENABLE_SILK = env.bool("ENABLE_SILK", default=DEBUG) # noqa: F405
SILK_URL_PREFIX = env.str("SILK_URL_PREFIX", default="api/v1/profiling")

if ENABLE_SILK:
    # Add Silk to Installed Apps
    INSTALLED_APPS += ["silk"]  # noqa: F405

    # Add Silk Middleware right after CommonMiddleware
    common_middleware_index = MIDDLEWARE.index( # noqa: F405
        "django.middleware.common.CommonMiddleware"
    )
    MIDDLEWARE.insert(  # noqa: F405
        common_middleware_index + 1, 
        "silk.middleware.SilkyMiddleware"
    )  

    # Add Silk URL patterns
    API_LOG_EXCLUDE_PREFIXES = list({
        *API_LOG_EXCLUDE_PREFIXES,  # noqa: F405
        f"/{SILK_URL_PREFIX.strip('/')}/",
    })

SILKY_AUTHENTICATION = env.bool("SILKY_AUTHENTICATION", default=True)
SILKY_AUTHORISATION = env.bool("SILKY_AUTHORISATION", default=True)
SILKY_META = env.bool("SILKY_META", default=True)
SILKY_ANALYZE_QUERIES = env.bool("SILKY_ANALYZE_QUERIES", default=True)
SILKY_INTERCEPT_PERCENT = env.int("SILKY_INTERCEPT_PERCENT", default=20)

# Ensure these directories are created and writable
os.makedirs(STATIC_ROOT, exist_ok=True) # noqa: F405
os.makedirs(MEDIA_ROOT, exist_ok=True) # noqa: F405