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

from typing import Union

import phonenumbers
from email_validator import EmailNotValidError, validate_email

from nqsdk.enums import ExternalIdType
from nqsdk.exceptions import ValidationError


class ExternalIdValidator:

    _VALIDATORS = {
        ExternalIdType.PHONE: "_validate_intl_phone",
        ExternalIdType.EMAIL: "_validate_email",
        ExternalIdType.TELEGRAM_USER_ID: "_validate_telegram_user_id",
    }

    def validate(self, id_type: Union[ExternalIdType, str], value: str) -> str:
        """
        Validates external ID depending on its type.

        Args:
            id_type:
                External ID type.
            value:
                External ID.

        Returns:
            External ID passed.

        Raises:
            nqsdk.exceptions.ValidationError:
                Validation failed.
        """

        method = getattr(self, self._VALIDATORS[ExternalIdType(id_type)])

        return method(value)

    @staticmethod
    def _validate_intl_phone(value: str) -> str:
        if not value.isdigit():
            raise ValidationError(
                "The phone number must be in international format and contain only digits."
            )

        try:
            if not phonenumbers.is_valid_number(phonenumbers.parse(f"+{value}")):
                raise ValidationError("Provided value doesn't seem to be a phone number.")
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValidationError(e)

        return value

    @staticmethod
    def _validate_telegram_user_id(value: str) -> str:
        if value.startswith("0") or not value.isdigit():
            raise ValidationError(
                "Telegram user ID must contain digits only & must not start w/ zero."
            )

        return value

    @staticmethod
    def _validate_email(value: str) -> str:
        try:
            validate_email(value, check_deliverability=False, allow_smtputf8=True)
        except EmailNotValidError as e:
            raise ValidationError(e)

        return value
