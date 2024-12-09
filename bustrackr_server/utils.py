from datetime import datetime
from decimal import Decimal

def orjson_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj).rstrip('0')
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')