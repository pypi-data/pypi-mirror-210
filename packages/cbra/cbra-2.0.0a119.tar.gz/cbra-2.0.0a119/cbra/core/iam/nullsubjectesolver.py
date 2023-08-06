# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.types import IRequestPrincipal
from cbra.types import ISubject
from cbra.types import ISubjectResolver
from cbra.types import NullSubject


class NullSubjectResolver(ISubjectResolver):
    __module__: str = 'cbra.core.iam'

    async def resolve(self, principal: IRequestPrincipal) -> ISubject:
        return NullSubject()