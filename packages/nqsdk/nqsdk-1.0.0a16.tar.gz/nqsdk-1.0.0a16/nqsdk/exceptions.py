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

from typing import TYPE_CHECKING, Any, Dict, Optional

from .abstract.mixins import SerializableMixin

if TYPE_CHECKING:  # pragma: no cover
    from .abstract.callback import CallbackResponse
    from .abstract.quotas import Quota


class SentException(Exception, SerializableMixin):
    def as_dict(self) -> Dict[str, Any]:
        return {"exc": self.__class__.__name__, "message": str(self)}


class CallbackHandlingException(Exception, SerializableMixin):
    """Exception raised when an error occurs while handling a callback."""

    def __init__(self, *args, response: CallbackResponse):
        super().__init__(*args)
        self._response = response

    @property
    def response(self) -> CallbackResponse:
        """Callback response will be used to generate an HTTP response."""

        return self._response

    def as_dict(self) -> Dict[str, Any]:
        return {"exc": self.__class__.__name__, "message": str(self)}


class UnsupportedCallbackEventException(Exception):
    """
    Exception raised for a callback event that isn't supported by a receiver.

    Supported events are listed in `nqsdk.enums.CallbackEvent`.
    """

    def __init__(self, *args, code: int):
        """
        Args:
            *args:
            code:
                HTTP status code.
        """

        super().__init__(*args)
        self._code = code

    def get_code(self) -> int:
        """HTTP status code."""

        return self._code


class ImproperlyConfigured(Exception):
    pass


class QuotaExceededException(Exception, SerializableMixin):
    def __init__(self, *args, quota: Quota = None):
        super().__init__(*args)
        self._quota = quota

    @property
    def quota(self) -> Optional[Quota]:
        return self._quota

    def as_dict(self) -> Dict[str, Any]:
        return {
            "exc": self.__class__.__name__,
            "message": str(self),
            "quota": self.quota.as_dict() if self.quota else None,
        }


class ValidationError(ValueError):
    pass
