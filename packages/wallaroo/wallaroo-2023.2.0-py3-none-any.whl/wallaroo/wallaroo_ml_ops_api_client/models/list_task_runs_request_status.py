from enum import Enum


class ListTaskRunsRequestStatus(str, Enum):
    ALL = "all"
    FAILURE = "failure"
    RUNNING = "running"
    SUCCESS = "success"

    def __str__(self) -> str:
        return str(self.value)
