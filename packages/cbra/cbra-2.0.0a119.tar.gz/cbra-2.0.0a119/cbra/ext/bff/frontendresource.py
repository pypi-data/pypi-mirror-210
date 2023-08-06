# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.core import Resource

from .frontendauthenticationcontextfactory import FrontendAuthorizationContextFactory


class FrontendResource(Resource, model=None):
    __abstract__: bool = True
    __module__: str = 'cbra.ext.bff'
    autodiscover: bool = False
    context_factory: FrontendAuthorizationContextFactory
    require_authentication: bool = True