from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.list_task_runs_request_status import ListTaskRunsRequestStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ListTaskRunsRequest")


@attr.s(auto_attribs=True)
class ListTaskRunsRequest:
    """ 
        Attributes:
            task_id (str):
            limit (Union[Unset, None, int]):
            status (Union[Unset, None, ListTaskRunsRequestStatus]): The available filters for task run status
                Please see [TaskStatus] for more details.
     """

    task_id: str
    limit: Union[Unset, None, int] = UNSET
    status: Union[Unset, None, ListTaskRunsRequestStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        task_id = self.task_id
        limit = self.limit
        status: Union[Unset, None, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value if self.status else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "task_id": task_id,
        })
        if limit is not UNSET:
            field_dict["limit"] = limit
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        task_id = d.pop("task_id")

        limit = d.pop("limit", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, None, ListTaskRunsRequestStatus]
        if _status is None:
            status = None
        elif isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ListTaskRunsRequestStatus(_status)




        list_task_runs_request = cls(
            task_id=task_id,
            limit=limit,
            status=status,
        )

        list_task_runs_request.additional_properties = d
        return list_task_runs_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
