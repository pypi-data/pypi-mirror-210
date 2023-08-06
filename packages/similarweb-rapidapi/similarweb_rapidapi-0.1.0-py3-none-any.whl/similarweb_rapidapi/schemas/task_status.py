from enum import Enum


class TaskStatus(Enum):
    PENDING = 'pending',
    INPROGRESS = 'inprogress',
    SUCCEEDED = 'succeeded',
    FAILED = 'failed',
    CANCELLED = 'cancelled',
    NOTFINISHED = 'notfinished',
    ALL = 'all'
    
    def __str__(self):
        return self.name.lower()