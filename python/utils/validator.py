from urllib.parse import urlparse


def is_valid_url(url):
    # 未入力はOK
    if not url:
        return True
    result = urlparse(url)
    return (
        result.scheme in ["http", "https"]
        and result.netloc
    )