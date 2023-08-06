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
from datetime import datetime
from typing import IO, List, Optional, Union

from nqsdk.enums import CallbackEvent


class Attachment(ABC):
    @abstractmethod
    def get_content_type(self) -> str:
        """Attachment content type, e.g. `text/html`."""

    @abstractmethod
    def get_contents(self) -> Union[str, bytes, IO]:
        """Attachment contents or file like object."""


class Message(ABC):
    @property
    @abstractmethod
    def channel(self) -> str:
        """Returns label of the channel which should be used for delivery."""

    @property
    @abstractmethod
    def attempt_uid(self) -> str:
        """Returns unique delivery attempt ID."""

    @abstractmethod
    def get_recipient_id(self) -> str:
        """
        Returns external ID like phone number or username
            where provider needs to send the message.
        """

    def get_signature(self) -> Optional[str]:
        """Returns sender signature."""
        return None

    @abstractmethod
    def get_content(self) -> str:
        pass

    def get_attachments(self) -> Optional[List[Attachment]]:
        """Message attachments."""
        return None


class SentMeta(ABC):
    """
    Abstract class for metadata that contain information about sent message.
    """

    @property
    @abstractmethod
    def attempt_uid(self) -> str:
        """Unique delivery attempt ID."""

    @property
    @abstractmethod
    def ext_id(self) -> str:
        """Sent message ID assigned by provider."""

    @property
    @abstractmethod
    def dt_sent(self) -> datetime:
        """Timezone aware date & time the message was sent."""


class BaseCallbackMeta(ABC):
    """
    Abstract base class for callbacks metadata that contain
    information about callback event related to sent message.
    """

    @property
    @abstractmethod
    def dt_updated(self) -> datetime:
        """Timezone aware date & time the message was updated."""

    @property
    @abstractmethod
    def event(self) -> CallbackEvent:
        """Callback event name."""


class CallbackMeta(BaseCallbackMeta, SentMeta, ABC):
    """
    Abstract class for callbacks metadata that contain full information about
    sent message & callback event related to it.
    """


class ExtIdCallbackMeta(BaseCallbackMeta, ABC):
    """
    Abstract class for static callbacks metadata where message identified by its external ID.

    Contains only limited information about sent message (its external ID).
    """

    @property
    @abstractmethod
    def ext_id(self) -> str:
        """Sent message ID assigned by provider."""
