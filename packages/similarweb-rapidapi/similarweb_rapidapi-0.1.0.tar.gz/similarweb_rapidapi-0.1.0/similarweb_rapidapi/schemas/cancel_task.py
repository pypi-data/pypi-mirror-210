from typing import List
from typing import Optional

from pydantic.fields import Field

from .base import BaseModelORM


class SimilarWebCancelTaskModel(BaseModelORM):
    status: int
    description: str
