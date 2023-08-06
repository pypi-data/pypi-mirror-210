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

from datetime import datetime

from nqsdk.abstract.message import CallbackMeta, ExtIdCallbackMeta, SentMeta
from nqsdk.enums import CallbackEvent


class DummySentMeta(SentMeta):
    def __init__(
        self,
        *,
        ext_id: str,
        attempt_uid: str,
        dt_sent: datetime,
    ):
        self._ext_id = ext_id
        self._attempt_uid = attempt_uid
        self._dt_sent = dt_sent

    @property
    def attempt_uid(self) -> str:
        return self._attempt_uid

    @property
    def ext_id(self) -> str:
        return self._ext_id

    @property
    def dt_sent(self) -> datetime:
        return self._dt_sent


class DummyCallbackMeta(CallbackMeta, DummySentMeta):
    def __init__(self, *, dt_updated: datetime, event: CallbackEvent, **kwargs):
        super().__init__(**kwargs)
        self._dt_updated = dt_updated
        self._event = event

    @property
    def dt_updated(self) -> datetime:
        return self._dt_updated

    @property
    def event(self) -> CallbackEvent:
        return self._event


class DummyExtIdCallbackMeta(ExtIdCallbackMeta):
    def __init__(self, *, ext_id: str, dt_updated: datetime, event: CallbackEvent):
        self._ext_id = ext_id
        self._dt_updated = dt_updated
        self._event = event

    @property
    def ext_id(self) -> str:
        return self._ext_id

    @property
    def dt_updated(self) -> datetime:
        return self._dt_updated

    @property
    def event(self) -> CallbackEvent:
        return self._event
