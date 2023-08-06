from ._mock import MockType
from .base import Base


class Dictionary(Base, metaclass=MockType):
    def __init__(self, baseurl='http://dictionary-prod:8000', transport=None):
        super().__init__(baseurl, transport)

    def get_dict_info(self, *, name: str, is_active: bool = True) -> dict:
        data = {
            'name': name,
            'is_active': is_active,
        }
        info = self._do_post('get_dict_info', data)
        result = {}
        for row in info["result_list"]:
            result[row["option_key"]] = row["option_value"]

        return result

    # def get_dict_by_ids(self, *, ids: list):
    #     data = {'ids': ids}
    #     info = self._do_post('/get_dict_by_ids', data)
    #     return info["result_list"]
    #
    # def get_option_by_ids(self, *, ids: list):
    #     data = {'ids': ids}
    #     info = self._do_post('/get_option_by_ids', data)
    #     return info["result_list"]

    def new_id(self, *, name: str, namespace: str):
        data = {
            'name': name,
            'namespace': namespace,
        }

        value_id = self._do_post('new_id', data, resp_jsonable=False)
        return value_id
