# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
from headless.ext.oauth2.models import OIDCToken
from headless.ext.oauth2.models import TokenResponse

from cbra.ext.credentials import CredentialRepository
from cbra.ext.credentials import SubjectCredential
from cbra.ext.credentials import ICredentialRepository
from cbra.types import SessionRequestPrincipal
from cbra.core.conf import settings
from .client import ManagedGrant
from .params import FrontendError
from .params import FrontendTokenResponse
from .tokenhandlerendpoint import TokenHandlerEndpoint


class FrontendRedirectionEndpoint(TokenHandlerEndpoint):
    __module__: str = 'cbra.ext.oauth2'
    credentials: ICredentialRepository = CredentialRepository
    error: Exception | None = FrontendError
    name: str = 'bff.redirection'
    path: str = '/oauth/v2/callback'
    principal: SessionRequestPrincipal # type: ignore
    status_code: int = 303
    redirect_uri: str = fastapi.Cookie(
        default=...,
        title="Redirect URI",
        alias='bff.redirect_uri',
        description=(
            "The URI to redirect the user-agent to after completing the "
            "login."
        )
    )
    summary: str = 'Frontend Redirection Endpoint'
    token: TokenResponse = FrontendTokenResponse

    async def get(self) -> fastapi.Response:
        if self.error:
            raise self.error
        if self.token.refresh_token is None:
            raise NotImplementedError
        if self.token.id_token is None:
            raise NotImplementedError
        assert self.client.client_id is not None
        oidc = oidc = OIDCToken.parse_jwt(self.token.id_token)
        if oidc.email:
            oidc.email_verified = settings.APP_ISSUER_TRUST
        credential = SubjectCredential(
            subject_id=oidc.sub,
            resource=self.request.url.netloc,
            credential=ManagedGrant(
                client_id=self.client.client_id,
                iss=self.client.get_issuer(),
                oidc=oidc,
                refresh_token=self.token.refresh_token,
                scope=set() if not self.token.scope else set(filter(bool, self.token.scope.split(' '))),
                token_endpoint=None
            )
        )

        await self.session
        await self.credentials.persist(credential)
        self.session.authenticate(oidc)
        self.delete_cookies()
        self.set_cookie(
            'grant', credential.id,
            httponly=True,
            secure=True,
            samesite='strict'
        )
        return fastapi.responses.RedirectResponse(
            status_code=303,
            url=self.redirect_uri
        )