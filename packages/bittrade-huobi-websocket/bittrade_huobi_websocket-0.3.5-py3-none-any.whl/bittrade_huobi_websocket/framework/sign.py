import hashlib
import hmac
import time
from typing import Any, Callable, Dict
from requests import PreparedRequest

def create_signer(api_key: str, secret: str) -> Callable[[PreparedRequest], PreparedRequest]:
    def sign_request(request: PreparedRequest) -> PreparedRequest:
        # Generate timestamp
        timestamp = str(int(time.time() * 1000))

        # Get endpoint and parameters from request object
        endpoint = request.url.replace(request.base_url, "")
        params = request.params

        # Create signature string
        method = request.method.upper()
        host = request.url.replace(endpoint, "").replace("https://", "").replace("http://", "")
        path = endpoint
        query = urlencode(sorted(params.items()))
        payload = f"{method}\n{host}\n{path}\n{query}"
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

        # Add signature headers to request
        request.headers["Authorization"] = f"Bearer {api_key}"
        request.headers["Timestamp"] = timestamp
        request.headers["Signature"] = signature

        return request

    return sign_request
