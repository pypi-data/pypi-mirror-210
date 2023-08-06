# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

import pydantic

from headless.types import IClient
from headless.types import IResource
from headless.types import IResponse
from .resourcemeta import ResourceMeta
from .resourcemetaclass import ResourceMetaclass


T = TypeVar('T', bound='Resource')
Request = TypeVar('Request')
Response = TypeVar('Response')


class Resource(IResource, metaclass=ResourceMetaclass):
    """The base class for all resource implementations."""
    __abstract__: bool = True
    _client: IClient[Any, Any] = pydantic.PrivateAttr()
    _meta: ResourceMeta = pydantic.PrivateAttr()

    @classmethod
    def get_create_url(cls, *params: Any) -> str:
        return cls._meta.get_create_url()

    @classmethod
    def get_list_url(cls, *params: Any) -> str:
        return cls._meta.get_list_url()

    @classmethod
    def get_retrieve_url(cls: type[T], resource_id: int | str | None) -> str:
        return cls._meta.get_retrieve_url(resource_id)

    @classmethod
    def get_next_url(
        cls,
        response: IResponse[Any, Any],
        n: int
    ) -> str | None:
        """Return the next URL when paginating, or ``None`` if there is
        no next URL.
        """
        raise NotImplementedError

    @classmethod
    def process_response(cls, action: str | None, data: dict[str, Any]) -> dict[str, Any]:
        """Process response data prior to parsing using the declared model."""
        return data

    @classmethod
    def parse_resource(cls: type[T], obj: Any) -> T:
        return cls.parse_obj(obj)

    @classmethod
    async def create(cls: type[T], client: IClient[Any, Any], params: Any) -> T:
        return await client.create(cls, params=params)

    async def delete(self) -> None:
        await self._client.destroy(type(self), instance=self)

    async def persist(
        self,
        client: IClient[Any, Any] | None = None,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ):
        client = getattr(self, '_client', None) or client
        if not client:
            raise TypeError("The 'client' parameter can not be None")
        await client.persist(
            model=type(self),
            instance=self,
            exclude=exclude,
            include=include
        )
        self._client = client

    def get_delete_url(self) -> str:
        return self.get_persist_url()

    def __await__(self):
        async def f(): return self
        return f().__await__()