"""Accept accessible citations without opening arbitrary HTTP source hosts."""
from urllib.parse import urlsplit

# Both historical primary-source sites were read over HTTP during the audit.
HTTP_SOURCE_HOSTS = {'www.sorahane.org', 'sorakaze.blue'}


def source_url_valid(value):
    if not isinstance(value, str):
        return False
    try:
        url = urlsplit(value)
        return bool(url.hostname) and (url.scheme == 'https' or
                                      (url.scheme == 'http' and url.hostname in HTTP_SOURCE_HOSTS))
    except ValueError:
        return False
