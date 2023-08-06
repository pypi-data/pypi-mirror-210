from typing import List
from typing import Optional

from pydantic.fields import Field

from .base import BaseModelORM

class Data(BaseModelORM):
    task_id: str
    task_status: str
    task_utc_created_at: str
    task_utc_finished_at: Optional[str]
    task_callback_url: Optional[str]
    task_callback_utc_sent_at: Optional[str]
    task_callback_status: Optional[str]
    task_result: Optional[str]

class SimilarWebMyTasksModel(BaseModelORM):
    status: int
    description: str
    data: List[Data]
