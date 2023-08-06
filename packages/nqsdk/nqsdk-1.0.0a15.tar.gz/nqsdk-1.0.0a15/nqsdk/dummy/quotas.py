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

from nqsdk.abstract.quotas import ProviderStaticQuota
from nqsdk.enums import QuotaIdentityType


class PerSecondQuota(ProviderStaticQuota):
    @classmethod
    def identity_type(cls) -> QuotaIdentityType:
        return QuotaIdentityType.AUTH_ENTITY

    @property
    def limit(self) -> int:
        return 3

    @property
    def frame(self) -> int:
        return 1


class PerHourQuota(ProviderStaticQuota):
    @classmethod
    def identity_type(cls) -> QuotaIdentityType:
        return QuotaIdentityType.AUTH_ENTITY

    @property
    def limit(self) -> int:
        return 6000

    @property
    def frame(self) -> int:
        return 60 * 60
