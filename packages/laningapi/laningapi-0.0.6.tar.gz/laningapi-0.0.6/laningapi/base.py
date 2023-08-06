from os.path import join

import requests
from requests import Response


class Transport:
    def init(self, *args, **kwargs):
        ...

    def post(self, url, json) -> Response:
        ...


class TransportInternal(Transport):
    def init(self):
        pass

    def post(self, url, *, json) -> Response:
        headers = {
            "x-forwarded-for-zl": "127.0.0.1",
            "x-current-user-id": 1,
            "x-current-username": "laningapi"
        }
        return requests.post(url, json=json, headers=headers)


class TransportExternal(Transport):
    def __init__(self):
        self.token = None

        # self.username = None
        # self.password = None
        # self.login_url = None

    def init(self, login_url: str, app_id: str, secret: str):
        payload = {
            "app_id": app_id,
            "secret": secret
        }
        response = requests.post(login_url, json=payload)
        try:
            self.token = response.json()['data']['token']
            # print(f"Login successful.\n{self.token}")
        except Exception:
            if response.status_code == 200:
                raise PermissionError("Error Response({})".format(response.text))
            else:
                raise PermissionError(f"Error Response {response.status_code}")

    def post(self, url, json, retry=1) -> Response:
        if self.token is None:
            raise PermissionError("Without a token. Please init().")
        headers = {
            'X-Token': self.token
        }
        # while retry >= 0:
        #     response = requests.post(url, json=json, headers=headers)
        #     if response.status_code == 200:
        #         return response
        #     elif response.status_code == 403:
        #         self.init(self.login_url, self.username, self.password)
        #
        #     retry -= 1
        #     time.sleep(3)
        response = requests.post(url, json=json, headers=headers)
        return response


class Base:
    def __init__(self, baseurl='http://seriesapi-prod:8000', transport=None):
        self.baseurl = baseurl

        self.transport = transport
        if self.transport is None:
            self.transport = TransportInternal()
            self.transport.init()

    def _get_url(self, path: str):
        url = join(self.baseurl, path)
        return url

    def _do_post(self, path, json, resp_jsonable=True):
        # print(self._get_url(path))
        response = self.transport.post(self._get_url(path), json=json)
        if response.status_code == 200:
            # print(response.content)
            if resp_jsonable:
                try:
                    info = response.json()
                except Exception as e:
                    raise Exception("返回值不是合法的JSON {}".format(response.text))

                if info['code'] == 0:
                    return info['data']
                else:
                    raise Exception("调用失败 {}".format(response.text))
            else:
                return response.text

        else:
            raise Exception("Error Response({})".format(response.status_code))
