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

import uuid
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, Union

from jsonschema import ValidationError, validate

from nqsdk.enums import CallbackUrl
from nqsdk.exceptions import ImproperlyConfigured

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.request import Request

    from .callback import CallbackResponse
    from .channel import Channel
    from .message import CallbackMeta, ExtIdCallbackMeta, Message, SentMeta
    from .quotas import ProviderStaticQuota


class Provider(ABC):
    """
    Base provider class.

    Attributes:
        label:
            Provider name (slug).
    """

    label: str = ""

    def __init__(self, *, config: Dict, callback_urls: Dict[Union[CallbackUrl, str], str]):
        """
        Args:
            config:
                Provider config.
            callback_urls:
                URL templates for callbacks; each template must contain `{attempt_uid}` placeholder.

                Example:

                    {
                        "ack": "https://example.com/cb/ack/{attempt_uid}",
                        "delivery": "https://example.com/cb/delivery/{attempt_uid}",
                        "common": "https://example.com/cb/{attempt_uid}",
                    }

        Raises:
            nqsdk.exceptions.ImproperlyConfigured:
                Config validation failed.
        """

        self._config = self.check_config(config=config)
        self._callback_urls = self._check_callback_urls(urls=callback_urls)

    @property
    def config(self) -> Dict:
        """Provider config."""
        return self._config

    @staticmethod
    def _check_callback_urls(
        urls: Dict[Union[CallbackUrl, str], str]
    ) -> Dict[Union[CallbackUrl, str], str]:
        attempt_uid = uuid.uuid4().hex
        for key, url in urls.items():
            if key not in CallbackUrl.values():
                raise ImproperlyConfigured(f"Invalid callback URL key: '{key}'.")
            if "{attempt_uid}" not in url or attempt_uid not in url.format(attempt_uid=attempt_uid):
                raise ImproperlyConfigured(
                    "Invalid callback URL: '{attempt_uid}' placeholder is missing."
                )

        return urls

    def get_callback_url(self, *, key: Union[CallbackUrl, str], attempt_uid: str) -> Optional[str]:
        url = self._callback_urls.get(key)
        if url:
            return url.format(attempt_uid=attempt_uid)

    def get_quotas(self) -> List[ProviderStaticQuota]:
        return []

    @abstractmethod
    def send(self, *, message: Message) -> SentMeta:
        """
        Sends message.

        Args:
            message:

        Returns:
            Sent message metadata.

        Raises:
            nqsdk.exception.SentException:
                Message sending failed by some reason reported by provider.
                This type of exception should only be raised if the failure is
                reported by provider. It's not for network errors, etc.
            nqsdk.exception.QuotaExceededException:
                Provider reported that quota was exceeded.
        """

    @classmethod
    @abstractmethod
    def get_config_schema(cls) -> Dict:
        """JSON schema for config validation."""

    @classmethod
    @abstractmethod
    def get_channels(cls) -> List[Type[Channel]]:
        """List of channels supported by provider."""

    @classmethod
    def check_config(cls, config: Dict) -> Dict:
        """
        Validates provider config against its schema.

        Args:
            config:
                Provider config.

        Returns:
            Provider config.

        Raises:
            nqsdk.exceptions.ImproperlyConfigured:
                Config validation failed.
        """

        try:
            validate(config, cls.get_config_schema())
        except ValidationError as e:
            raise ImproperlyConfigured(e)

        return config


class HealthCheckMixin(ABC):
    """Health check support."""

    @abstractmethod
    def check_health(self) -> bool:
        """Checks provider health."""


class BalanceCheckMixin(ABC):
    """Balance check support."""

    @abstractmethod
    def get_balance(self) -> Decimal:
        """Checks user's balance."""


class DeliveryCheckMixin(ABC):
    """Delivery check support."""

    @abstractmethod
    def check_delivery(self, *, meta: SentMeta) -> Optional[CallbackMeta]:
        """Send request to provider to check if message was delivered."""


class AckCheckMixin(ABC):
    """Ack check support."""

    @abstractmethod
    def check_ack(self, *, meta: SentMeta) -> Optional[CallbackMeta]:
        """Send request to provider to check if message was read."""


class CallbackHandleMixin(ABC):
    """Callback handling support with no difference b/w delivery & ack callbacks."""

    @abstractmethod
    def handle_callback(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        """
        Handles 'message delivered' & 'message ack' callbacks from provider
        in case it does not support separate callbacks for each one.

        Args:
            request:
                Raw HTTP request from provider's callback.
            meta:
                Sent message metadata.

        Returns:
            Callback response & sent message metadata.

        Raises:
            nqsdk.exceptions.CallbackHandlingException:
                Must be raised in case of handling error.
        """


class StaticCallbackHandleMixin(ABC):
    """Callback handling support for callbacks send to a static provider-related endpoint."""

    @abstractmethod
    def handle_static_callback(
        self, *, request: Request
    ) -> Tuple[CallbackResponse, ExtIdCallbackMeta]:
        """
        Handles static callbacks from provider where message identified by its external ID.

        Args:
            request:
                Raw HTTP request from provider's callback.

        Returns:
            Callback response & message metadata.

        Raises:
            nqsdk.exceptions.CallbackHandlingException:
                Must be raised in case of handling error.
        """


class DeliveryHandleMixin(ABC):
    """Delivery handling support."""

    @abstractmethod
    def handle_delivered(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        """
        Handles 'message delivered' callback from provider.

        Args:
            request:
                Raw HTTP request from provider's callback.
            meta:
                Sent message metadata.

        Returns:
            Callback response & sent message metadata.

        Raises:
            nqsdk.exceptions.CallbackHandlingException:
                Must be raised in case of handling error.
        """


class AckHandleMixin(ABC):
    """Ack handling support."""

    @abstractmethod
    def handle_ack(
        self, *, request: Request, meta: SentMeta
    ) -> Tuple[CallbackResponse, CallbackMeta]:
        """
        Handles 'message ack' callback from provider.

        Args:
            request:
                Raw HTTP request from provider's callback.
            meta:
                Sent message metadata.

        Returns:
            Callback response & sent message metadata.

        Raises:
            nqsdk.exceptions.CallbackHandlingException:
                Must be raised in case of handling error.
        """
