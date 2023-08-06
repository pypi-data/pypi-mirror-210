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

from typing import Type


class Channel:
    """
    Base channel class.

    Attributes:
        label:
            Channel name (slug).
        is_delivery_supported:
            Channel supports message delivery reports.
        is_ack_supported:
            Channel supports message read reports.
    """

    label: str = ""
    is_delivery_supported: bool = False
    is_ack_supported: bool = False

    @classmethod
    def create(
        cls, *, label: str, is_delivery_supported: bool = False, is_ack_supported: bool = False
    ) -> Type[Channel]:
        return type(
            f"{label.capitalize()}Channel",
            (cls,),
            {
                "label": label,
                "is_delivery_supported": is_delivery_supported,
                "is_ack_supported": is_ack_supported,
            },
        )
