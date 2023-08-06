from ._mock import MockType
from .base import Base


class Series(Base, metaclass=MockType):
    def submit(self, *, bucket_name: str, realpath: str, filename: str):
        data = {
            'bucket_name': bucket_name,
            'realpath': realpath,
            'filename': filename,
        }

        return self._do_post('program_video/submit', data).get('id', -1)

    def submit_by_huashu(self, *, id: str, source: str, bucket_name: str, realpath: str, filename: str):
        data = {
            'id': id,
            'source': source,
            'bucket_name': bucket_name,
            'realpath': realpath,
            'filename': filename,
        }

        return self._do_post('program_video/huashu/submit', data).get('id', -1)

    def add_urls(self, program_id: int, urls):
        data = {
            'program_id': program_id,
            'urls': ["{}||{}".format(item['url'], item['title']) for item in urls],
        }

        return self._do_post('program_video/add_urls', data).get('result', None)

    def submit_by_copy(self, *, program_id: str, realpath: str, filename: str):
        data = {
            'program_id': program_id,
            'realpath': realpath,
            'filename': filename,
        }

        return self._do_post('program_video/submit_by_copy', data).get('id', -1)
