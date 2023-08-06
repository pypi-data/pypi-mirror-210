# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Awaitable
from typing import Callable

from headless.ext.oauth2 import Client
from headless.ext.oauth2 import RefreshTokenException
from headless.ext.oauth2.models import ManagedGrant
from headless.ext.oauth2.types import ITokenResponse
from headless.types import IRequest

from cbra.types import ServiceNotAvailable
from ..types import IPersistableCredential
from .basecredential import BaseCredential


class OpenAuthorizationAccessToken(BaseCredential):
    __module__: str = 'cbra.ext.credentials.http'
    client: Client
    credential: IPersistableCredential
    expires: datetime | None = None
    grant: ManagedGrant
    resource: str | None = None
    token: str | None = None

    def __init__(
        self,
        client: Client,
        credential: IPersistableCredential,
        *,
        resource: str | None = None,
        token: str | None = None,
        expires: datetime | None = None,
        on_obtained: Callable[[str, str, ITokenResponse], Awaitable[None]] | None = None
    ):
        assert isinstance(credential.credential, ManagedGrant)
        self.client = client
        self.credential = credential
        self.expires = expires
        self.grant = credential.credential
        self.resource = resource
        self.token = token
        self.on_obtained = on_obtained

    async def add_to_request(self, request: IRequest[Any]) -> None:
        now = datetime.now(timezone.utc)
        if self.token is None or (self.expires and self.expires <= now):
            try:
                await self.refresh(now)
            except RefreshTokenException:
                self.logger.critical(
                    "Unable to obtain access token (iss: %s, client: %s)",
                    self.client.get_issuer(), self.client.client_id
                )
                raise ServiceNotAvailable
        assert self.token is not None
        request.add_header('Authorization', f'Bearer {self.token}')

    async def refresh(self, now: datetime) -> None:
        self.logger.info(
            "Refreshing access token (client: %s, sub: %s, email: %s)",
            self.client.client_id, self.grant.sub, self.grant.email
        )
        response = await self.grant.refresh(self.client, resource=self.resource)
        await self.credential.persist()
        assert self.grant.refresh_token == response.refresh_token

        # TODO: This assumes that the authorization server does not lie about
        # the lifetime of the access token. If it does, this might cause an
        # infinite loop.
        self.expires = now + timedelta(seconds=int(response.expires_in * 0.75))
        self.token = str(response.access_token)
        await self._on_obtained(response)

    async def _on_obtained(self, response: ITokenResponse):
        if self.on_obtained is None: return
        if self.resource is None: return
        await self.on_obtained(
            str(self.credential.get_primary_key()),
            self.resource,
            response
        )