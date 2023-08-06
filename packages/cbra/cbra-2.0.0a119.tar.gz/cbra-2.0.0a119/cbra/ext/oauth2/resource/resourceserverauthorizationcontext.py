# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast

from cbra.types import IAuthorizationContext
from cbra.types import ISubject
from cbra.types import Request
from cbra.types import PolicyPrincipal
from ..types import RFC9068AccessToken
from .types import UserInfoSubject


class ResourceServerAuthorizationContext(IAuthorizationContext):
    __module__: str = 'cbra.ext.oauth2.resource'
    _request: Request
    _subject: UserInfoSubject
    _token: RFC9068AccessToken

    def __init__(
        self,
        request: Request,
        token: RFC9068AccessToken,
        subject: ISubject
    ):
        self._request = request
        self._subject = cast(UserInfoSubject, subject)
        self._token = token

    def get_principals(self) -> set[PolicyPrincipal]:
        principals: set[PolicyPrincipal] = set()
        if self.subject.email is not None:
            principals.add(PolicyPrincipal.email(self.subject.email))

        # Only add the client_id as a principal if it is the same
        # as the subject.
        if self._token.client_id == self._token.sub:
            principals.add(PolicyPrincipal.client(self._token.iss, self._token.client_id))

        return principals

    def get_subject(self) -> ISubject:
        return self._subject