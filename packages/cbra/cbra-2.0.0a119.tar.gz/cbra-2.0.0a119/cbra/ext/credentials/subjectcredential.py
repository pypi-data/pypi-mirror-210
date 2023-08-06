# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from typing import Literal

import pydantic
from canonical import DomainName
from canonical import ResourceName
from headless.ext.oauth2.models import ManagedGrant

from cbra.types import PersistedModel
from cbra.ext.security import ApplicationKeychain
from .types import CredentialScope
from .types import ICredentialRepository
from .types import SubjectCredentialIdentifier


class SubjectCredential(PersistedModel):
    scope: Literal[CredentialScope.SUBJECT] = pydantic.Field(
        default=CredentialScope.SUBJECT
    )

    id: str = pydantic.Field(
        default_factory=lambda: secrets.token_urlsafe(48),
        primary_key=True
    )

    subject_id: str = pydantic.Field(
        default=...
    )

    resource: DomainName | ResourceName = pydantic.Field(
        default=...
    )

    credential: ManagedGrant = pydantic.Field(
        default=...
    )

    encrypted: bool = pydantic.Field(
        default=False
    )

    __repository__: ICredentialRepository | None = pydantic.PrivateAttr(
        default=None
    )

    def get_primary_key(self) -> SubjectCredentialIdentifier:
        return SubjectCredentialIdentifier(self.id)

    async def decrypt(self, keychain: ApplicationKeychain):
        await self.credential.decrypt(keychain)
        self.encrypted = False

    async def encrypt(self, keychain: ApplicationKeychain):
        await self.credential.encrypt(keychain)
        self.encrypted = True

    async def persist(self) -> None:
        assert self.__repository__ is not None
        await self.__repository__.persist(self)