# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse

from .compositeobjectidentifier import CompositeObjectIdentifier
from .iaccesstoken import IAccessToken


class ResourceAccessTokenIdentifier(CompositeObjectIdentifier[IAccessToken]):
    __module__: str = 'cbra.ext.oauth2.types'

    @classmethod
    def parse_url(cls, grant_id: str, service: str):
        p = urllib.parse.urlparse(service)
        return cls(grant_id, p.netloc)

    def __init__(self, grant_id: str, resource: str):
        self.grant_id = grant_id
        self.resource = resource

    def __repr__(self) -> str:
        return f"<ResourceAccessTokenIdentifier('{self.grant_id}', '{self.resource}')>"