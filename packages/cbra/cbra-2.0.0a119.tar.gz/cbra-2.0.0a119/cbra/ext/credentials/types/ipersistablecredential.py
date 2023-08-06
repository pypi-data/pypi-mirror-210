# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol
from typing import TypeAlias
from typing import Union

from headless.ext.oauth2.models import ManagedGrant

from cbra.ext.security import ApplicationKeychain
from .globalcredentialidentifier import GlobalCredentialIdentifier
from .subjectcredentialidentifier import SubjectCredentialIdentifier


CredentialIdentifierType: TypeAlias = Union[
    GlobalCredentialIdentifier,
    SubjectCredentialIdentifier
]


class IPersistableCredential(Protocol):
    credential: ManagedGrant

    def get_primary_key(self) -> CredentialIdentifierType: ...
    async def persist(self) -> None: ...
    async def decrypt(self, keychain: ApplicationKeychain): ...
    async def encrypt(self, keychain: ApplicationKeychain): ...