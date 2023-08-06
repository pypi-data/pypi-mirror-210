from typing import List
from typing import Optional

from pydantic.fields import Field

from .base import BaseModelORM

class Data(BaseModelORM):
    task_id: str

class SimilarWebCompleteDataTaskModel(BaseModelORM):
    status: int
    description: str
    data: Data
