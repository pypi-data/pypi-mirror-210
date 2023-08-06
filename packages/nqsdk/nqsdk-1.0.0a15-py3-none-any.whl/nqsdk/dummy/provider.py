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

import json
import random
import string
import uuid
from datetime import datetime
from decimal import Decimal
from importlib import resources
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

import pytz
import requests
from requests import Response

from nqsdk.abstract.channel import Channel
from nqsdk.abstract.provider import (
    AckCheckMixin,
    AckHandleMixin,
    BalanceCheckMixin,
    CallbackHandleMixin,
    DeliveryCheckMixin,
    DeliveryHandleMixin,
    HealthCheckMixin,
    Provider,
    StaticCallbackHandleMixin,
)
from nqsdk.enums import CallbackEvent, CallbackStatus, CallbackUrl
from .callback import DummyCallbackResponse
from .message import DummyCallbackMeta, DummyExtIdCallbackMeta, DummySentMeta
from .quotas import PerHourQuota, PerSecondQuota

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.request import Request

    from nqsdk.abstract.callback import CallbackResponse
    from nqsdk.abstract.message import CallbackMeta, ExtIdCallbackMeta, Message, SentMeta
    from nqsdk.abstract.quotas import ProviderStaticQuota


class DummyProvider(
    BalanceCheckMixin,
    HealthCheckMixin,
    DeliveryCheckMixin,
    AckCheckMixin,
    DeliveryHandleMixin,
    AckHandleMixin,
    CallbackHandleMixin,
    StaticCallbackHandleMixin,
    Provider,
):

    label = "Dummy provider"

    @classmethod
    def get_channels(cls) -> List[Type[Channel]]:
        channels = []
        for label in [
            "email",
            "dummy",
            "push",
            "sms",
            "phone",
            "telegram",
            "viber",
            "whatsapp",
            "icq",
        ]:
            channels.append(
                Channel.create(label=label, is_delivery_supported=True, is_ack_supported=True)
            )

        return channels

    @classmethod
    def get_config_schema(cls) -> Dict:
        return json.loads(
            resources.files("nqsdk.dummy").joinpath("resources/config_schema.json").read_text()
        )

    @classmethod
    def get_quotas(cls) -> List[ProviderStaticQuota]:
        return [PerSecondQuota(), PerHourQuota()]

    def check_health(self) -> bool:
        self._request(key="health_check")

        return True

    def get_balance(self) -> Decimal:
        self._request(key="balance_get")

        return Decimal(f"{random.uniform(1.0, 1000.0 * 10):.2f}")

    def send(self, *, message: Message) -> SentMeta:
        data = {
            "channel": message.channel,
            "recipient_id": message.get_recipient_id(),
            "signature": message.get_signature(),
            "content": message.get_content(),
        }

        for url_type in CallbackUrl.values():
            url = self.get_callback_url(key=url_type, attempt_uid=message.attempt_uid)
            # If callback URL is set we'll add it to the request.
            if url:
                data[f"callback_url_{url_type.lower()}"] = url

        self._request(key="send", data=data)

        return DummySentMeta(
            attempt_uid=message.attempt_uid,
            ext_id=uuid.uuid4().hex,
            dt_sent=datetime.now(tz=pytz.timezone("UTC")),
        )

    def check_delivery(self, *, meta: SentMeta) -> Optional[CallbackMeta]:
        self._request(key="delivery_check", data={"message_id": meta.ext_id})

        return DummyCallbackMeta(
            attempt_uid=meta.attempt_uid,
            ext_id=meta.ext_id,
            dt_sent=meta.dt_sent,
            dt_updated=datetime.now(tz=pytz.timezone("UTC")),
            event=CallbackEvent.DELIVERY,
        )

    def check_ack(self, *, meta: SentMeta) -> Optional[CallbackMeta]:
        self._request(key="ack_check", data={"message_id": meta.ext_id})

        return DummyCallbackMeta(
            attempt_uid=meta.attempt_uid,
            ext_id=meta.ext_id,
            dt_sent=meta.dt_sent,
            dt_updated=datetime.now(tz=pytz.timezone("UTC")),
            event=CallbackEvent.ACK,
        )

    def handle_delivered(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        return DummyCallbackResponse(status=CallbackStatus.OK, meta=meta), DummyCallbackMeta(
            attempt_uid=meta.attempt_uid,
            ext_id=meta.ext_id,
            dt_sent=meta.dt_sent,
            dt_updated=datetime.now(tz=pytz.timezone("UTC")),
            event=CallbackEvent.DELIVERY,
        )

    def handle_ack(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        return DummyCallbackResponse(status=CallbackStatus.OK, meta=meta), DummyCallbackMeta(
            attempt_uid=meta.attempt_uid,
            ext_id=meta.ext_id,
            dt_sent=meta.dt_sent,
            dt_updated=datetime.now(tz=pytz.timezone("UTC")),
            event=CallbackEvent.ACK,
        )

    def handle_callback(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        if random.choice([True, False]):
            return self.handle_delivered(request=request, meta=meta)
        else:
            return self.handle_ack(request=request, meta=meta)

    def handle_static_callback(
        self, *, request: Request
    ) -> Tuple[CallbackResponse, ExtIdCallbackMeta]:
        return DummyCallbackResponse(status=CallbackStatus.OK), DummyExtIdCallbackMeta(
            # Randomly generate message ext ID.
            ext_id="".join(random.choices(string.ascii_uppercase + string.digits, k=20)),
            dt_updated=datetime.now(tz=pytz.timezone("UTC")),
            event=CallbackEvent(random.choice(CallbackEvent.values())),
        )

    def _request(self, key: str, data: Dict = None) -> Optional[Response]:
        options = self._get_request_options(key)
        if options:
            if data:
                if options["method"] == "get":
                    options["params"] = data
                else:
                    options["json"] = data

            resp = requests.request(**options)
            if resp.status_code == 200:
                return resp
            else:
                resp.raise_for_status()

    def _get_request_options(
        self, key: str, default_method: str = "get"
    ) -> Optional[Dict[str, Any]]:
        if key == "send":
            default_method = "post"
        url = self.config.get(f"{key}_url")
        if url:
            options = {"url": url, "method": self.config.get(f"{key}_method", default_method)}

            auth_token = self.config.get("auth_token")
            if auth_token:
                options["headers"] = {"Authorization": auth_token}

            return options
