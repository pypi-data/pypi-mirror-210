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

from enum import Enum, IntEnum
from typing import List, Tuple


class StrEnum(str, Enum):
    def __str__(self):
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        return [t.value for t in cls]

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(t.value, str(t.name)) for t in cls]


class CallbackStatus(IntEnum):
    OK = 0
    FAILED = 1


class QuotaType(IntEnum):
    ABSTRACT = 0
    PROVIDER = 1


class QuotaIdentityType(IntEnum):
    ABSTRACT = 0
    AUTH_ENTITY = 1
    IP_ADDRESS = 2


class CallbackUrl(StrEnum):
    ACK = "ack"
    DELIVERY = "delivery"
    GENERAL = "general"


class CallbackEvent(StrEnum):
    ACK = "ack"
    DELIVERY = "delivery"


class ExternalIdType(StrEnum):
    PHONE = "phone"
    EMAIL = "email"
    TELEGRAM_USER_ID = "telegram_user_id"
