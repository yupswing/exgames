# Games Universal ID
import re
import hashlib


def makeGuid(title):
    if not title:
        return None
    guid = title.lower()
    guid = re.sub(r"[^A-Za-z0-9+]+", "", guid, 0, re.MULTILINE)
    guid = hashlib.sha1(guid.encode('utf-8')).hexdigest()
    return guid
