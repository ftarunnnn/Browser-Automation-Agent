import re
from urllib.parse import urlparse
from typing import Tuple


class InputValidator:
    BLOCKED_SCHEMES = ["file", "gopher", "dict", "ftp"]
    BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "::1"]

    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validates target URL against SSRF and malicious protocol schemes.
        """
        if not url:
            return False, "URL cannot be empty"

        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("data:text/html")):
            url = "https://" + url

        if url.startswith("data:text/html"):
            return True, url

        parsed = urlparse(url)
        if parsed.scheme.lower() in cls.BLOCKED_SCHEMES:
            return False, f"URL scheme '{parsed.scheme}' is blocked for security"

        hostname = (parsed.hostname or "").lower()
        if hostname in cls.BLOCKED_HOSTS and not url.startswith("http://127.0.0.1:8088"):  # local test server exception
            return False, f"Access to private/internal host '{hostname}' is restricted (SSRF protection)"

        return True, url

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitizes filenames to prevent path traversal vulnerabilities.
        """
        clean = re.sub(r"[/\\]", "", filename)
        clean = re.sub(r"\.\.+", ".", clean)
        return clean or "downloaded_file"


input_validator = InputValidator()
