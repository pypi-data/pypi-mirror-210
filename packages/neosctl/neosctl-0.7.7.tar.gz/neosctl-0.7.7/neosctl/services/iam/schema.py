from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class EffectEnum(Enum):
    allow = "allow"
    deny = "deny"


class Statement(BaseModel):
    sid: str
    principal: List[str]
    action: List[str]
    resource: List[str]
    condition: Optional[List[str]] = None
    effect: EffectEnum = EffectEnum.allow

    class Config:
        """Pydantic configuration object."""

        use_enum_values = True


class Statements(BaseModel):
    statements: List[Statement]


class Policy(BaseModel):
    version: str = "2022-10-01"
    statements: List[Statement]


class UserPolicy(BaseModel):
    user: str
    policy: Policy
