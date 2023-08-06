"""
Copyright (c) 2022 Inqana Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from nqsdk.consts import DEFAULT_CALLBACK_CODE_ERROR, DEFAULT_CALLBACK_CODE_OK
from nqsdk.enums import CallbackStatus

if TYPE_CHECKING:  # pragma: no cover
    from .message import SentMeta


class CallbackResponse(ABC):
    @property
    @abstractmethod
    def status(self) -> CallbackStatus:
        """Status of the callback response."""

    @property
    @abstractmethod
    def meta(self) -> Optional[SentMeta]:
        """Sent message metadata."""

    @property
    @abstractmethod
    def error(self) -> Optional[str]:
        """Error message."""

    @property
    def code_ok(self) -> int:
        """Default HTTP status code for a successful response."""

        return DEFAULT_CALLBACK_CODE_OK

    @property
    def code_error(self) -> int:
        """Default HTTP status code for an error response."""

        return DEFAULT_CALLBACK_CODE_ERROR

    def get_code(self) -> int:
        """Get the HTTP status code based on the response status."""

        if self.status == CallbackStatus.OK:
            return self.code_ok
        else:
            return self.code_error

    def get_content_type(self) -> Optional[str]:
        """Content type header value, e.g. `application/json`."""
        return None

    def get_content(self) -> Optional[Any]:
        """
        Content as is, i.e. not serialized.

        E.g. if your content type is `text/plain` return string then, if `application/json`
        return raw python structure `dict`, `list` or whatever else.
        It must be serializable by standard DRF renderers:
        https://www.django-rest-framework.org/api-guide/renderers/.
        """
        return None
