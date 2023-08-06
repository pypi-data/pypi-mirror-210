import json.decoder
import httpx


class UsersideCategory:
    def __init__(self, category: str, api: 'UsersideAPI'):
        self._api = api
        self._cat = category

    def __getattr__(self, action: str):
        def method(**kwargs):
            return self._api._request(cat=self._cat,
                                      action=action,
                                      **kwargs)
        return method


class UsersideAPI:
    def __init__(self,
                 url: str,
                 key: str, ):
        self._url = url
        self._key = key
        self._in_use = 0
        self._session = httpx.Client(params={'key': self._key})

    def _request(self, cat: str, action: str, **kwargs):
        params = {'cat': cat, 'action': action}
        params.update(kwargs)
        response = self._session.get(url=self._url, params=params)
        try:
            content = response.json()
        except json.decoder.JSONDecodeError:
            raise RuntimeError('Non-JSON response')
        if not response.status_code == 200:
            raise RuntimeError(content.get('error', 'No error from Userside'))
        elif not response.text:
            raise RuntimeError('Empty response')
        return self._parse_response(content)

    @staticmethod
    def _parse_response(response: dict):
        if (id_ := response.get('id')) is not None:
            return id_
        if (data := response.get('data')) is not None:
            return data
        if (list_ := response.get('list')) is not None:
            return list_.split(',')
        return response

    def __getattr__(self, item):
        return UsersideCategory(item, self)
