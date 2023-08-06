# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Callable
from typing import Generator
from typing import TypeVar

from pydantic.validators import str_validator

from .claimset import ClaimSet
from .oidctoken import OIDCToken


T = TypeVar('T', bound='EncodedIDToken')


class EncodedIDToken(str):
    __module__: str = 'cbra.ext.oauth2.models'

    @classmethod
    def __get_validators__(cls: type[T]) -> Generator[Callable[..., str | T], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls: type[T], v: str) -> T:
        return cls(v)

    def parse(self) -> OIDCToken:
        return OIDCToken.parse_jwt(self, {'application/jwt', 'jwt'})
    
    def claims(self) -> ClaimSet:
        return ClaimSet.parse_jwt(self, {'application/jwt', 'jwt'})

    def __repr__(self) -> str:
        return f'<EncodedOIDCToken>'