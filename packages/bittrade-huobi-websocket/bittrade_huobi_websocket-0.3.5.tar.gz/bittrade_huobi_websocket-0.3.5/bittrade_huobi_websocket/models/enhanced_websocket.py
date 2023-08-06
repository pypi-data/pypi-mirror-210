from typing import Any
from elm_framework_helpers.websockets import models
import orjson


class EnhancedWebsocket(models.EnhancedWebsocket):
    def send_message(self, message: Any) -> int | str:
        return self.send_json(message)

    def prepare_request(self, message: Any) -> tuple[str, bytes]:
        self._id += 1
        return f"id{self._id}", orjson.dumps(message)
