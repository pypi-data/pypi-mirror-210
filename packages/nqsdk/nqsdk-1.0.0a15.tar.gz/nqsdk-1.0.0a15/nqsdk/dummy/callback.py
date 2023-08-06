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

from typing import Dict, Optional

from nqsdk.abstract.callback import CallbackResponse
from nqsdk.abstract.message import SentMeta
from nqsdk.enums import CallbackStatus


class DummyCallbackResponse(CallbackResponse):
    def __init__(self, *, status: CallbackStatus, meta: SentMeta = None, error: str = None):
        self._status = status
        self._meta = meta
        self._error = error

    @property
    def status(self) -> CallbackStatus:
        return self._status

    @property
    def meta(self) -> Optional[SentMeta]:
        return self._meta

    @property
    def error(self) -> Optional[str]:
        return self._error

    @property
    def code_ok(self) -> int:
        return 200

    def get_content_type(self) -> Optional[str]:
        if (self.status == CallbackStatus.OK and self.meta) or self.error:
            return "application/json"

    def get_content(self) -> Optional[Dict]:
        if self.status == CallbackStatus.OK and self.meta:
            return {"message_id": self.meta.ext_id}
        else:
            if self.error:
                return {"error": self.error}
