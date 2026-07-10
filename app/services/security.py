import bleach
from itsdangerous import URLSafeTimedSerializer


ALLOWED_TAGS = ["b", "strong", "i", "em", "ul", "ol", "li", "p", "br", "span"]


def clean_text(value: str) -> str:
    return bleach.clean(value or "", tags=ALLOWED_TAGS, strip=True)


def token_serializer(secret_key: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key)
