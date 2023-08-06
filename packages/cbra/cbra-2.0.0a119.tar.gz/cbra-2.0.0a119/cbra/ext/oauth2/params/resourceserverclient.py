# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import logging
from typing import Any

import fastapi
from headless.ext import oauth2
from headless.types import IClient
from headless.ext.oauth2.models import ManagedGrant
from headless.ext.oauth2.types import IAuthorizationServerClient
from headless.ext.oauth2.types import ITokenResponse

from cbra.core.conf import settings
from cbra.ext.credentials import CredentialRepository
from cbra.ext.credentials import ICredentialRepository
from cbra.ext.credentials.http import OpenAuthorizationAccessToken
from cbra.ext.credentials.types import SubjectCredentialIdentifier
from cbra.types import NotAuthorized
from cbra.types import NotFound
from ..types import IFrontendStorage
from ..types import ResourceServerAccessToken
from ..types import ResourceAccessTokenIdentifier
from .applicationclient import ApplicationClient
from .clientstorage import ClientStorage


logger: logging.Logger = logging.getLogger('cbra.auth')


async def cache_access_token(
    client: IAuthorizationServerClient,
    storage: IFrontendStorage,
    grant_id: str,
    audience: str,
    response: ITokenResponse
):
    access_token_id = ResourceAccessTokenIdentifier.parse_url(grant_id, audience)
    logger.info("Obtained access token (audience: %s)", access_token_id.resource)
    access_token = ResourceServerAccessToken.parse_response(
        grant_id=grant_id,
        issuer=client.get_issuer(),
        resource=access_token_id.resource,
        response=response # type: ignore
    )
    await storage.persist(access_token)


async def get(
    client: oauth2.Client = ApplicationClient,
    credentials: ICredentialRepository = CredentialRepository,
    storage: IFrontendStorage = ClientStorage,
    grant_id: SubjectCredentialIdentifier | None = fastapi.Cookie(
        default=None,
        title="Grant ID",
        alias='bff.grant',
        description=(
            "Identifies the grant that is used to exchange tokens with "
            "the authorization server."
        )
    ),
    resource: str = fastapi.Path(
        default=...
    ),
    path: str = fastapi.Path(
        default=...
    )
):
    path = path or '/'
    spec = settings.OAUTH2_RESOURCE_SERVERS.get(resource)
    if spec is None:
        raise NotFound
    service = spec['resource']
    if grant_id is None:
        logger.warning("Grant not specified (resource: %s)", service)
        raise NotAuthorized(
            headers={'WWW-Authenticate': 'authorization_code'}
        )
    grant = await credentials.get(grant_id)
    if grant is None:
        logger.warning("Grant does not exist (resource: %s).", service)
        raise NotAuthorized(
            headers={'WWW-Authenticate': 'authorization_code'}
        )
    if not isinstance(grant.credential, ManagedGrant):
        logger.critical("Invalid grant configured (id: %s)", grant_id)
        raise NotAuthorized(
            headers={'WWW-Authenticate': 'authorization_code'}
        )
    
    # Check if there is a cached access token for this resource
    # and grant.
    access_token_id = ResourceAccessTokenIdentifier.parse_url(
        grant_id=str(grant.get_primary_key()),
        service=service
    )
    cached = await storage.get(access_token_id)
    expires = token = None
    if cached is not None and not cached.is_expired():
        logger.debug("Using cached acccess token (service: %s)", service)
        expires = cached.expires
        token = cached.access_token
    assert isinstance(grant.credential, ManagedGrant)
    credential = OpenAuthorizationAccessToken(
        client=client,
        credential=grant,
        resource=service,
        token=token,
        expires=expires,
        on_obtained=functools.partial(cache_access_token, client, storage)
    )

    async with oauth2.ResourceServer(base_url=service, credential=credential) as resource_client:
        yield resource_client


RequestedResourceServerClient: IClient[Any, Any] = fastapi.Depends(get)

