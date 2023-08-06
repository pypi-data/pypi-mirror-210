import json
from json import JSONDecodeError


def unpack(request, default=None):
    request.raise_for_status()
    try:
        return json.loads(request.content)
    except (JSONDecodeError, UnicodeDecodeError):
        return request.content or default
