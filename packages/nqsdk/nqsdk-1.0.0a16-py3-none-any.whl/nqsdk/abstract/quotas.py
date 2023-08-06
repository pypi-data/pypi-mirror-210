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
from typing import TYPE_CHECKING, Any, Dict

from nqsdk.abstract.mixins import SerializableMixin
from nqsdk.enums import QuotaType

if TYPE_CHECKING:  # pragma: no cover
    from nqsdk.enums import QuotaIdentityType


class Quota(SerializableMixin, ABC):
    def as_dict(self) -> Dict[str, Any]:
        return {
            "quota_type": self.quota_type().value,
        }

    @classmethod
    @abstractmethod
    def quota_type(cls) -> QuotaType:
        pass


class ProviderQuota(Quota, ABC):
    def as_dict(self) -> Dict[str, Any]:
        dump = super().as_dict()
        dump.update(
            {
                "identity_type": self.identity_type().value,
            }
        )

        return dump

    @classmethod
    def quota_type(cls) -> QuotaType:
        return QuotaType.PROVIDER

    @classmethod
    @abstractmethod
    def identity_type(cls) -> QuotaIdentityType:
        pass


class ProviderStaticQuota(ProviderQuota, ABC):
    def __str__(self):
        return f"<{self.__class__.__name__}: {self.identity_type()} {self.limit} per {self.frame}>"

    def as_dict(self) -> Dict[str, Any]:
        dump = super().as_dict()
        dump.update(
            {
                "limit": self.limit,
                "frame": self.frame,
            }
        )

        return dump

    @property
    @abstractmethod
    def limit(self) -> int:
        """How many requests are allowed per time frame."""

    @property
    @abstractmethod
    def frame(self) -> int:
        """Time frame in seconds."""


class ProviderDynamicQuota(ProviderQuota, ABC):

    DATETIME_FORMAT = "%Y-%m-%dT%H-%M-%S%z"

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.identity_type()} until {self._date2str()}>"

    def _date2str(self) -> str:
        return self.until.strftime(ProviderDynamicQuota.DATETIME_FORMAT)

    def as_dict(self) -> Dict[str, Any]:
        dump = super().as_dict()
        dump.update(
            {
                "until": self._date2str(),
            }
        )

        return dump

    @property
    @abstractmethod
    def until(self) -> datetime:
        """Timezone aware date & time in the future when we're allowed to send the next request."""
