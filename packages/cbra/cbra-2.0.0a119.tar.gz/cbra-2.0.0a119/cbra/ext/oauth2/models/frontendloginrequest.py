# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic


class FrontendLoginRequest(pydantic.BaseModel):
    prompt: Literal["select_account"] | None = None
    redirect_uri: str
    ui_locales: list[str]
    scope: set[str] = set()