from typing import List, Optional

from redis_om import Field, HashModel


class TranslationKey(HashModel):
    snake_name: str = Field(index=True)
    id_name: str = Field(index=True)
    uuid: str = Field(index=True)
    views: Optional[str] = Field(
        index=True
    )  # this need to stay optional for now because po translations don't have assigned view
    occurrences: List[str]
    usage_context: Optional[str]
    flags: Optional[str]
    category: int = 0  # default value is 0
    translation: str
    language: str


class Views(HashModel):
    name: str = Field(index=True)
    language: str
    updated_at: int


class Occurrences(HashModel):
    name: str = Field(index=True)
    language: str
    updated_at: int
