"""Lazy GEE initialization shared by geospatial services."""
import json
import os

import ee

from core.config import settings

_initialized = False


def init_gee():
    global _initialized
    if _initialized:
        return
    key_json_str = settings.gee_key_json or os.environ.get("GEE_KEY_JSON", "")
    if key_json_str:
        key_data = json.loads(key_json_str)
        credentials = ee.ServiceAccountCredentials(
            key_data["client_email"],
            key_data=key_data,
        )
        ee.Initialize(credentials)
    elif settings.gee_service_account:
        credentials = ee.ServiceAccountCredentials(
            settings.gee_service_account,
            settings.gee_key_file,
        )
        ee.Initialize(credentials)
    else:
        # Development: interactive auth via `earthengine authenticate`.
        ee.Initialize()
    _initialized = True