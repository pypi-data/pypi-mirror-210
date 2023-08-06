from ._mock import MockType
from .base import Base


class OpLog(Base, metaclass=MockType):
    def __init__(self, baseurl='http://oplogapi-prod:8000', transport=None):
        super().__init__(baseurl, transport)

    def add_oplog(
            self, *,
            event_type: str,
            user_id: int,
            ip: str,
            event_detail: str = "",
            module: str = "",
            target_id: int = None
    ):
        payload = {
            'event_type': event_type,
            'user_id': user_id,
            'ip': ip,
            'event_detail': event_detail,
            'module': module,
            'target_id': target_id
        }

        response = self._do_post('add_oplog', payload)
        return response["id"]

    def add_console(self, *, module: str, category: str = "", description: str = ""):
        payload = {
            'module': module,
            'description': description,
            'category': category
        }

        response = self._do_post('add_console', payload)
        return response["id"]
