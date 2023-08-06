# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import cbra.core as cbra
from .bookpublication import BookPublication


class Book(cbra.ResourceModel):
    id: int | None = cbra.Field(
        default=None,
        read_only=True,
        path_alias='book_id',
        primary_key=True
    )
    title: str
    publications: list[BookPublication]